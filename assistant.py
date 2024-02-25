import os
import openai
from dotenv import load_dotenv
import json
import time
import sys
from modules import functions
from modules import logger

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
MODEL = os.getenv('MODEL')
DEBUG = int(os.getenv('DEBUG'))



MAX_TOKENS = 800

def LoadFromTxt(filename):
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            data = file.readlines()
            data = data[:-1]
            data = ''.join(data)
            
            messages = json.loads(data)
            return messages
    
    except FileNotFoundError:
        print(f"Soubor {filename} nebyl nalezen.")
        exit()

    except json.JSONDecodeError as e:
        print(f"Obsah souboru {filename} není platný JSON. Error message: {e}")
        exit()


def SendToChatGPT(messages, Handler, Logger, attempts = 0):
    try:
        response = openai.ChatCompletion.create(
            model= MODEL,
            messages = messages,
            functions = Handler.getAllSpecs(),
            max_tokens = MAX_TOKENS,
        )

    except Exception as e:
        print(f"Nastala chyba při komunikaci s chatGPT: {e}")
        
        if attempts > 2:
            print("Příliš mnoho pokusů o komunikaci s chatGPT. Program se ukončí.")
            exit()

        else:
            print("Zkusím to znovu...")
            time.sleep((attempts+1)*5)

        return SendToChatGPT(messages, Handler, Logger, attempts+1)


    token_usage = response['usage']['completion_tokens']
    TotalTokens = response['usage']['total_tokens']

    if (DEBUG > 8):
        print(f"Token usage: {token_usage}")

        if token_usage >= MAX_TOKENS:
            print("!!! WARNING !!!!  Max tokens exceeded!")


    message = response.choices[0]['message']['content']
    messages.append(response.choices[0]['message'])
    Logger.log_message(str(json.dumps(response.choices[0]['message'], indent=4)), TotalTokens)

    if "function_call" in response.choices[0]['message']:
        if message is not None:
            print("\n"+ message +"\n")

        function_name = response.choices[0]['message']['function_call']['name']

        try:
            arguments = json.loads(response.choices[0]['message']['function_call']['arguments'])

            response = Handler.HandleFunction(function_name, arguments)
        except json.JSONDecodeError:
            if (DEBUG > 3):
                print("Invalid JSON!")  
                print(response.choices[0]['message']['function_call']['arguments'])

        messages.append({"role": "function", "name": function_name, "content": response})        
        Logger.log_message(str(json.dumps({"role": "function", "name": function_name, "content": response}, indent=4)), TotalTokens)
        
        resp = SendToChatGPT(messages, Handler, Logger)

        return resp
        

    return message


def main():
    Handler = functions.FunctionHandler()

    messages=[
        {"role": "system", "content": str({Handler.getPrompt_message()})},
    ]
    
    if len(sys.argv) > 1:
        messages = LoadFromTxt(sys.argv[1])
    
    Logger = logger.Logger(MODEL, messages)    

    resp = SendToChatGPT(messages, Handler, Logger)

    if (DEBUG > 3) or len(messages) > 2:
        print(resp+"\n")
        

    # print welcome message IF messages are empty
    if len(messages) <= 2:
        print(Handler.getWelcome_message() + "\n") #TODO: INTRO MESSAGE

    user_input = input("Zadejte vstup: ")

    # loop until user types "exit"
    while user_input != "exit": #TODO: EXIT COMMAND?
        if user_input == "help":
            print(Handler.getWelcome_message() + "\n")
            user_input = ""

        if user_input == "":
            user_input = input("Zadejte vstup: ")
            continue
        
        messages.append({"role": "user", "content": user_input})
        Logger.log_message(str(json.dumps({"role": "user", "content": user_input}, indent=4)))

        resp = SendToChatGPT(messages, Handler, Logger)

        print("\n"+resp+"\n")
        user_input = input("Zadejte vstup: ")

    
if __name__ == "__main__":
    main()
