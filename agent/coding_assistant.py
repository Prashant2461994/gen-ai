import json
from openai import OpenAI
import requests
from dotenv import load_dotenv
import os
import zipfile

load_dotenv()

client = OpenAI()


def generateSpringBootApp(curl_command, file, extract_to=".\\"):

    import subprocess

    try:
        print(f"creating springboot app {curl_command}")
        subprocess.run(curl_command, shell=True)

        # Step 2: Unzip the file
        if not os.path.exists(file):
            raise FileNotFoundError(f"The file '{file}' does not exist.")

        # Step 2: Unzip the file
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(extract_to)

        print(f"✅ Project extracted to: {extract_to}")
        return "project created successfully."
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while creating the project: {e}")
        return "Could not create project"
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return "Could not create project - file not found"
    except zipfile.BadZipFile as e:
        print(f"Invalid zip file: {e}")
        return "Could not create project - invalid zip file"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Could not create project due to an unexpected error"


available_tools = {
    "generateSpringBootApp": {
        "fn": generateSpringBootApp,
        "description": "Takes curl command as input and generate springboot app",
    }
}

system_prompt = """
You are a coding assistant, who is expert in Java and Springboot.
Your task is to help generate code or projects related to java and springboot in current directory using available tools.
You work on start, plan, action and observe mode.
For the given user query and available tools, plan the step by step execution and based on planning,
select the relevant tool from the available tool  and based on tool selection you perform the action.


Available tools:
    -generateSpringBootApp:  is a tool which generate maven springboot applcation with all the given dependency 

Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query



Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
         "input": {{
            "curl_command": "string",
            "file": "string"
         }}
    }}

Example:
User query: Please generate a sprinboot application with springweb and H2 database
Output: {{ "step":"plan","content": "The user is interested in generating springboot application with spring web and H2 dependencies" }}
Output: {{ "step":"plan","content": "From available tool I should call generateSpringBoot" }}
Output: {{ "step": "action", "function": "generateSpringBoot", "input": {{
                                                            "curl_command": "curl https://start.spring.io/starter.zip "
                                                                            "-d dependencies=web,h2 "
                                                                            "-d language=java "
                                                                            "-d type=maven-project "
                                                                            "-d name=demoapp "
                                                                            "-d groupId=com.example "
                                                                            "-d artifactId=demoapp "
                                                                            "-d packageName=com.example.demoapp "
                                                                            "-o demoapp.zip",
                                                            "file": "demoapp.zip"}} 
    }}
Output: {{ "step": "observe", "output": "Springboot demo.zip app created" }}
Output: {{ "step": "output", "content": "Sprinboot app is created on your system successfully , Please use command <command reequired to run springboot app> locally " }}


"""

messages = [{"role": "system", "content": system_prompt}]

while True:
    user_query = input("> ")
    messages.append({"role": "user", "content": user_query})

    count = 0
    while True:
        response = client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"}, messages=messages
        )
        # print(response)
        parsed_output = json.loads(response.choices[0].message.content)
        print("jsonfied respose ::", parsed_output)
        messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            if count > 6:
                break
            print(f"🎈 : {parsed_output.get('content')}")
            count = count + 1
            continue

    

        if parsed_output.get("step") == "action":
            if parsed_output.get("function", False) != False:
                tool_name = parsed_output.get("function")
                if "input" in parsed_output:
                    tool_input = parsed_output.get("input", {})
                    if "curl_command" in tool_input and "file" in tool_input:
                        curl_command = tool_input.get("curl_command")
                        file_name = tool_input.get("file")  # Extract the file name

                        if tool_name in available_tools:
                            tool_fn = available_tools[tool_name].get("fn")
                            if callable(tool_fn):
                                output = tool_fn(curl_command, file_name)
                                messages.append(
                                    {
                                        "role": "assistant",
                                        "content": json.dumps(
                                            {"step": "observe", "output": output}
                                        ),
                                    }
                                )
                                continue

                            else:
                                print(
                                    f"⚠️ Log: The function for tool '{tool_name}' is not callable."
                                )
                                output = "Function not callable"
                    else:
                        print(
                            "⚠️ Log: Missing required keys 'curl_command' or 'file' in input."
                        )
                        output = "Missing required input keys"

            elif "function" not in parsed_output:
                print("⚠️ Log: Parsed output does not contain the 'function' key.")

        if parsed_output.get("step") == "observe":
            print(f"👀 {parsed_output.get("content")}") 
            continue;
        if parsed_output.get("step") == "output":
            print(f"🟢 {parsed_output.get("output")}") 
            break;