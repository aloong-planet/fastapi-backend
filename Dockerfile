FROM --platform=linux/amd64 python:3.11-alpine

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY requirements.txt /project/
COPY entry.sh /project/
COPY alembic.ini /project/

RUN apk update && \
    apk add --update --no-cache \
    gcc \
    git \
    libc-dev \
    build-base && \
    apk add python3-dev \
    libffi-dev

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /project/requirements.txt

COPY app/ /project/app/
COPY migrations/ /project/migrations/

EXPOSE 8000

WORKDIR /project
ENTRYPOINT ["./entry.sh"]
