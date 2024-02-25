import subprocess
import modules.functions as functions

Handler = functions.FunctionHandler()

with open('./txt_sources/testing_prompts.txt', 'r', encoding='utf-8') as f:
    question_string = f.read()

questions = question_string.split('\n\n')
questions_prompts = [row.split('\n') for row in questions]

for i, row in enumerate(questions_prompts):
    process = subprocess.Popen(['python', './assistant.py'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

    for j, cell in enumerate(row):
        if cell.startswith('command:'): # command:GetPose#{none}
            command = cell.replace('command:', '')
            com_param = command.split('#')
            print(f"Command: {command}")
            Handler.HandleFunction(com_param[0], dict(com_param[1]))
            continue    

        process.stdin.write(cell + '\n')
        process.stdin.flush()

    output = process.stdout.read()
    error = process.stderr.read()

    if error:
        print(f"Chyba na řádku [{i+1}]: {error}")
    else:
        output = output.replace("Write prompt: ","")    
        print(f"Výstup pro test [{i+1}]: {output}")

    process.stdin.close()
    process.stdout.close()
    process.stderr.close()
    process.wait()
