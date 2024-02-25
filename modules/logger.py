import datetime
import json


class Logger:
    log = ""
    model = ""
    log_filename = ""
    Max_tokens = 0


    def __init__(self, model, messages):
        self.model = model

        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")

        self.log_filename = f"./logs/log_{time_str}.txt"
        
        try:
            with open(self.log_filename, 'a', encoding="utf-8") as file: 
                file.write(str("[\n" + json.dumps(messages[0], indent=4))) 
                file.flush()

        except Exception as e:
            print(f"Error logging message: {e}")
        
        for message in messages[1:]:
            self.log_message(str(json.dumps(message, indent=4)))

        #self.log_message(str("[\n" + json.dumps({"role": "user", "content": str({prompt})}, indent=4))) 


    def __del__(self):
        try:
            with open(self.log_filename, 'a', encoding="utf-8") as file: 
                file.write("]\nSuccesfully exited!, Total tokens used: " + str(self.Max_tokens) + ", GPT: " + str(self.model))
                file.flush()

        except Exception as e:
            print(f"Error logging message: {e}")


    def log_message(self, message, Used_tokens = 0): 
        if Used_tokens > self.Max_tokens:
            self.Max_tokens = Used_tokens

        try:
            with open(self.log_filename, 'a', encoding="utf-8") as file: 
                file.write(",\n" + message)
                file.flush()

        except Exception as e:
            print(f"Error logging message: {e}")



