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
if OPENAI_API_KEY is None:
    logger.FancyPrint(logger.Role.SYSTEM, "Není nastaven API klíč pro OpenAI. Zadejte ho do souboru .env pod klíčem OPENAI_API_KEY.")
    exit()

openai.api_key = OPENAI_API_KEY

MODEL = os.getenv('MODEL', 'gpt-3.5-turbo-0125')
DEBUG = int(os.getenv('DEBUG', '0')) # 0 - no debug, 10 - all debug
URL = os.getenv('ROBOT_URL')


MAX_TOKENS = 800

if "gpt-4" in MODEL:
    MODEL_MAX_CONTEXT = 127000

else:
    MODEL_MAX_CONTEXT = 15000


def load_context(filename: str) -> tuple[list[dict], int]:
    """
    Load context from file (remove last line and returns json list).

    Args:
        filename (str): Path to the file with context

    Returns:
        list: List of json messages
        int: Number of tokens used in the context

    Raises:
        FileNotFoundError: If the file is not found.
        JSONDecodeError: If the file content is not valid JSON.
    """
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            data = file.read()
            
        messages = json.loads(data)
        gpt_tokens = int(messages[-1]['used_tokens'])
        return messages[:-1], gpt_tokens # remove last entry, which is the usage and model info
    
    except FileNotFoundError:
        logger.FancyPrint(logger.Role.SYSTEM, f"Soubor {filename} nebyl nalezen.")
        exit()

    except json.JSONDecodeError as e:
        logger.FancyPrint(logger.Role.SYSTEM, f"Obsah souboru {filename} není platný JSON. Error message: {e}")
        exit()


def num_tokens_from_messages(messages: list[dict], model:str = MODEL) -> int:
    # Source:
    # https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken#6-counting-tokens-for-chat-completions-api-calls
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        #print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def get_used_tokens(messages: list[dict]) -> int:
    """
    Get the number of tokens used in the context

    Args:
        messages (list[dict]): List of messages

    Returns:
        int: Number of tokens used
    """
    encoding = tiktoken.encoding_for_model(MODEL)
    
    return len(encoding.encode(json.dumps(messages))) 


def clear_context(messages: list[dict], actual_context_size: int, limit: int = MODEL_MAX_CONTEXT) -> None:
    """
    Frees the context to fit the token limit

    Args:
        messages (list[dict]): List of messages
        actual_context_size (int): Number of tokens used in the context (returned by chatGPT)
    """   
    
    if actual_context_size < limit:
        return
    
    val = actual_context_size - limit
    i = 1
    tmp = (num_tokens_from_messages(messages[1:i]) + get_used_tokens(messages[1:i])) / 2
    while tmp < val:
        tmp = (num_tokens_from_messages(messages[1:i]) + get_used_tokens(messages[1:i])) / 2
        i+=1

    del messages[1:i]
    
    if DEBUG > 4:
        logger.FancyPrint(logger.Role.DEBUG, "REMOVED Context")

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


def better_input() -> str:
    """
    Get user input with better handling of KeyboardInterrupt

    Returns:
        str: User input
    """
    try:
        return input("Zadejte vstup: ")
    except (KeyboardInterrupt, EOFError):
        logger.FancyPrint(logger.Role.SYSTEM,"\nUkončuji program...")
        exit()


def send_to_chatGPT(messages: list[dict], handler: functions.FunctionHandler, log: logger.Logger, attempts: int = 0) -> str:
    clear_context(messages, log.get_context_size())
    try:
        response = openai.ChatCompletion.create(
            model= MODEL,
            messages = messages,
            functions = handler.get_all_specs(),
            max_tokens = MAX_TOKENS,    
        )
    except openai.error.AuthenticationError as e:
        logger.FancyPrint(logger.Role.SYSTEM, "Nastala chyba při autentizaci. Zkontrolujte svůj API key.")
        if DEBUG > 4:
            logger.FancyPrint(logger.Role.DEBUG, f"Chyba: {e}")
        exit()
    
    except (openai.APIError, openai.error.RateLimitError) as e:
        if "You exceeded your current quota" in str(e):
            logger.FancyPrint(logger.Role.SYSTEM, "Byl překročen aktuální limit. Zkontrolujte svůj účet, zda máte zaplaceno.")
            if DEBUG > 4:
                logger.FancyPrint(logger.Role.DEBUG, f"Chyba: {e}")
            exit()

        attempts += 1
        logger.FancyPrint(logger.Role.SYSTEM, "Nastala chyba při komunikaci s chatGPT")
        if DEBUG > 4:  
            logger.FancyPrint(logger.Role.DEBUG, f"Chyba: {e}")
            logger.FancyPrint(logger.Role.DEBUG, f"Pokus číslo: {attempts}")
        
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

    if DEBUG > 4:
        logger.FancyPrint(logger.Role.DEBUG, "total tokens(gpt): " + str(total_tokens))
        logger.FancyPrint(logger.Role.DEBUG, "Get used tokens:" + str(get_used_tokens(messages)))
        try:
            logger.FancyPrint(logger.Role.DEBUG, "Num_tokens... "+ str(num_tokens_from_messages(messages)))
        except:
            pass

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
    
    context_len = 0

    if len(sys.argv) > 1:
        messages, context_len = load_context(sys.argv[1])        
    
    log = logger.Logger(MODEL, messages, context_len)    

    resp = send_to_chatGPT(messages, handler, log)

    if len(messages) > 2:
        logger.FancyPrint(logger.Role.GPT, resp)    

    elif (DEBUG > 3):
        logger.FancyPrint(logger.Role.DEBUG, resp)

    if len(messages) <= 2:
        logger.FancyPrint(logger.Role.GPT, handler.get_welcome_message())

    user_input = better_input()

    # loop until user types "exit" (checked in function is_command())
    while True: 
        if is_command(user_input, handler):
            user_input = better_input()
            continue
        
        messages.append({"role": "user", "content": user_input})
        log.log_message(str(json.dumps({"role": "user", "content": user_input}, indent=4)))

        resp = send_to_chatGPT(messages, handler, log)

        logger.FancyPrint(logger.Role.GPT, resp)
        user_input = better_input()

    
if __name__ == "__main__":
    main()
