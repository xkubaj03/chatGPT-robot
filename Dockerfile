FROM python:3.11.5

EXPOSE 8501

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["streamlit", "run", "chat_interface.py"]

