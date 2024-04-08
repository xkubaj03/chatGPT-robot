FROM python:3.11.5

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

#CMD ["python", "assistant.py"]
CMD ["/bin/bash"]

