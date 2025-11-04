FROM python:3.9-slim

WORKDIR /api

COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y gcc python3-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc python3-dev && apt-get clean

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
