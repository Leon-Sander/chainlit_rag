#from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
import os
#def create_embeddings(embeddings_path):
#    return HuggingFaceInstructEmbeddings(model_name=embeddings_path)

def get_openai_embeddings(embedding_model = "text-embedding-3-small"):
    return OpenAIEmbeddings(model=embedding_model)

def get_openai_llm(temperature = 0.2, streaming = True):
    return ChatOpenAI(temperature=temperature, streaming=streaming)

def get_vector_db(embeddings, collection_name):
    client = QdrantClient("qdrant", port=6333)
    async_client = AsyncQdrantClient("qdrant", port=6333)
    qdrant = Qdrant(client=client, async_client=async_client, collection_name=collection_name, embeddings=embeddings)
    return qdrant

def create_db_collection(collection_name):
    client = QdrantClient("qdrant", port=6333)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    print("Collection created")

def create_chat_memory():
    return ConversationBufferWindowMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True,
        k=4,
    )

def get_pdf_chat_runnable(vector_db, memory):
    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2, streaming=True),
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k":2}),
        memory=memory,
        return_source_documents=False,
        )
    return chain

if __name__ == "__main__":
    if not os.path.isdir("./qdrant_storage/collections/pdfs"):
        create_db_collection("pdfs")
    else:
        print("Collection already exists")