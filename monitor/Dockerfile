FROM python:3.6
COPY . /app
WORKDIR /app
## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc python-dev libpq-dev && \
    apt-get clean
RUN apt-get update
RUN python3.6 -m pip install --upgrade cython
RUN python3.6 -m pip --no-cache-dir install -r requirements.txt
EXPOSE 8082
CMD ["python3", "app.py"]
