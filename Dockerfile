FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/poster/

# Copy resources
COPY . .

RUN chmod +x ./bin/entrypoint.sh
RUN chmod +x ./bin/validate-python.sh
RUN chmod +x ./bin/build-sass.sh
RUN chmod +x ./bin/watch-sass.sh

# Configure env
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-psycopg2 \
    gettext \
    nodejs \
    npm \
    libmagic1

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN npm install -g sass

EXPOSE $PORT
