import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

async def process_file(file):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    loader = None
    if file.mime == "text/plain":
        loader = TextLoader(file.path)
    elif file.mime == "application/pdf":
        loader = PyPDFLoader(file.path)
    else:
        raise ValueError(f"Unsupported MIME type: {file.mime}")
    
    if loader is None:
        raise ValueError("Loader not initialized")

    documents = await asyncio.to_thread(loader.load)

    docs = text_splitter.split_documents(documents)
    return docs