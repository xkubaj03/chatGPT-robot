import os
import openai
from dotenv import load_dotenv
import json
from modules import functions
from modules import logger

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
MODEL = os.getenv('MODEL')

MAX_TOKENS = 800


def SendToChatGPT(messages, Handler, Logger):
    response = openai.ChatCompletion.create(
        model= MODEL,
        messages = messages,
        functions = Handler.getAllSpecs(),
        max_tokens = MAX_TOKENS,
    )
    
    token_usage = response['usage']['completion_tokens']
    global TotalTokens 
    TotalTokens = response['usage']['total_tokens']
    print(f"Token usage: {token_usage}")

    if token_usage >= MAX_TOKENS:
        print("!!! WARNING !!!!  Max tokens exceeded!")


    message = response.choices[0]['message']['content']
    messages.append(response.choices[0]['message'])
    Logger.log_message(str(json.dumps(response.choices[0]['message'], indent=4)), TotalTokens)

    if "function_call" in response.choices[0]['message']:
        if message is not None:
            print(message)

        function_name = response.choices[0]['message']['function_call']['name']

        try:
            arguments = json.loads(response.choices[0]['message']['function_call']['arguments'])

            response = Handler.HandleFunction(function_name, arguments)
        except json.JSONDecodeError:
            print("Invalid JSON!")  
            print(response.choices[0]['message']['function_call']['arguments'])

        messages.append({"role": "function", "name": function_name, "content": response})        
        Logger.log_message(str(json.dumps({"role": "function", "name": function_name, "content": response}, indent=4)), TotalTokens)
        
        resp = SendToChatGPT(messages, Handler, Logger)

        return resp
        

    return message


def main():
    Logger = logger.Logger(MODEL)
    Handler = functions.FunctionHandler()

    messages=[
        {"role": "user", "content": str({Logger.Get_prompt()})}
    ]   

    resp = SendToChatGPT(messages, Handler, Logger)
    print(resp)

    user_input = input("Write prompt: ")

    # loop until user types "exit"
    while user_input != "exit": 
        if user_input == "":
            continue
        
        messages.append({"role": "user", "content": user_input})
        Logger.log_message(str(json.dumps({"role": "user", "content": user_input}, indent=4)))

        resp = SendToChatGPT(messages, Handler, Logger)

        print(resp)
        user_input = input("Write prompt: ")

    
if __name__ == "__main__":
    main()
