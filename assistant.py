import os
import openai
from dotenv import load_dotenv
import json
import time
import sys
from modules import functions
from modules.logger import Logger

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
MODEL = os.getenv('MODEL')
DEBUG = int(os.getenv('DEBUG'))
URL = os.getenv('ROBOT_URL')



MAX_TOKENS = 800

def load_context(filename):
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


def send_to_chatGPT(messages, handler, logger, attempts = 0):
    try:
        response = openai.ChatCompletion.create(
            model= MODEL,
            messages = messages,
            functions = handler.getAllSpecs(),
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

        return send_to_chatGPT(messages, handler, logger, attempts+1)


    token_usage = response['usage']['completion_tokens']
    total_tokens = response['usage']['total_tokens']

    if (DEBUG > 8):
        print(f"Token usage: {token_usage}")

        if token_usage >= MAX_TOKENS:
            print("!!! WARNING !!!!  Max tokens exceeded!")


    message = response.choices[0]['message']['content']
    messages.append(response.choices[0]['message'])
    logger.log_message(str(json.dumps(response.choices[0]['message'], indent=4)), total_tokens)

    if "function_call" in response.choices[0]['message']:
        if message is not None:
            print("\n"+ message +"\n")

        function_name = response.choices[0]['message']['function_call']['name']

        try:
            arguments = json.loads(response.choices[0]['message']['function_call']['arguments'])

            response = handler.HandleFunction(function_name, arguments)
        except json.JSONDecodeError:
            if (DEBUG > 3):
                print("Invalid JSON!")  
                print(response.choices[0]['message']['function_call']['arguments'])

        messages.append({"role": "function", "name": function_name, "content": response})        
        logger.log_message(str(json.dumps({"role": "function", "name": function_name, "content": response}, indent=4)), total_tokens)
        
        resp = send_to_chatGPT(messages, handler, logger)

        return resp
        

    return message


def main():
    handler = functions.FunctionHandler(DEBUG, URL)

    messages=[
        {"role": "system", "content": str({handler.getPrompt_message()})},
    ]
    
    if len(sys.argv) > 1:
        messages = load_context(sys.argv[1])
    
    logger = Logger(MODEL, messages)    

    resp = send_to_chatGPT(messages, handler, logger)

    if (DEBUG > 3) or len(messages) > 2:
        print(resp+"\n")
        

    # print welcome message IF messages are empty
    if len(messages) <= 2:
        print(handler.get_welcome_message() + "\n") #TODO: INTRO MESSAGE

    user_input = input("Zadejte vstup: ")

    # loop until user types "exit"
    while user_input != "exit": #TODO: EXIT COMMAND?
        if user_input == "help":
            print(handler.get_welcome_message() + "\n")
            user_input = ""

        if user_input == "":
            user_input = input("Zadejte vstup: ")
            continue
        
        messages.append({"role": "user", "content": user_input})
        logger.log_message(str(json.dumps({"role": "user", "content": user_input}, indent=4)))

        resp = send_to_chatGPT(messages, handler, logger)

        print("\n"+resp+"\n")
        user_input = input("Zadejte vstup: ")

    
if __name__ == "__main__":
    main()
