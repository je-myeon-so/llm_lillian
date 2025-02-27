FROM python:3.12.7-slim

COPY ./src /src
WORKDIR /src

RUN pip install --no-cache-dir -r ./requirements.txt

#COPY src/* /src/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
