FROM python:3.6.3-alpine3.6
ARG DJANGO_SETTINGS_MODULE
ARG DJANGO_ADMIN_URL
ARG DJANGO_SECRET_KEY
ARG DATABASE_URL
ARG DJANGO_SENTRY_DSN
ENV PYTHONBUFFERED=1 DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} DJANGO_ADMIN_URL=${DJANGO_ADMIN_URL} DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} DATABASE_URL=${DATABASE_URL} DJANGO_SENTRY_DSN=${DJANGO_SENTRY_DSN}

# Add new user to run the whole thing as non-root
RUN addgroup -S app
RUN adduser -G app -h /app -D app

# Copy Pipfile and install system-wide
# We're installing system-wide, because we currently have problems
# correctly using the entrypoint.sh, while activating the virtual environment
COPY Pipfile Pipfile.lock /app/
WORKDIR /app

# Install build dependencies for PostgreSQL. While we're at it, also install
# pipenv and all python requirements. Then remove unneeded build dependencies.
RUN apk update \
    && apk add bash \
    && apk add --no-cache --virtual .build-deps \
       gcc \
       musl-dev \
       zlib-dev \
       jpeg-dev \
       libxslt-dev \
       libxml2-dev \
       git \
    && apk add --no-cache postgresql postgresql-dev jpeg \
    && pip install pipenv \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pipenv install --system --deploy" \
    && apk del .build-deps

# Change to user and copy code
USER app
COPY . /app

# Copy dokku specific files
COPY docker/dokku/* /app/

# Let Django collect all staticfiles
RUN python /app/manage.py collectstatic --noinput
