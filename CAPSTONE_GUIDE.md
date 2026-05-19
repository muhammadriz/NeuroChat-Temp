# NeuroMind Capstone Project

> **Your Mission:** Build a production-ready AI assistant with persistent memory, streaming responses, and multiple personas.

Welcome to the NeuroMind Capstone. You have been given the **scaffold** of a fully functional AI assistant. The architecture is complete—your job is to implement the core business logic that makes it work.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                                                                             │
│   ┌─────────────┐         ┌──────────────┐                                  │
│   │   app.py    │────────▶│  UIManager   │  Terminal rendering (Rich)      │
│   │  (CLI App)  │         │              │  Markdown, streaming, prompts   │
│   └──────┬──────┘         └──────────────┘                                  │
│          │                                                                  │
└──────────┼──────────────────────────────────────────────────────────────────┘
           │
           │ HTTP/SSE
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│                                                                             │
│   ┌─────────────────┐                                                       │
│   │ NeuroMindClient │  HTTP client (httpx)                                  │
│   │   client.py     │  Handles REST calls + SSE streaming                   │
│   └────────┬────────┘                                                       │
│            │                                                                │
│            │ REST API                                                       │
│            ▼                                                                │
│   ┌─────────────────┐                                                       │
│   │  FastAPI Server │  server.py                                            │
│   │   /threads      │  Endpoints, SSE streaming, LLM orchestration          │
│   │   /chat         │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                │
└────────────┼────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PERSISTENCE LAYER                                  │
│                                                                             │
│   ┌──────────────┐         ┌──────────────┐                                 │
│   │ ThreadManager│────────▶│   SQLite     │  SQLModel ORM                   │
│   │              │         │  neuromind.db│  Thread + Message tables        │
│   └──────────────┘         └──────────────┘                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            INFERENCE LAYER                                   │
│                                                                             │
│   ┌─────────────┐         ┌──────────────┐                                  │
│   │  LangChain  │────────▶│ Ollama/Gemini│  Model inference                 │
│   │  init_model │         │   qwen3:8b   │  Streaming + Reasoning           │
│   └─────────────┘         └──────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Interface** | Rich | Terminal UI, Markdown rendering, streaming display |
| **HTTP Client** | httpx | Synchronous HTTP with streaming support |
| **API Framework** | FastAPI | REST API with SSE streaming responses |
| **ORM** | SQLModel | Type-safe database operations |
| **AI Orchestration** | LangChain | Model abstraction, streaming, reasoning chains |
| **Inference** | Ollama / Google GenAI | Local or cloud LLM inference |

---

## 2. The Setup

### Prerequisites

- **Python 3.13+**
- **uv** package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Ollama** installed and running ([ollama.ai](https://ollama.ai))

### Installation

```bash
# 1. Clone the scaffold repository
git clone <your-scaffold-repo-url>
cd neuromind-starter

# 2. Install dependencies
uv sync

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Verify environment and pull the model
python setup_check.py
```

### Running the Application

You need **two terminals**:

```bash
# Terminal 1: Start the API server
python start_server.py

# Terminal 2: Launch the CLI
python app.py
```

### Validation Checkpoints

After implementing each ticket, verify your work:

| Checkpoint | Command | Expected Result |
|------------|---------|-----------------|
| Server starts | `python start_server.py` | No errors, "Uvicorn running on 0.0.0.0:8000" |
| Health check | `curl localhost:8000/health` | `{"status": "ok", "model": "qwen3:8b"}` |
| CLI connects | `python app.py` | Header displays, prompt appears |
| Chat works | Type a message | Streaming response with reasoning panel |

---

## 3. Engineering Tickets

### Ticket 1: The Memory Layer

**File:** `neuromind/thread_manager.py`

**Objective:** Implement persistent storage for conversation threads and messages.

**Requirements:**
- CRUD operations for threads and messages
- Message history retrieval as LangChain message types
- Thread listing with message counts

**Constraints:**
- Use SQLModel's `Session` context manager
- `get_history()` returns `List[BaseMessage]`

---

### Ticket 2: The AI Server

**File:** `neuromind/server.py`

**Objective:** Build the FastAPI backend with LLM orchestration and SSE streaming.

**Requirements:**
- Initialize LangChain chat model from config
- Build conversation context (system prompt + history + user input)
- Stream responses as SSE events
- Persist messages after completion

**Constraints:**
- SSE format: `data: {"type": "<type>", "content": "<content>"}\n\n`
- Event types: `reasoning`, `content`, `done`, `error`
- Reasoning content is in `chunk.additional_kwargs["reasoning_content"]`

---

### Ticket 3: The API Client

**File:** `neuromind/client.py`

**Objective:** HTTP client with REST calls and SSE streaming support.

**Requirements:**
- Thread management endpoints (CRUD)
- SSE parser yielding `StreamEvent` objects
- Graceful error handling

**Constraints:**
- Use `httpx` for HTTP operations
- `stream_chat()` must be a generator
- Stream errors yield events; non-stream errors raise `APIError`

---

### Ticket 4: The Application Shell

**File:** `app.py`

**Objective:** CLI application loop with command handling and live streaming display.

**Requirements:**
- Command dispatcher (`/new`, `/switch`, `/list`, `/clear`, `/exit`)
- Stream processor with live UI updates
- Persona selection for new threads

**Constraints:**
- Use `UIManager` for all output
- `KeyboardInterrupt` should not exit the app

---

## 4. Technical Hints

These hints address specific implementation challenges. Try to solve them yourself first!

<details>
<summary><strong>Hint 1: SSE Line Parsing</strong></summary>

Server-Sent Events (SSE) have a specific format. Each event line starts with `data:` followed by the JSON payload. When parsing:

```python
# The line looks like: "data: {"type": "content", "content": "Hello"}"
# You need to:
# 1. Check if the line starts with "data:"
# 2. Strip the prefix (first 5 characters)
# 3. Parse the remaining string as JSON

if line.startswith("data:"):
    payload = line[5:].strip()  # Remove "data:" prefix
    event_data = json.loads(payload)
```

Empty lines between events are normal—skip them.

</details>

<details>
<summary><strong>Hint 2: LangChain Streaming with Reasoning Models</strong></summary>

When using reasoning models (like Qwen 3 or Gemini with thinking), the reasoning tokens are NOT in `chunk.content`. They're in a special field:

```python
async for chunk in llm.astream(messages):
    # Regular content
    if chunk.content:
        yield content_event(chunk.content)
    
    # Reasoning/thinking content - check additional_kwargs
    reasoning = chunk.additional_kwargs.get("reasoning_content")
    if reasoning:
        yield reasoning_event(reasoning)
```

The `init_chat_model()` function needs `reasoning=True` to enable this.

</details>

<details>
<summary><strong>Hint 3: SQLModel Session Patterns</strong></summary>

SQLModel objects become "detached" after the session closes. If you return an object and try to access its attributes outside the session, you'll get an error.

**Problem Pattern:**
```python
def get_thread(self, name: str):
    with Session(self.engine) as session:
        thread = session.exec(select(Thread).where(Thread.name == name)).first()
    return thread  # ❌ Detached - accessing .name later may fail
```

**Solution:** SQLModel handles this correctly for simple models returned directly from the session—just make sure you access all needed attributes while still in the session, or return the object directly (SQLModel's `table=True` models work fine when returned immediately).

For the `list_threads()` query with aggregation, you'll need to join the `Thread` and `Message` tables and use `func.count()`:

```python
select(Thread.name, Thread.persona, func.count(Message.id))
    .outerjoin(Message, Thread.id == Message.thread_id)
    .group_by(Thread.id)
```

</details>

---

## 5. Deliverables Checklist

Before submitting, verify:

- [ ] `python start_server.py` runs without errors
- [ ] `curl localhost:8000/health` returns status OK
- [ ] `python app.py` connects and displays the header
- [ ] Creating a new thread with `/new` works
- [ ] Sending a message returns a streaming response
- [ ] Reasoning panel displays (if using a reasoning model)
- [ ] `/list` shows threads with message counts
- [ ] `/clear` wipes the current thread's history
- [ ] `/switch` changes the active thread
- [ ] Conversation history persists across restarts

---

## 6. Stretch Goals (Optional)

If you complete the core tickets early:

1. **Add a `/persona` command** that changes the persona of the current thread
2. **Implement token counting** to warn when approaching the context window limit
3. **Add `/export` command** that saves the current thread to a Markdown file
4. **Implement retry logic** in the client for transient failures

---

Good luck, Engineer. Build something you're proud of. 🧠

