FROM python:3.11.5

EXPOSE 8501

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py /app
COPY ./modules /app
COPY ./txt_sources /app

COPY ./logs /app/logs
COPY ./src /app/src
COPY ./trash_src /app/trash_src


CMD ["streamlit", "run", "chat_interface.py"]

