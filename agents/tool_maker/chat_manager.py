import importlib
from pathlib import Path
from agents.tool_maker.tool_manager import ToolManager
from agents.tool_maker.assistant_manager import AssistantManager
import json
import os
import time
from openai import OpenAI

Assistant = type(OpenAI().beta.assistants.list().data[0])
Thread = type(OpenAI().beta.threads.create())



class ChatManager:
    def __init__(self, client: OpenAI):
        self.client = client
        functions_path = os.path.join(
            Path(__file__).absolute().parent, "python_functions"
        )
        self.functions_path = functions_path
        print(self.functions_path)

    def create_thread_from_user_input(self):
        return self.client.beta.threads.create(
            messages=[{"role": "user", "content": input("Begin\n")}]
        )

    def create_empty_thread(self):
        return self.client.beta.threads.create()

    def run_python_from_function_name(self, call):
        print("CALLING FUNCTION")
        base = ".".join(__name__.split(".")[:-1])
        try:
            function_name = call.function.name

            fn = getattr(
                importlib.reload(
                    importlib.import_module(f"{base}.python_functions.{function_name}")
                ),
                function_name,
            )
            print(fn)
            result = fn(**json.loads(call.function.arguments))
            response = {"tool_call_id": call.id, "output": f"result:{result}"}
        except Exception as error:
            response = {
                "tool_call_id": call.id,
                "output": f"{{{type(error)}:{error.args}}}",
            }
        print(response)
        return response
    
    def get_existing_functions(self):
        print("Get Built Functions")
        results = []
        if os.path.exists(self.functions_path):
            for filename in os.listdir(self.functions_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.functions_path,filename)
                    with open(file_path, "r") as file:
                        results.append(file)
        return results

    def handle_fucntion_request(
        self,
        call,
        interface_assistant: Assistant,
        interface_thread: Thread,
        functional_assistant: Assistant,
        functional_thread: Thread,
    ):
        try:
            # Create Function Tool
            schema = ToolManager.schema_from_response(call.function.arguments)
            tool = ToolManager.tool_from_function_schema(schema)
            filtered_interface_assistant_tools = list(filter(lambda tool: tool.type == "function" ,interface_assistant.tools))
            if tool["function"]["name"] in [
                previous_tool.function.name
                for previous_tool in filtered_interface_assistant_tools
            ]:
                tools = [
                    previous_tool
                    for previous_tool in filtered_interface_assistant_tools
                    if previous_tool.function.name != tool["function"]["name"]
                ]
                interface_assistant = self.client.beta.assistants.update(
                    assistant_id=interface_assistant.id,
                    tools=[*tools, tool],
                )
            else:
                interface_assistant = self.client.beta.assistants.update(
                    assistant_id=interface_assistant.id,
                    tools=[*interface_assistant.tools, tool],
                )

            # Generate Python Function
            self.client.beta.threads.messages.create(
                thread_id=functional_thread.id, content=str(tool), role="user"
            )
            functional_run = self.client.beta.threads.runs.create(
                thread_id=functional_thread.id,
                assistant_id=functional_assistant.id,
            )
            
            functional_response = self.simple_run(
                run=functional_run,
                thread=functional_thread,
            )
            function_lines = functional_response.split("```python")[1].split("```")[0]
            name = tool["function"]["name"]
            if not os.path.exists(self.functions_path):
                os.mkdir(self.functions_path)
            with open(f"{self.functions_path}/{name}.py", "w") as file:
                file.writelines(function_lines)
            with open(f"{self.functions_path}/{name}.json", "w") as file:
                file.writelines(str(schema))

            response = {"tool_call_id": call.id, "output": "{success}"}

        except Exception as error:
            # If error, pass details back to assistant for next steps
            response = {
                "tool_call_id": call.id,
                "output": f"{{{type(error)}:{error.args}}}",
            }

        return interface_assistant, response

    def simple_run(self, run, thread):
        """Supply context to assistant and await for next user response"""
        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(
                run_id=run.id, thread_id=thread.id
            )
            if run.status == "requires_action":
                responses = []
                for call in run.required_action.submit_tool_outputs.tool_calls:
                    print(f"calling: {call.function.name}")
                    if call.function.name == "get_existing_functions":
                        available_functions = self.get_existing_functions()
                        response = {"tool_call_id": call.id, "output": f"result:{available_functions}"}
                        responses.append(response)
                    else:
                        response = {"tool_call_id": call.id, "output": f"result:None"}
                        responses.append(response)
                try:
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        run_id=run.id,
                        thread_id=thread.id,
                        tool_outputs=responses,
                    )
                except:
                    print(run.status)
                    print(run)
                    print(call)
                    print(responses)

        response = (
            self.client.beta.threads.messages.list(thread_id=thread.id)
            .data[0]
            .content[0]
            .text.value
        )
        return response

    def begin_run(
        self,
        run,
        interface_assistant,
        interface_thread,
        functional_assistant,
        functional_thread,
    ):
        #seems like run is by default completed, it's not mentioned anywhere in the docs
        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(
                run_id=run.id, thread_id=interface_thread.id
            )
            if run.status == "requires_action":
                tools = []
                responses = []
                for call in run.required_action.submit_tool_outputs.tool_calls:
                    print(f"calling: {call.function.name}")
                    if call.function.name == "function_request":
                        interface_assistant, response = self.handle_fucntion_request(
                            call=call,
                            interface_assistant=interface_assistant,
                            interface_thread=interface_thread,
                            functional_assistant=functional_assistant,
                            functional_thread=functional_thread,
                        )
                    else:
                        response = self.run_python_from_function_name(call)
                    responses.append(response)
                try:
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        run_id=run.id,
                        thread_id=interface_thread.id,
                        tool_outputs=responses,
                    )
                except:
                    print(run.status)
                    print(run)
                    print(call)
                    print(responses)
            if run.status == "failed" or run.status == "expired":
                print("DIED")
                run.status = "completed"
        response = (
            self.client.beta.threads.messages.list(thread_id=interface_thread.id)
            .data[0]
            .content[0]
            .text.value
        )
        return interface_assistant, response
    

    def begin_no_function_run(
        self,
        run,
        interface_assistant,
        interface_thread,
    ):
        start_time = time.time()
        while run.status != "completed":
            ##the runtime chills here until the api returns with a response
            #could probably restructure it so this all happens outside this loop and hangs on the input function 

            run = self.client.beta.threads.runs.retrieve(
                run_id=run.id, thread_id=interface_thread.id
            )

            #print (run)
            if run.status == "requires_action":
                tools = []
                responses = []
                #print(run.status)
                #print(run)
                #print(responses)
        response = (
            self.client.beta.threads.messages.list(thread_id=interface_thread.id)
            .data[0]
            .content[0]
            .text.value
        )
        end_time = time.time()
        duration = end_time - start_time
        print(f"the no function assistant run took {duration}s")

        return interface_assistant, response
    


    def begin_dual_thread_run(
        self,
        runss,
        interface_assistant,
        interface_thread,
        subthreads,
        subagents,
    ):
        start_time = time.time()
        runstat = "completed"
        for run in runss:
            if run.status != "completed":
                #print(run.status)
                print("\n")
                runstat = "not all completed"
    
            
        
        while runstat != "completed":
            print("Dual thread")
            ##the runsstime chills here until the api returns with a response
            #could probably restructure it so this all happens outside this loop and hangs ont eh input function
            for i in range(len(runss)):
                runss[i] = self.client.beta.threads.runs.retrieve(
                    run_id=runss[i].id, thread_id=subthreads[i].id
                )

            #print eventually add on the funcitonality thing

            runstat = "completed"
            for run in runss:
                if run.status != "completed":
                    runstat = "not all completed"

        #      alter to loop and and 
        response = ""
        for subthread_run in subthreads:
            response = (
                self.client.beta.threads.messages.list(thread_id=subthread_run.id)
                .data[0]
                .content[0]
                .text.value
            )
            print("********************************")
            print(response)
            print("******************")

        end_time = time.time()
        duration = end_time - start_time
        print(f"the no function assistant run took {duration//60}:{duration%60}")
        print("********************************")

    
        return interface_assistant, response

    

    #   interate on this to make more flexable agent loops
    #   currently hard coded with only 2 threads 
    #   planned
    #       input handler for ai tools creating a librairy for async thread creation and execution
    #       expand to handle different ai models and their workings. replace the purely openai thread based implementation
    ## might be best to concat the subthread repsonses into a single doccument to better parse and make sense of.
    def run_unit(
        self,
        subthreads,
        subagents,
        interface_assistant: Assistant,
        interface_thread: Thread,
        functional_assistant: Assistant,
        functional_thread: Thread,
    ):
        # #talks to the exec agent
        self.client.beta.threads.messages.create(
            thread_id=interface_thread.id, content=input("type: "), role="user"
        )
        print()
        #   exec agent to sub-agent
        interface_run = self.client.beta.threads.runs.create(
            thread_id=interface_thread.id,
            assistant_id=interface_assistant.id,
            instructions="please remember you are talking to an API, minimize output text tokens for cost saving. You are also able to communicate with the function ai using the description property of function_request.",
        )
        #   runs the chat loop 
        interface_assistant, response = self.begin_no_function_run(
            run=interface_run,
            interface_assistant=interface_assistant,
            interface_thread=interface_thread,       
        )

        print(f"\n\n {response}" )

        
        #loops through subthreads to create the beginning message
        for index, thread in enumerate(subthreads):
            self.client.beta.threads.messages.create(
                thread_id=thread.id, content=input(f"input for subthread {index}:"), role="user"

            )
            print()
        #   exec agent to sub-agent
        # actually starts the run of each of the subthreads and adds them to a subthread runs variable
        subthread_runs = []
        for i in range(len(subthreads)):
            subthread_runs.append(self.client.beta.threads.runs.create(
                thread_id=subthreads[i].id,
                assistant_id=subagents[i].id,
                instructions="please remember you are talking to an API, minimize output text tokens for cost saving. You are also able to communicate with the function ai using the description property of function_request.",
            ))

        print(" \n\n\n\n\n dual thread run\n\n\n\n\n")
        interface_assistant, _ = self.begin_dual_thread_run(
            runss = subthread_runs ,
            interface_assistant=interface_assistant,
            interface_thread=interface_thread,       
            subthreads= subthreads,
            subagents = subagents,
        )


        interface_thread = self.client.beta.threads.retrieve(
            thread_id=interface_thread.id
        )
        functional_thread = self.client.beta.threads.retrieve(
            thread_id=functional_thread.id
        )
        # print(response)
        print()
        return interface_assistant, interface_thread, functional_thread
    



    


