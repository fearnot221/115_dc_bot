FROM python:3.12-slim AS build

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

LABEL maintainer="Fearnot kenin221@gmail.com"
LABEL description="Discord bot for 115"

WORKDIR /app

COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY . .

CMD ["python3", "bot.py"]