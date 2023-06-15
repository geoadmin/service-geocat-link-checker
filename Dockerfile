FROM python:3.9-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/ .

ARG AWS_ACCESS_KEY
ARG AWS_SECRET_ACCESS_KEY
ENV AWS_ACCESS_KEY $AWS_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY

CMD ["python3", "main.py"]