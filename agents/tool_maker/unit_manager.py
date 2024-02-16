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

        print("instantiated the basic builders \n\n\n\n\n")

        
        self.interface_assistant = self.assistant_manager.get_assistant()
        self.functional_assistant = self.assistant_manager.get_coding_assistant()


        print("instantiated the assistant instances\n")
        self.interface_thread = self.chat_manager.create_empty_thread()
        self.functional_thread = self.chat_manager.create_empty_thread()

        print("instantiated the coding instances\n")


        print("instantiated the coding instances \n")

        self.subthreads = []
        self.subagents = []

    #does not work and used for reference
    def chat(self):
        """
        Accepts user input and performs a thread run with the `interface_assistant`
        """

        while True:
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

    #  runs the actual exec cluster 
    def exec_chat(self):
        """
        Accepts user input and performs a thread run with the `interface_assistant`
        """

            # start with the main thread between the exec and the user.
            # from there let the exec make new threads within the run function


        #initalizing the the threads and assistants list for use later
        #this data structure is fairly basic and will need to be expended to a class later
        #put these into the function, they aren;t needed here
        # no issyes with  the  thread bc the scoping won't die while the agents are relevant and the exec just sends a string to the thread 
        #thread and assistant list should be in the inner class' scope too, much eadier to clean up unused threads
        #should keep a running file system for the responses 

        #removed the product things and made it so that they are less shittily palced and better placed to access and use for the exec agent

        while True:
            print("set up agents\n")
            (
                self.interface_assistant,
                self.interface_thread,
                self.functional_thread,
            ) = self.chat_manager.run_unit(
                subagents = self.subagents,
                subthreads = self.subthreads,
                interface_assistant=self.interface_assistant,
                interface_thread=self.interface_thread,
                functional_assistant=self.functional_assistant,
                functional_thread=self.functional_thread,
            )




if __name__ == "__main__":
    from shared.openai_config import get_openai_client

    client = get_openai_client()
    print("initiated the openai client\n")
    unit = Unit(client=client)
    unit.exec_chat()
