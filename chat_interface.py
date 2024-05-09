import streamlit as st
import openai
import os
import assistant as a
from dotenv import load_dotenv
import modules.functions as f
import modules.logger as l
import json

# Fix pro šířku stránky
st.markdown("""
<style>
.st-emotion-cache-11kmii3 {
    width: 100%;
    padding: 6rem 1rem 1rem;
    max-width: 1100px;
}
.st-emotion-cache-139wi93 {
    width: 100%;
    padding: 1rem 1rem 55px;
    max-width: 1100px;
}
</style>
""", unsafe_allow_html=True)


#func
def is_command(message: str, handler: f.FunctionHandler, messages: list[dict]) -> bool:
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
        
        clear_session_vars()
        st.rerun()
        return True
    
    if message == "help":
        #l.FancyPrint(l.Role.GPT, handler.get_welcome_message())
        messages.append({"role": "show", "content": handler.get_welcome_message()})
        return True
    
    return False

log_directory = './logs'
# Funkce pro získání seznamu logových souborů
def get_log_files(directory= './logs'):
    return [file for file in os.listdir(directory) if file.endswith('.txt')]

# Funkce pro přejmenování souboru
def rename_file(directory, old_name, new_name):
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)
    os.rename(old_path, new_path)


def clear_session_vars():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


# GLOBAL VARIABLES
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    l.FancyPrint(l.Role.SYSTEM, "Není nastaven API klíč pro OpenAI. Zadejte ho do souboru .env pod klíčem OPENAI_API_KEY.")
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

# INITIALIZATION
if "handler" not in st.session_state:
    st.session_state.handler = f.FunctionHandler(DEBUG, URL)

if "logger" not in st.session_state:
    # Initial message setup
    if "load_context" not in st.session_state:
        initial_messages = [
            {"role": "system", "content": str({st.session_state.handler.get_prompt_message()})}
        ]
    else:
        initial_messages, _ = a.load_context("logs/" + st.session_state.load_context)
    
    # Logger initialization
    st.session_state.logger = l.Logger(MODEL, initial_messages, 0)

    # Add welcome message
    if "load_context" not in st.session_state:
        st.session_state.messages = initial_messages + [{"role": "show", "content": st.session_state.handler.get_welcome_message()}]
    else:
        st.session_state.messages = initial_messages
        
elif "messages" not in st.session_state:
    # Only initialize messages if they don't exist, but keep the logger intact
    if "load_context" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": str({st.session_state.handler.get_prompt_message()})},
            {"role": "show", "content": st.session_state.handler.get_welcome_message()}
        ]
    else:
        st.session_state.messages, _ = a.load_context("logs/" + st.session_state.load_context)

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False


# UPDATE CONTEXT LENGTH
st.session_state.context_len = len(st.session_state.messages)

# SHOW MESSAGES
for message in st.session_state.messages[1:]:
    if message["role"] != "function":
        with st.chat_message(message["role"]):
            msg = str(message["content"])
            if "```python" in msg:
                parts = msg.split("```python")
                st.markdown(parts[0])
                for part in parts[1:]:
                    code, rest = part.split("```", 1)
                    st.code(code, language="python")
                    st.markdown(rest)

            else:
                st.markdown(message["content"])

# Generate and display response if processing
if st.session_state.is_processing:
    with st.spinner("Zpracování..."):        
        prompt = st.session_state.messages[-1]["content"]
        if is_command(prompt, st.session_state.handler, st.session_state.messages):
            pass
        else:

            response = a.send_to_chatGPT(
                messages=[msg for msg in st.session_state.messages if msg["role"] in ["system", "assistant", "user"]], 
                handler=st.session_state.handler, 
                log=st.session_state.logger,
                )
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)            
            

        st.session_state.is_processing = False
        st.rerun()

# Handle user input
if not st.session_state.is_processing:    
    if prompt := st.chat_input(placeholder="Zde zadej vstup", disabled=st.session_state.is_processing):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Set processing state to True
        st.session_state.is_processing = True

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        st.session_state.logger.log_message(str(json.dumps({"role": "user", "content": prompt}, indent=4)))

        st.rerun()


# Vytvoření sidebaru
st.sidebar.title("Log Files")
files = ["Žádný"] + get_log_files(log_directory)  # Přidání možnosti 'Žádný'

# Použití radio buttonů pro výběr log souboru
selected_file = st.sidebar.radio("Vyberte log soubor", files, index=0)

# Přejmenování souboru
if selected_file and selected_file != "Žádný":
    new_file_name = st.sidebar.text_input("Nový název souboru", value=selected_file)
    if st.sidebar.button("Přejmenovat"):
        current = st.session_state.logger.log_filename
        
        if current == "./logs/" + selected_file:
            st.session_state.logger.log_filename = "./logs/" + new_file_name
            
        rename_file(log_directory, selected_file, new_file_name)              
        st.sidebar.success("Soubor přejmenován")
        st.rerun()  # Aktualizuje seznam souborů v sidebaru



st.sidebar.write(f"Znovu spustit s načtením vybraného kontextu: **{selected_file}**")  # Tlačítko pro znovunačtení kontextu
if st.sidebar.button("Spustit"):
    # clear session state
    clear_session_vars()
    if selected_file != "Žádný":
        st.session_state.load_context = selected_file
    
    st.rerun()