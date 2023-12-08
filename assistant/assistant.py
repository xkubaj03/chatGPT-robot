import os
import openai
from dotenv import load_dotenv
import json
import datetime
from functions import functions
import requests

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

messages=[
    {"role": "user", "content": "Write when ready. Please write short responses."}
]

Handler = functions.FunctionHandler()

def SendToChatGPT(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages = messages,
        functions = Handler.getAllSpecs(),

        max_tokens = 100,
    )

    message = response.choices[0]['message']['content']
    messages.append(response.choices[0]['message'])

    if message is None: #TODO real check
        function_name = response.choices[0]['message']['function_call']['name']
        arguments = json.loads(response.choices[0]['message']['function_call']['arguments'])

        response = Handler.HandleFunction(function_name, arguments)
        
        messages.append({"role": "function", "name": function_name, "content": response})        
        resp = SendToChatGPT(messages)

        return resp
        

    return message

def main():
    user_input = ""

    # loop until user types "exit"
    while user_input != "exit": 
        if user_input != "":
            messages.append({"role": "user", "content": user_input})

        resp = SendToChatGPT(messages)

        print(resp)
        user_input = input("Write prompt: ")


    # Save the log
    current_time = datetime.datetime.now()
    time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")

    log_filename = f"./logs/log_{time_str}.txt"
    messages_json = json.dumps(messages, indent=4) 


    print(Handler.HandleFunction("saveTXT", {"file_path": log_filename, "text": messages_json}))

if __name__ == "__main__":
    main()
