import datetime
import json
import colorama
import difflib
from enum import Enum


class CodeHighlight:
    code = ""

    @classmethod
    def print_code_with_diff(cls, new_code: str) -> None:
        """
        This method prints the code with color highlighting.
        """
        if cls.code == "":
            # First time calling this method
            cls.code = new_code.splitlines()
            FancyPrint(Role.CODE, new_code)
            return
        
        # Find the differences between the two codes
        new_code = new_code.splitlines()

        differ = difflib.Differ()
        code_differences = list(differ.compare(cls.code, new_code))

        different_lines_count = sum(1 for line in code_differences if line.startswith('+') or line.startswith('-'))

        # If there are more than 70% of lines different, print the whole code again
        if different_lines_count / len(cls.code) > 0.7:
            cls.code = new_code
            FancyPrint(Role.CODE,  "\n".join(new_code)) # Connect rows
            return

        for row in code_differences:
            if row.startswith('+'):
                FancyPrint(Role.CODE_HIGHLIGHT, row)
            elif row.startswith('-'):
                #FancyPrint(Role.CODE_HIGHLIGHT, row)
                pass
            elif row.startswith('?'):
                pass
            else:
                FancyPrint(Role.CODE, row)

        # Update the current code
        cls.code = new_code
        

    def separate_python_code(message: str) -> list:
        """
        This separates the input string into three parts. Message, python code and the rest of the message.
        If there is no python code, returns the original string.
        Be careful this only works if maximum of one python code is in the string.
        """
        # Finds first separator
        first_split = message.split("```python", 1)

        # If the first separator is not found
        if len(first_split) == 1:
            return [message]
        
        first_part, rest_of_message = first_split
        # Finds second separator
        second_split = rest_of_message.split("```", 1)
        
        if len(second_split) == 1:
            # Second separator not found
            return [message]
        
        middle_part, last_part = second_split
        return [first_part, '```python' + middle_part + '```', last_part]


class Role(Enum):
    SYSTEM = "system"                   # LIGHTRED_EX
    DEBUG = "function"                  # LIGHTMAGENTA_EX
    GPT = "gpt"                         # LIGHTBLUE_EX
    CODE = "code"                       # LIGHTGREEN_EX
    CODE_HIGHLIGHT = "code_highlight"   # LIGHTWHITE_EX or RED
    DEFAULT = "default"


def FancyPrint(role: Role, message: str) -> None:
    """
    Method for printing messages with color coding (or later for logging or sound module)
    """
    if role == Role.SYSTEM:
        print(colorama.Fore.LIGHTRED_EX + message + colorama.Style.RESET_ALL)

    elif role == Role.DEBUG:
        print(colorama.Fore.LIGHTMAGENTA_EX + message + colorama.Style.RESET_ALL)

    elif role == Role.CODE:
        print(colorama.Fore.LIGHTGREEN_EX + message + colorama.Style.RESET_ALL)

    elif role == Role.CODE_HIGHLIGHT:
        print(colorama.Fore.RED + message + colorama.Style.RESET_ALL)

    elif role == Role.GPT:
        list = CodeHighlight.separate_python_code(message)
        
        if len(list) == 3:
            print(colorama.Fore.LIGHTBLUE_EX + "\n" + list[0] + colorama.Style.RESET_ALL)
            CodeHighlight.print_code_with_diff(list[1])
            print(colorama.Fore.LIGHTBLUE_EX + list[2] + "\n" + colorama.Style.RESET_ALL)
            return
        

        print(colorama.Fore.LIGHTBLUE_EX + "\n" + message + "\n" + colorama.Style.RESET_ALL)        
        
        
    else:
        colorama.Style.RESET_ALL
        print(message)

class Logger:
    log = ""
    model = ""
    log_filename = ""
    Max_tokens = 0


    def __init__(self, model: str, messages: list):
        self.model = model

        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")

        self.log_filename = f"./logs/log_{time_str}.txt"
        
        try:
            with open(self.log_filename, 'a', encoding="utf-8") as file: 
                file.write(str("[\n" + json.dumps(messages[0], indent=4))) 
                file.flush()

        except Exception as e:
            FancyPrint(Role.SYSTEM, f"Error logging message: {e}")
        
        for message in messages[1:]:
            self.log_message(str(json.dumps(message, indent=4)))



    def __del__(self):
        try:
            with open(self.log_filename, 'a', encoding="utf-8") as file: 
                file.write("]\nSuccesfully exited!, Total tokens used: " + str(self.Max_tokens) + ", GPT: " + str(self.model))
                file.flush()

        except Exception as e:
            FancyPrint(Role.SYSTEM, f"Error logging message: {e}")


    def log_message(self, message, Used_tokens = 0): 
        if Used_tokens > self.Max_tokens:
            self.Max_tokens = Used_tokens

        try:
            with open(self.log_filename, 'a', encoding="utf-8") as file: 
                file.write(",\n" + message)
                file.flush()

        except Exception as e:
            FancyPrint(Role.SYSTEM, f"Error logging message: {e}")



