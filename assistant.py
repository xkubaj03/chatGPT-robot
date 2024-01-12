import os
import openai
from dotenv import load_dotenv
import json
import datetime
from modules import functions
import requests

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY


MAX_TOKENS = 250


def log_message(log_file, message):
    try:
        with open(log_file, 'a') as file:
            file.write(message + "\n")
            file.flush()
    except Exception as e:
        print(f"Error logging message: {e}")


with open('./txt_sources/prompt.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()


messages=[
    {"role": "user", "content": str({prompt})}
]


Handler = functions.FunctionHandler()


def SendToChatGPT(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages,
        functions = Handler.getAllSpecs(),
        max_tokens = MAX_TOKENS,
    )
    
    token_usage = response['usage']['completion_tokens']
    print(f"Token usage: {token_usage}")
    if token_usage >= MAX_TOKENS:
        print("!!! WARNING !!!!  Max tokens exceeded!")


    message = response.choices[0]['message']['content']
    messages.append(response.choices[0]['message'])
    log_message(log_filename, str(json.dumps(response.choices[0]['message'], indent=4)))

    if "function_call" in response.choices[0]['message']:
        if message is not None:
            print(message)

        function_name = response.choices[0]['message']['function_call']['name']
        try:
            arguments = json.loads(response.choices[0]['message']['function_call']['arguments'])

            response = Handler.HandleFunction(function_name, arguments)
        except json.JSONDecodeError: # TODO: For some reason json.loads doesn't work because last "}" always missing
            print("Invalid JSON!")   # I think that it was because i set max_tokens to 100
            print(response.choices[0]['message']['function_call']['arguments'])
            exit()
            #response = "Invalid JSON! Can you please try again with correct one?" 
            arguments = json.loads(response.choices[0]['message']['function_call']['arguments'] + "\n}")

            response = Handler.HandleFunction(function_name, arguments)

        messages.append({"role": "function", "name": function_name, "content": response})        
        log_message(log_filename, str(json.dumps({"role": "function", "name": function_name, "content": response}, indent=4)))
        
        resp = SendToChatGPT(messages)

        return resp
        

    return message


def main():
    # Create Log
    current_time = datetime.datetime.now()
    time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")

    global log_filename
    log_filename = f"./logs/log_{time_str}.txt"
    
    log_message(log_filename, str(json.dumps(messages, indent=4)))
    

    user_input = ""

    # loop until user types "exit"
    while user_input != "exit": 
        if user_input != "":
            messages.append({"role": "user", "content": user_input})
            log_message(log_filename, str(json.dumps({"role": "user", "content": user_input}, indent=4)))

        resp = SendToChatGPT(messages)

        print(resp)
        user_input = input("Write prompt: ")

    log_message(log_filename, "Succesfully exited!")
    
if __name__ == "__main__":
    main()
