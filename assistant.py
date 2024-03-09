import os
import openai
from dotenv import load_dotenv
import json
import time
import sys
import tiktoken
from modules import functions
from modules import logger

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

MODEL = os.getenv('MODEL')
DEBUG = int(os.getenv('DEBUG'))
URL = os.getenv('ROBOT_URL')


MAX_TOKENS = 800


def load_context(filename: str) -> list[dict]:
    """
    Load context from file (remove last line and returns json list).

    Args:
        filename (str): Path to the file with context

    Returns:
        list: List of json messages

    Raises:
        FileNotFoundError: If the file is not found.
        JSONDecodeError: If the file content is not valid JSON.
    """
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            data = file.read()
            
        messages = json.loads(data)
        return messages[:-1] # remove last entry, which is the usage and model info
    
    except FileNotFoundError:
        logger.FancyPrint(logger.Role.SYSTEM, f"Soubor {filename} nebyl nalezen.")
        exit()

    except json.JSONDecodeError as e:
        logger.FancyPrint(logger.Role.SYSTEM, f"Obsah souboru {filename} není platný JSON. Error message: {e}")
        exit()


def get_used_tokens(messages: list[dict]) -> int:
    """
    Get the number of tokens used in the context

    Args:
        messages (list[dict]): List of messages

    Returns:
        int: Number of tokens used
    """
    encoding = tiktoken.encoding_for_model(MODEL)
    # TODO: implement token counting which is accurate
    text = sum(len(encoding.encode(message['content'])) if message['content'] is not None else 0 for message in messages)
    function_calling_args = sum(len(encoding.encode(message['function_call']['arguments'])) if 'function_call' in message  else 0 for message in messages)
    print("calculated tokens from messages: " + str(text + function_calling_args))
    
    return text + function_calling_args


def clear_context(messages: list[dict]):
    """
    Frees the context to fit the token limit

    Args:
        messages (list[dict]): List of messages
    """
    while get_used_tokens(messages) > 16000: #TODO remove hardcoded value
        del messages[1]

    return


def is_command(message: str, handler: functions.FunctionHandler) -> bool:
    """
    Check for commands and execute them if found

    Args:
        message (str): User input
        handler (functions.FunctionHandler): Function handler to execute commands
    
    Returns:
        bool: True if the message is a command or empty input, False otherwise
    """
    if not (message := message.lower().strip()):
        return True
    
    if message == "exit":
        exit()
    
    if message == "help":
        logger.FancyPrint(logger.Role.GPT, handler.get_welcome_message())
        return True
    
    return False


def send_to_chatGPT(messages: list[dict], handler: functions.FunctionHandler, log: logger.Logger, attempts: int = 0) -> str:
    clear_context(messages)
    try:
        response = openai.ChatCompletion.create(
            model= MODEL,
            messages = messages,
            functions = handler.get_all_specs(),
            max_tokens = MAX_TOKENS,
        )
    except openai.error.AuthenticationError as e:
        logger.FancyPrint(logger.Role.SYSTEM, f"Nastala chyba při autentizaci. Zkontrolujte svůj API key. \nChyba: {e}")
        exit()

    except (openai.APIError, openai.error.RateLimitError) as e:
        attempts += 1
        logger.FancyPrint(logger.Role.SYSTEM, f"Nastala chyba při komunikaci s chatGPT: {e}")
        
        if attempts > 3:
            logger.FancyPrint(logger.Role.SYSTEM, "Příliš mnoho pokusů o komunikaci s chatGPT. Program se ukončí.")
            exit()

        else:
            logger.FancyPrint(logger.Role.SYSTEM, "Zkusím to znovu...")
            time.sleep((attempts)*5)

        return send_to_chatGPT(messages, handler, log, attempts)

    except openai.error.InvalidRequestError as e:
        # Handle invalid requests, such as exceeding token limits
        if (DEBUG > 0):
            logger.FancyPrint(logger.Role.DEBUG, f"Byl překročen limit tokenů: {e}")

        # Remove part of the context and try again 
        # We need to keep the first message, which is the prompt
        # Also we need to remove bulk of messages because of RateLimitError
        del messages[1:8]

        return send_to_chatGPT(messages, handler, log)
        


    token_usage = response['usage']['completion_tokens']
    total_tokens = response['usage']['total_tokens']

    if (DEBUG > 8):
        logger.FancyPrint(logger.Role.DEBUG, f"Token usage: {token_usage}")

        if token_usage >= MAX_TOKENS:
            logger.FancyPrint(logger.Role.DEBUG, "!!! WARNING !!!!  Max tokens exceeded!")


    message = response.choices[0]['message']['content']
    messages.append(response.choices[0]['message'])
    log.log_message(str(json.dumps(response.choices[0]['message'], indent=4)), total_tokens)

    if "function_call" in response.choices[0]['message']:
        if message is not None:
            logger.FancyPrint(logger.Role.GPT, message)

        function_name = response.choices[0]['message']['function_call']['name']

        try:
            arguments = json.loads(response.choices[0]['message']['function_call']['arguments'])

            response = handler.handle_function(function_name, arguments)
        except json.JSONDecodeError:
            if (DEBUG > 3):
                logger.FancyPrint(logger.Role.DEBUG, "Invalid JSON!\n Arguments: " + response.choices[0]['message']['function_call']['arguments'])

        messages.append({"role": "function", "name": function_name, "content": response})        
        log.log_message(str(json.dumps({"role": "function", "name": function_name, "content": response}, indent=4)), total_tokens)
        
        resp = send_to_chatGPT(messages, handler, log)

        return resp
        

    return message


def main():
    handler = functions.FunctionHandler(DEBUG, URL)

    messages=[
        {"role": "system", "content": str({handler.get_prompt_message()})},
    ]
    
    if len(sys.argv) > 1:
        messages = load_context(sys.argv[1])
    
    log = logger.Logger(MODEL, messages)    

    resp = send_to_chatGPT(messages, handler, log)

    if len(messages) > 2:
        logger.FancyPrint(logger.Role.GPT, resp)    

    elif (DEBUG > 3):
        logger.FancyPrint(logger.Role.DEBUG, resp)

    if len(messages) <= 2:
        logger.FancyPrint(logger.Role.GPT, handler.get_welcome_message())

    user_input = input("Zadejte vstup: ")

    # loop until user types "exit" (checked in function is_command())
    while True: 
        if is_command(user_input, handler):
            user_input = input("Zadejte vstup: ")
            continue
        
        messages.append({"role": "user", "content": user_input})
        log.log_message(str(json.dumps({"role": "user", "content": user_input}, indent=4)))

        resp = send_to_chatGPT(messages, handler, log)

        logger.FancyPrint(logger.Role.GPT, resp)
        user_input = input("Zadejte vstup: ")

    
if __name__ == "__main__":
    main()
