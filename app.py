import sys
from concurrent.futures import thread
from typing import List

from requests import Session

from neuromind.client import APIError, NeuroMindClient, StreamEventType, ThreadInfo
from neuromind.config import Config, Persona
from neuromind.ui_manager import UIManager

import asyncio

class NeuroApp:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.client = NeuroMindClient(base_url)
        self.ui = UIManager()
        self.active_thread: ThreadInfo | None = None

        try:
            # print("APP ---> Try")
            health = self.client.health_check()

            # BUG: Temp fix
            # self.model_name = health.get("model", "unknown")
            # comment: temporary due to empty functions in the client
            self.model_name = "qwen:0.5b"

        except APIError as e:
            self.ui.print_critical_error(
                f"{e.message}\nMake sure the server is running: python start_server.py"
            )
            # print("APP ---> Exception")
            sys.exit(1)
        self.active_thread = asyncio.run(self.client.get_or_create_thread(Config.DEFAULT_THREAD))
        # Config.DEAFAULT_THREAD="master"

        # ----------------------------------------------------------------------
        #  TEMPORARY CODE
        # from sqlmodel import Field, SQLModel,create_engine,Session, select
        # # Create Table --> Thread
        # class Thread(SQLModel, table=True):
        #     """A conversation thread with a specific persona."""
        #     id: int | None = Field(default=None, primary_key=True)
        #     name: str = Field(unique=True, index=True)
        #     persona: str
        # # Create Table --> Message
        # class Message(SQLModel, table=True):
        #     """A message in a conversation thread."""
        #     id: int | None = Field(default=None, primary_key=True)
        #     thread_id: int = Field(foreign_key="thread.id")
        #     role: str
        #     content: str
        #
        # db_path = "data/neuromind.db"
        # engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False},echo=True )
        # SQLModel.metadata.create_all(engine)  # creates the table
        #
        # #  Create Thread
        # name="Thread1"
        # persona="neuromind"
        # new_thread = Thread(name=name, persona=persona)
        # thread_1= Thread(name="thread2", persona="coder",id=3)
        # thread_2= Thread(name="thread4", persona="coder")
        #
        # print("APP ---> Write Thread to a SQL Model")
        # import pdb; pdb.set_trace()
        # # INSERT DATA (SQL Model)
        # with Session(engine) as session:
        #     # session.add(new_thread)
        #     session.add(thread_1)
        #     session.commit()
        #
        # with Session(engine) as session:
        #     # session.add(new_thread)
        #     session.add(thread_2)
        #     session.commit()
        #
        #
        # # Create Message
        # thread_id = 3
        # role = persona
        # content = "What is the future of electric vehicles"
        # print("APP ---> Create Message")
        # message_1 = Message(thread_id=thread_id, role=persona, content=content)
        # import pdb; pdb.set_trace()
        #
        # self.active_thread = new_thread
        #
        #
        #
        # with Session(engine) as session:
        #     # session.add(new_thread)
        #     session.add(message_1)
        #     session.commit()
        #
        # print("APP ---> List all values")
        # import pdb; pdb.set_trace()
        # with Session(engine) as session:
        #     statement = select(Thread)
        #     results = session.exec(statement)
        #     threads_ = results.all()
        #
        #     for thread_ in threads_:
        #         print(thread_)
        #
        #
        # print("APP ---> Filter Data SQL Model")
        # import pdb;pdb.set_trace()
        # # Filter data from SQL Model
        # with Session(engine) as session:
        #     statement=select(Thread).where(Thread.name=="thread5")
        #     results=session.exec(statement)
        #
        #     thread_=results.first()
        #
        #     for thread in results:
        #         print(thread)
        #
        # print("APP ---> Update data in a SQL Model")
        # import pdb; pdb.set_trace()
        # # Update data in SQL Model
        # with Session(engine) as session:
        #     statement=select(Thread).where(Thread.name=="thread2")
        #     results=session.exec(statement)
        #
        #     # throws error if more than one statement
        #     thread=results.one()
        #     print(f"Hero: {thread}")
        #
        #     thread.name="thread3"
        #
        #     session.add(thread)
        #     session.commit()
        #     session.refresh(thread)
        #
        #     print(f"Updated thread: {thread}")
        #
        # print("APP ---> Delete data in a SQL Model")
        # import pdb;pdb.set_trace()
        # # Delete data in SQL Model
        #
        # thread_del="thread3"
        # with Session(engine) as session:
        #     statement = select(Thread).where(Thread.name == thread_del)
        #     results = session.exec(statement)
        #
        #     # throws error if more than one statement
        #     thread = results.one()
        #     print(f"Hero: {thread}")
        #
        #     session.delete(thread)
        #     session.commit()
        #
        #     statement = select(Thread).where(Thread.name == "thread3")
        #     results = session.exec(statement)
        #
        #     thread=results.first()
        #
        #     if thread is None:
        #         print(f"There is no thread named:{thread_del}")
        #
        #     print(f"Updated thread: {thread}")
        # -----------------------------------------------------------------------
        # print("APP ---> Temporary Code Ends Here")
        # ------------------------------------------------------------------------




    def _cmd_list(self):
        """Display all available threads."""
        # TODO: Fetch and display threads.
        pass

    def _cmd_new(self, args: List[str]):
        """Create a new thread with a selected persona."""
        # TODO: Prompt for persona, create thread, update active_thread.
        pass

    def _cmd_switch(self, args: List[str]):
        """Switch to an existing thread."""
        # TODO: Switch active_thread to the specified thread.
        pass

    def _cmd_clear(self):
        """Clear all messages in the current thread."""
        # TODO: Confirm and clear messages.
        pass

    def _process_stream(self, events) -> None:
        """Process streaming events and update the live display."""
        thought_buffer = ""
        response_buffer = ""

        # TODO: Iterate events, accumulate content, update live display.
        # Handle REASONING, CONTENT, ERROR, and DONE event types.
        pass

    def run(self):
        """Main application loop."""
        # print("APP ---> RUN")

        self.ui.show_header(self.model_name, self.active_thread.name)
        while True:
            try:
                user_input = self.ui.get_user_input(self.active_thread.name)
                from neuromind.thread_manager import ThreadManager
                from sqlmodel import Field, Session, SQLModel, create_engine, func, select
                from neuromind.thread_manager import Thread
                thread_manager = ThreadManager("data/neuromind.db")
                # TODO: Handle slash commands (/exit, /list, /new, /switch, /clear).
                # For regular input, stream the chat response.
                if(user_input=="/list"):
                    print("Show available threads")
                    thread_list=thread_manager.list_threads()
                    for thread_name in thread_list:
                        print(thread_name)

                elif(user_input=="/new"):
                    print('Create a new thread (prompt user for Persona)')
                    name = input("Enter thread name: ")
                    # TODO: Automatical assign thread name
                    persona = input("Enter thread persona(code / logician / neuromind / roaster / teacher : ")

                    thread_new=thread_manager.get_or_create_thread(name, persona)
                    print("Thread created: ",thread_new)
                elif(user_input=="/switch"):
                    print("Switch active context.")
                    name = input("Enter thread name: ")
                    thread_new=thread_manager.get_thread(name)
                    self.active_thread.name=thread_new.name
                    print("Active thread: ",thread_new.name)
                elif(user_input=="/clear"):
                    print("Wipe the current thread's message history: ",self.active_thread.name)
                    with Session(thread_manager.engine) as session:
                        statement=select(Thread).where(Thread.name==self.active_thread.name)
                        results=session.exec(statement)

                        thread_=results.first()
                    thread_manager.clear_messages(thread_.id)
                elif(user_input=="/exit"):
                    sys.exit(0)
                else:
                    print("Use /exit to quit.")


            except KeyboardInterrupt:
                self.ui.print_info("\nUse /exit to quit.")
            except APIError as e:
                self.ui.print_error(e.message)
            except Exception as e:
                self.ui.print_error(str(e))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NeuroMind CLI")
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="API server URL (default: http://localhost:8000)",
    )
    args = parser.parse_args()
    app = NeuroApp(base_url=args.server)
    app.run()
