FROM python:3.12.7-slim

COPY ./requirements.txt /fastapi/
COPY ./src /fastapi/src
COPY ./src/.env /fastapi/src/
WORKDIR /fastapi

RUN pip install --no-cache-dir -r ./requirements.txt

#COPY src/* /src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
