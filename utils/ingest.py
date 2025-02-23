from docling.chunking import HybridChunker
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from config import EnvironmentVariables

EXPORT_TYPE = ExportType.DOC_CHUNKS


def docling_document_ingestion_into_qdrant_database() -> None:
    """
    Docling parses PDF, DOCX, PPTX, HTML, and other formats into a rich unified representation including document
    layout, tables etc., making them ready for generative AI workflows like RAG.
    https://python.langchain.com/docs/integrations/document_loaders/docling/
    https://ds4sd.github.io/docling/examples/rag_langchain/#document-loading
    :return:
    """
    loader = DoclingLoader(
        file_path=str(EnvironmentVariables().DATA_INGESTION_LOCATION),
        export_type=EXPORT_TYPE,
        chunker=HybridChunker(
            tokenizer=EnvironmentVariables().HUGGING_FACE_EMBED_MODEL_ID
        ),
    )
    docling_documents = loader.load()

    # Determining the splits
    if EXPORT_TYPE == ExportType.DOC_CHUNKS:
        splits = docling_documents
    elif EXPORT_TYPE == ExportType.MARKDOWN:
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header_1"),
                ("##", "Header_2"),
                ("###", "Header_3"),
            ],
        )
        splits = [
            split
            for doc in docling_documents
            for split in splitter.split_text(doc.page_content)
        ]
    else:
        raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")

    # Initialize Embeddings
    embedding = HuggingFaceEmbeddings(
        model_name=EnvironmentVariables().HUGGING_FACE_EMBED_MODEL_ID
    )

    # Create and persist a Qdrant vector database from the chunked documents
    QdrantVectorStore.from_documents(
        documents=splits,
        embedding=embedding,
        url=str(EnvironmentVariables().QDRANT_DATABASE_URL),
        collection_name=EnvironmentVariables().QDRANT_COLLECTION_NAME,
    )


if __name__ == "__main__":
    docling_document_ingestion_into_qdrant_database()
