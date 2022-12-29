FROM --platform=linux/amd64 python:3.10-alpine as builder

# Update packages and install git
RUN apk update
RUN apk add git

# Copy package requirements file
COPY requirements.txt requirements.txt

# Install deps
RUN pip3 install -r requirements.txt

# FROM --platform=linux/amd64 python:3.10-alpine as app

# Create app directory
WORKDIR /app/

# Bundle app source
COPY . .

CMD [ "python3", "main.py" ]