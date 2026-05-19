from typing import List, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlmodel import Field, Session, SQLModel, create_engine, func, select

from neuromind.config import Persona


class Thread(SQLModel, table=True):
    """A conversation thread with a specific persona."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    persona: str


class Message(SQLModel, table=True):
    """A message in a conversation thread."""

    id: int | None = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="thread.id")
    role: str
    content: str


class ThreadManager:
    def __init__(self, db_path: str):
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        SQLModel.metadata.create_all(self.engine)

    def get_thread(self, name: str) -> Thread | None:
        """Retrieves a thread by its unique name."""
        # DONE: Query the database for a thread matching the given name.
        # Filter data from SQL Model
        with Session(self.engine) as session:
            statement = select(Thread).where(Thread.name == name)
            results = session.exec(statement)

            # thread_ = results.one()
            thread_=results.first()
            # for thread in results:
            #     print(thread)
        return thread_

    def get_or_create_thread(
        self, name: str, persona: Persona = Persona.NEUROMIND
    ) -> Thread:
        """Gets an existing thread or creates a new one."""
        # DONE: Return existing thread if found, otherwise create and return a new one.

        # Get Thread (if exists)
        with Session(self.engine) as session:
            statement=select(Thread).where(Thread.name==name)
            results=session.exec(statement)
            thread_=results.first()
        if thread_ is None:
            print('Creating new thread')
            #  Create Thread
            thread_ = Thread(name=name, persona=persona)
            with Session(self.engine) as session:
                # session.add(new_thread)
                session.add(thread_)
                session.commit()
        else:
            print("Thread already exists")
        return thread_

    def list_threads(self) -> List[Tuple[str, str, int]]:
        """Lists all threads with their message counts."""
        # DONE: Return (name, persona, message_count) for all threads.
        with Session(self.engine) as session:
            statement = select(Thread)
            results = session.exec(statement)

            # print("THREAD MANAGER -> list threads")
            # import pdb; pdb.set_trace()
            results = session.exec(statement)
            threads_ = results.all()
            thread_list=[]
            for thread_ in threads_:
                statement = select(Message).where(Message.thread_id == thread_.id)
                messages = session.exec(statement).all()
                thread_list.append((thread_.name, thread_.persona, len(messages)))
        return thread_list

    def add_message(self, thread_id: int, role: str, content: str):
        """Adds a new message to a thread."""
        # DONE: Insert a new message record.
        with Session(self.engine) as session:
            message_ = Message(thread_id=thread_id, role=role, content=content)
            session.add(message_)
            session.commit()


    def get_history(self, thread_id: int) -> List[BaseMessage]:
        """Retrieves the message history as LangChain message objects."""
        # DONE: Return messages as HumanMessage or AIMessage based on role.
        with Session(self.engine) as session:
            statement=select(Message).where(Message.thread_id==thread_id)
            results = session.exec(statement).all()

            if(len(results)>0):
                history_=[]
                for result in results:
                    history_.append(result.content)
            else:
                history_=results
        history_=AIMessage(content=history_)
        return history_

    def clear_messages(self, thread_id: int):
        """Deletes all messages in a thread."""
        # DONE: Remove all messages for the given thread.
        with Session(self.engine) as session:
            statement = select(Message).where(Message.thread_id == thread_id)
            results = session.exec(statement)

            # message_ = results.one()
            message_ = results.first()

            if message_ is not None:
                session.delete(message_)
                session.commit()
