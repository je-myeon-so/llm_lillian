FROM python:3.12.7-slim

WORKDIR /fastapi

COPY ./requirements.txt /fastapi/

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY src /fastapi

ENV PYTHONPATH=/fastapi

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
