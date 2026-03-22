FROM python:3.11-slim

WORKDIR /app

RUN apt update && apt install -y git

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
