import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import Depends, FastAPI,HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from neuromind.config import Config, Persona
from neuromind.thread_manager import Thread, ThreadManager

# from langchain_ollama import ChatOllama
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# from schema import StreamChunk
logger = logging.getLogger(__name__)

load_dotenv()


class ThreadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    persona: Persona = Persona.NEUROMIND


class ThreadListItem(BaseModel):
    name: str
    persona: str
    message_count: int


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    role: str
    content: str


class PersonaResponse(BaseModel):
    name: str
    description: str

# def _pack_message(content: str, is_last: bool = False) -> str:
#     chunk = StreamChunk(content=content, is_last=is_last)
#     return f"data: {chunk.model_dump_json()}\n\n"

def get_db() -> ThreadManager:
    return ThreadManager(Config.Path.DATABASE_FILE)


def get_llm():
    """Initialize and return the LangChain chat model."""
    # TODO: Initialize the chat model using Config.MODEL settings.
    print("Initialize Chat Model")
    # llm = ChatOllama(model=Config.MODEL.name,
    #                  temperature=Config.MODEL.temperature,
    #                  reasoning=Config.MODEL.reasoning)

    llm = init_chat_model(Config.MODEL.name, model_provider="ollama")
    return llm


def get_personas() -> dict[str, str]:
    """Load all persona system prompts from disk."""
    return {
        p.value: (Config.Path.PERSONAS_DIR / f"{p.value}.md").read_text()
        for p in Persona
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.personas = get_personas()
    yield


app = FastAPI(
    title="NeuroMind API",
    description="AI Assistant REST API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/personas", response_model=list[PersonaResponse])
def list_personas():
    """List all available personas."""
    return [
        PersonaResponse(name=p.value, description=f"{p.value.title()} persona")
        for p in Persona
    ]


@app.get("/threads", response_model=list[ThreadListItem])
def list_threads(db: ThreadManager = Depends(get_db)):
    """List all conversation threads."""
    # TODO: Return all threads as ThreadListItem objects.
    # import pdb; pdb.set_trace()
    # print("SERVER --> List threads")
    # import pdb; pdb.set_trace()
    threads_=db.list_threads()
    t1 =[]
    for thread_ in threads_:
        t1.append(ThreadListItem(name=thread_[0],persona=thread_[1],message_count=thread_[2]))
    return t1

@app.post("/threads", response_model=Thread, status_code=201)
def create_thread(data: ThreadCreate, db: ThreadManager = Depends(get_db)):
    """Create a new conversation thread."""
    # TODO: Create the thread and return it.
    return db.get_or_create_thread(data.name, data.persona)


@app.get("/threads/{thread_name}", response_model=Thread)
def get_thread_endpoint(thread_name: str, db: ThreadManager = Depends(get_db)):
    """Get a thread by name."""
    # TODO: Return the thread or 404 if not found.
    thread_=db.get_thread(thread_name)
    if thread_ is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread_


@app.get("/threads/{thread_name}/messages", response_model=list[MessageResponse])
def get_messages(thread_name: str, db: ThreadManager = Depends(get_db)):
    """Get message history for a thread."""
    # TODO: Return messages as MessageResponse objects, or 404 if thread not found.
    thread_=db.get_thread(thread_name)
    history_=db.get_history(thread_.id)
    if history_ is None:
        raise HTTPException(status_code=404, detail="No history found")
    return history_


@app.delete("/threads/{thread_name}/messages", status_code=204)
def clear_messages(thread_name: str, db: ThreadManager = Depends(get_db)):
    """Clear all messages in a thread."""
    # TODO: Clear messages for the thread, or 404 if not found.
    thread_ = db.get_thread(thread_name)
    if thread_ is None:
        raise HTTPException(status_code=404, detail="No thread found")
    else:
        db.clear_messages(thread_.id)
    # if history_ is None:
    #     raise HTTPException(status_code=404, detail="No history found")
    # return history_


def _build_context(thread: Thread, user_input: str, personas: dict, db: ThreadManager):
    """Build the full message context for LLM invocation."""
    # TODO: Combine system prompt, history, and user input into a message list.
    message_=[]
    message_.append(personas[thread.persona])
    history_=db.get_history(thread.id)
    if history_ is not None:
        message_.append(history_)
    if user_input is not None:
        message_.append(user_input.content)
    return message_


@app.post("/threads/{thread_name}/chat")
async def chat(
    thread_name: str,
    data: MessageCreate,
    db: ThreadManager = Depends(get_db),
    llm=Depends(get_llm),
    ):
    # await generate(thread_name, data, db, llm)
    return StreamingResponse(
        generate(thread_name,data, db, llm),
        media_type="text/event-stream",
    )





    """Send a message and stream the AI response via Server-Sent Events."""
    # TODO: Get or create the thread and build context.

    # import pdb; pdb.set_trace()
    # db.add_message(thread_.id, thread_.persona, "ev batter price can be an issue")
async def generate(thread_name,data,db,llm) -> AsyncGenerator[str, None]:
    """Stream LLM response as SSE events."""
    #
    full_content = ""



    # TODO: Stream from the LLM and yield SSE events.
    # Event types: "reasoning", "content", "done", "error"
    # Format: data: {"type": "<type>", "content": "<content>"}\n\n
    # Save messages to database after successful completion.
    # Handle errors gracefully without crashing.
    full_response = ""
        # ---------------------------------------------------------------------
        # EXAMPLES
        # ---------------------------------------------------------------------
        # INVOKE: Synchronous Call
        # r1=llm.invoke(conversations[thread_.name])

        # AINVOKE: Asynchronous Call
        # r1= await llm.ainvoke(conversations[thread_.name])

        # STREAM: Streaming Response (Sync)
        # for chunk in llm.stream(conversations[thread_.name]):
        #     print(chunk.content, end="")
        # for chunk in llm.stream("What is the future of EVs"):
        #     print(chunk.content, end="")

        # ASTREAM: Asynchronous Streaming
        # async for chunk in llm.astream(conversations[thread_.name]):
        #     print(chunk.content, end="")
        # async for chunk in llm.astream("What is the future of EVs"):
        #     print(chunk.content, end="")
        # ---------------------------------------------------------------------
    conversations = {}
    thread_ = db.get_thread(thread_name)
    personas_ = get_personas()
    # context_ = _build_context(thread_, data, personas_, db)

    SYSTEM_PROMPT = SystemMessage(personas_[thread_.persona])
    USER_INPUT = HumanMessage(data.content)

    conversations[thread_.name] = [SYSTEM_PROMPT]
    conversations[thread_.name].append(USER_INPUT)

    async for chunk in llm.astream(conversations[thread_.name]):
    # async for chunk in llm.astream("What is the future of EVs"):
        if chunk.content:
            print(chunk.content, end="")
            full_response += chunk.content
                # yield _pack_message(chunk.content)

        # r1 = await llm.ainvoke(conversations[thread_.name])
        # print(r1)
        # conversations[thread_.name].append(AIMessage(full_response))
        # yield _pack_message("", is_last=True)
    db.add_message(thread_.id, thread_.persona, full_response)
    yield full_response

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "model": Config.MODEL.name}
