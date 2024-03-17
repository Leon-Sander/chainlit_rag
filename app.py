from llm_loading import  get_openai_embeddings, get_vector_db, get_pdf_chat_runnable, create_chat_memory
from langchain.schema.runnable.config import RunnableConfig
from pdf_handling import process_file
from chainlit.types import ThreadDict
from typing import Dict, Optional
from dotenv import load_dotenv
import chainlit as cl
load_dotenv()


def setup_vector_db():
    embeddings = get_openai_embeddings()
    vector_db = get_vector_db(embeddings, "pdfs")
    cl.user_session.set("vector_db", vector_db)

def setup_pdf_runnable():
    vector_db = cl.user_session.get("vector_db")
    memory = cl.user_session.get("memory")
    pdf_chain = get_pdf_chat_runnable(vector_db, memory)
    cl.user_session.set("pdf_chain", pdf_chain)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("memory", create_chat_memory())
    setup_vector_db()
    setup_pdf_runnable()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    memory = create_chat_memory()
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "USER_MESSAGE":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    cl.user_session.set("memory", memory)
    setup_vector_db()
    setup_pdf_runnable()

async def add_docs(file):
    docs = await process_file(file)
    vector_db = cl.user_session.get("vector_db")
    await vector_db.aadd_documents(docs)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("pdf_chain")

    res = cl.Message(content="")
    if message.elements != []:
        for file in message.elements:
            await add_docs(file)
        res_doc = cl.Message(content="Documents added")
        await res_doc.send()
    
    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await res.stream_token(chunk["answer"])

@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return default_user