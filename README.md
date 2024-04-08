# chatGPT-robot

## Project description
This project is focused on developing a virtual assistant powered by chatGPT to help users control and create programs for robotic arm and conveyor belt. The assistant is designed to interpret user commands in natural language to work with the robot.

## Features
- **Relative positioning commands** to directly operate robot
- **Code generation** to create accurate Python scripts  using a custom module
- **Working with programs** The Assistant can list available programs, type them out, save/adjust them, or even run them. 
## How to use
- **Download dependencies** install all packages
- **Initialize environment** set up environment variables like robot address, openAI API key, etc.
- **Use assistant** Write tasks for the assistant as precisely as possible and try it for yourself.

### Using Docker

You can use Docker to run the application, which allows for quick and easy setup without needing to configure dependencies on your host system. Follow these steps to build the Docker image and run it in a container:

1. **Building Docker image**:

   First, build the Docker image from the Dockerfile in your project using the command:

   ```docker build -t your_image_name .```

   This command creates a new Docker image named your_image_name based on the instructions defined in your Dockerfile.

2. **Running the container**:

    After successfully building the image, you can run the container as follows:   
    ```docker run -d --name your_container_name --env-file .env your_image_name```

    This command runs the container in detached mode (-d means in the background) with the name your_container_name based on the your_image_name image.  
    If you prefer to run the container in interactive mode, you can use the -it flag instead.

3. **Interacting with the container**:

    To interact with the running container, use:  
    ```docker exec -it your_container_name /bin/bash```

    This command allows you to access the shell inside the container, which is useful for debugging and executing commands within the container. Once inside the container, you can finally start the assistant by running the command:  
    ```python assistant.py```

    Additionally, you can specify the path to a log file as a parameter, which will load the conversation context from the log. For example:  
    ```python assistant.py /path/to/your/logfile.log```