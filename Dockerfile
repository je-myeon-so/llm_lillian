FROM python:3.12.7-slim

WORKDIR /src

COPY ./requirements.txt /src/

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY src/* /src/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
