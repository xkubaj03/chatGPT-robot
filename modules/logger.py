import datetime
import json


class Logger:
    prompt = ""
    log = ""
    model = ""
    log_filename = ""
    Max_tokens = 0


    def __init__(self, model):
        self.model = model

        with open('./txt_sources/prompt.txt', 'r', encoding='utf-8') as file:
            self.prompt = file.read()

        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")

        self.log_filename = f"./logs/log_{time_str}.txt"
        
        self.log_message(str("[\n" + json.dumps({"role": "user", "content": str({self.prompt})}, indent=4))) 


    def __del__(self):
        self.log_message("]\nSuccesfully exited!, Total tokens used: " + str(self.Max_tokens) + ", GPT: " + str(self.model))


    def log_message(self, message, Used_tokens = 0): 
        if Used_tokens > self.Max_tokens:
            self.Max_tokens = Used_tokens

        try:
            with open(self.log_filename, 'a') as file: 
                file.write(message + ",\n")
                file.flush()

        except Exception as e:
            print(f"Error logging message: {e}")

    def Get_prompt(self):
        return self.prompt
        


