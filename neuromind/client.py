from dataclasses import dataclass
from enum import Enum
from typing import Generator, List, Tuple

from neuromind.config import Persona

import httpx
import json
import asyncio
class StreamEventType(str, Enum):
    REASONING = "reasoning"
    CONTENT = "content"
    DONE = "done"
    ERROR = "error"


@dataclass
class ThreadInfo:
    id: int
    name: str
    persona: str


@dataclass
class StreamEvent:
    """Represents a streaming event from the chat endpoint."""

    type: StreamEventType
    content: str = ""
    error: str | None = None
    message: str | None = None


class APIError(Exception):
    """Raised when API request fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NeuroMindClient:
    """Client for interacting with the NeuroMind REST API."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def health_check(self) -> dict:
        """Check if the API server is healthy."""
        # TODO: GET /health and return the response. Raise APIError on failure.
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", "http://localhost:8000/health") as response:
                async for line in response.aiter_lines():
                    # Logic: Check for 'data:' prefix and parse remaining content
                    parsed_json = json.loads(line)

            return parsed_json

    async def list_personas(self) -> List[dict]:
        """List all available personas."""
        # TODO: GET /personas and return the JSON response.
        print("CLIENT ---> List personas")
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", "http://localhost:8000/personas") as response:
                async for line in response.aiter_lines():
                    # Logic: Check for 'data:' prefix and parse remaining content
                    parsed_json = json.loads(line)
                    for persona_ in parsed_json:
                        print(persona_['name'], persona_['description'])
        return parsed_json


    async def list_threads(self) -> List[Tuple[str, str, int]]:
        """List all threads as (name, persona, message_count) tuples."""
        # TODO: GET /threads and transform the response.
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", "http://localhost:8000/threads") as response:
                async for line in response.aiter_lines():
                    # Logic: Check for 'data:' prefix and parse remaining content
                    parsed_json = json.loads(line)
                    thread_list = []
                    for thread_ in parsed_json:
                        thread_list.append(tuple(thread_.values()))
                        print(thread_['name'], thread_['persona'], thread_['message_count'])
            return thread_list

    async def get_or_create_thread(
        self, name: str, persona: Persona = Persona.NEUROMIND
    ) -> ThreadInfo:
        """Get or create a thread by name."""
        # TODO: Try GET /threads/{name}, if not found POST to /threads.
        # return self.get_or_create_thread(name, persona)
        # return ThreadInfo(id=3,name="thread2", persona="coder")
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", "http://localhost:8000/threads/"+name) as response:
                async for line in response.aiter_lines():
                    # Logic: Check for 'data:' prefix and parse remaining content
                    parsed_json = json.loads(line)
        if "detail" in parsed_json:
            async with httpx.AsyncClient(base_url="http://localhost:8000") as ac:
                response = await ac.post("/threads", json={"name": name, "persona": persona})
            print("Status Code: ", response.status_code)
            async with client.stream("GET", "http://localhost:8000/threads/"+name) as response:
                async for line in response.aiter_lines():
                    # Logic: Check for 'data:' prefix and parse remaining content
                    parsed_json = json.loads(line)
        else:
            thread_=ThreadInfo(id=parsed_json["id"], name=parsed_json["name"], persona=parsed_json["persona"])

            return thread_

    async def clear_messages(self, thread_name: str) -> None:
        """Clear all messages in a thread."""
        # TODO: DELETE /threads/{thread_name}/messages
        async with httpx.AsyncClient() as client:
            response = await client.delete("http://localhost:8000/threads/" + thread_name + "/messages")
        print("Status Code: ", response.status_code)
        # print("Response: ", response.json())

    async def stream_chat(
        self, thread_name: str, content: str
    ) -> Generator[StreamEvent, None, None]:
        """Stream chat response via SSE. Yields StreamEvent for each chunk."""
        # TODO: POST to /threads/{thread_name}/chat with streaming.
        # Parse SSE lines (data: {...}) and yield appropriate StreamEvents.
        # Handle connection errors gracefully.
        async with httpx.AsyncClient(base_url="http://localhost:8000") as ac:
            response = await ac.post("/threads/"+thread_name+"/chat", json={"content": content})
        print("Status Code: ", response.status_code)

