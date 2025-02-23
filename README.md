# Python Langchain Chainlit Qdrant Ollama Stack Template

![python](https://img.shields.io/badge/python-3.11.6-informational)
<a href="https://github.com/new?template_name=python-langchain-chainlit-qdrant-ollama-stack-template&template_owner=kwame-mintah">
<img src="https://img.shields.io/badge/use%20this-template-blue?logo=github">
</a>

This a template project, to demonstrate using docker compose to create a Retrieval-Augmented Generation (RAG) application
using Langchain, chainlit, qdrant and ollama on a specified knowledge base.

## Prerequisites

1. [Python 3.11.6](https://www.python.org/downloads/release/python-3116/)
2. [Langchain](https://python.langchain.com/docs/introduction/)
3. [Chainlit](https://docs.chainlit.io/get-started/overview)
4. [Qdrant](https://qdrant.tech/documentation/quickstart/)
5. [Ollama](https://ollama.com/download)
6. [Docker for desktop](https://docs.docker.com/desktop/)

# Usage

1. Install python packages used for the project

```pycon
pip install -r requirements.txt
```

2. Start [Qdrant](https://qdrant.tech/documentation/quickstart/) vector search database via docker

```shell
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```

3. Start [Ollama](https://ollama.readthedocs.io/en/quickstart/) and download large language models needed, waiting for the download to complete

```shell
ollama run deepseek-r1:1.5b
```

4. Ingest data into the Qdrant database

```pycon
python utils/ingest.py
```

5. Confirm Qdrant collection has been created with data ingested via the Web UI @ http://localhost:6333/dashboard

6. Start Chainlit application

```pycon
chainlit run main.py
```

## Environment variables

The following environment variables are used by this project.

| Environment Variable        | Description                           | Default Value                          |
|-----------------------------|---------------------------------------|----------------------------------------|
| QDRANT_DATABASE_URL         | The Qdrant Database URL               | http://localhost:6333                  |
| QDRANT_COLLECTION_NAME      | The name of the Qdrant collection     | template                               |
| OLLAMA_URL                  | The Ollama host URL                   | http://localhost:11434                 |
| OLLAMA_LLM_MODEL            | The Ollama model to use               | deepseek-r1:1.5b                       |
| DATA_INGESTION_LOCATION     | The file path for data to be ingested |                                        |
| HUGGING_FACE_EMBED_MODEL_ID | The Hugging Face embeddings name      | sentence-transformers/all-MiniLM-L6-v2 |

# Running via Docker Compose

An alternative way of running the stack involves using [docker compose](https://docs.docker.com/compose/), the [`docker-compose.yaml`](docker-compose.yaml)
contains the services needed to run this project, such as starting chainlit, qdrant and ollama.

1. In the root directory start all the services.

```shell
docker compose up -d
```

2. Access the services on the following endpoint in your browser. chainlit (http://localhost:8000/) and qdrant (http://localhost:6333/dashboard)
3. An _optional_ step to run is enabling GPU usage via docker compose, you will need to uncomment out the following lines
   in the yaml found under the Ollama service, providing better performance with large language models (LLM) models.

```yaml
...
#  Enable GPU support using host machine
#  https://docs.docker.com/compose/how-tos/gpu-support/
 deploy:
   resources:
     reservations:
       devices:
         - driver: nvidia
           count: all
           capabilities: [ gpu ]
```

# References

[100% Local RAG Using LangChain, DeepSeek, Ollama, Qdrant, Docling, Huggingface & Chainlit](https://www.youtube.com/watch?v=MCHOam13JSk) by [Data Science Basics](https://www.youtube.com/@datasciencebasics)
