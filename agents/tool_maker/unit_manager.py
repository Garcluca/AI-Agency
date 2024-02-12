from agents.tool_maker.assistant_manager import AssistantManager
from agents.tool_maker.chat_manager import ChatManager


class Unit:
    """
    A class which creates and exposes chat functionality for a Unit Agent.
    A Unit is a first prototype for a Minmium Viable Agent (MVA).

    A `Unit` is two `Assistant`s in a symbiotic relationship.
    One `Assistant` is the Interface with a thread sharing input with the contents passed via the `chat` method,
    the other `Assistant` is a functional one which shares a thread with `submit_tool` requests during runs and is responsible for writing python functions.

    :param AssistantManager assistant_manager: Creates and retrieves different `Assistant` types
    :param ChatManager chat_manager: provides functionality for managing `Threads`
    :param Assistant interface_assistant: talks with `chat` method
    :param Assistant functional_assistant: writes python functions when `OpenAI.beta.threads.runs.submit_tools` is called in `chat`
    :param Thread interface_thread: `Thread` between `interface_assistant` and `chat`
    :param Thread functional_thread: `Thread` between `functional_assistant` and `OpenAI.beta.threads.runs.submit_tools`
    :returns: this is retured
    """

    def __init__(self, client):
        """
        Instantiates a Unit object

        :param Client client: OpenAI instance
        """

        #instantiates the assistant and chat managers
        # they probably share an agent thread pool with the inclusion of the client

        self.assistant_manager = AssistantManager(client=client)
        self.chat_manager = ChatManager(client=client)

        self.interface_assistant = self.assistant_manager.get_assistant()
        self.functional_assistant = self.assistant_manager.get_coding_assistant()

        self.interface_thread = self.chat_manager.create_empty_thread()
        self.functional_thread = self.chat_manager.create_empty_thread()

    def chat(self):
        """
        Accepts user input and performs a thread run with the `interface_assistant`
        """

            # start with the main thread between the exec and the user.
            # from there let the exec make new threads within the run function
            # ?? possible error being the scoping of the threads, maybe need to pass the client thread interfece
         
        while True:
            print("GEWGNRHYEMJTEHQFBANSHMY5J4TH3RGQAFGNHMTSYRJTEHW")
            (
                self.interface_assistant,
                self.interface_thread,
                self.functional_thread,
            ) = self.chat_manager.run_unit(
                interface_assistant=self.interface_assistant,
                interface_thread=self.interface_thread,
                functional_assistant=self.functional_assistant,
                functional_thread=self.functional_thread,
            )

    #   runs the actual exec cluster 
    # idk   if it actully does allow it to apss teh thread createer and the agent creator to the other function without fucking it completeley
    def exec_chat(self):
        """
        Accepts user input and performs a thread run with the `interface_assistant`
        """

            # start with the main thread between the exec and the user.
            # from there let the exec make new threads within the run function
            # ?? possible error being the scoping of the threads, maybe need to pass the client thread interfece
         
        while True:
            print("GEWGNRHYEMJTEHQFBANSHMY5J4TH3RGQAFGNHMTSYRJTEHW")
            #the loop is for killing the whole thing while preserving the 
            (
                self.interface_assistant,
                self.interface_thread,
                self.functional_thread,
                self.assistant_manager,
            ) = self.chat_manager.run_exec(
                interface_assistant=self.interface_assistant,
                interface_thread=self.interface_thread,
                functional_assistant=self.functional_assistant,
                functional_thread=self.functional_thread,
                assistant_manager=self.assistant_manager,
            )




if __name__ == "__main__":
    from shared.openai_config import get_openai_client

    client = get_openai_client()

    unit = Unit(client=client)
    unit.chat()
