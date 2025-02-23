import chainlit as cl
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableConfig
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_qdrant import QdrantVectorStore

from config import EnvironmentVariables


@cl.on_chat_start
async def on_chat_start():
    template = """Answer the question based only on the following context:

    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    embedding = HuggingFaceEmbeddings(
        model_name=EnvironmentVariables().HUGGING_FACE_EMBED_MODEL_ID
    )

    vectorstore = QdrantVectorStore.from_existing_collection(
        embedding=embedding,
        collection_name=EnvironmentVariables().QDRANT_COLLECTION_NAME,
        url=str(EnvironmentVariables().QDRANT_DATABASE_URL),
    )

    retriever = vectorstore.as_retriever()

    runnable = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | OllamaLLM(
            base_url=str(EnvironmentVariables().OLLAMA_URL),
            model=EnvironmentVariables().OLLAMA_LLM_MODEL,
        )
        | StrOutputParser()
    )

    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable
    msg = cl.Message(content="")

    class PostMessageHandler(BaseCallbackHandler):
        """
        Callback handler for handling the retriever and LLM processes.
        Used to post the sources of the retrieved documents as a Chainlit element.
        """

        def __init__(self, msg: cl.Message):
            BaseCallbackHandler.__init__(self)
            self.msg = msg
            self.sources = set()  # To store unique pairs

        def on_retriever_end(self, documents, *, run_id, parent_run_id, **kwargs):
            for d in documents:
                source_page_pair = (d.metadata["source"], d.metadata["page"])
                self.sources.add(source_page_pair)  # Add unique pairs to the set

        def on_llm_end(self, response, *, run_id, parent_run_id, **kwargs):
            if len(self.sources):
                sources_text = "\n".join(
                    [f"{source}#page={page}" for source, page in self.sources]
                )
                self.msg.elements.append(
                    cl.Text(name="Sources", content=sources_text, display="inline")
                )

    async for chunk in runnable.astream(
        message.content,
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler(), PostMessageHandler(msg)]
        ),
    ):
        await msg.stream_token(chunk)

    await msg.send()
