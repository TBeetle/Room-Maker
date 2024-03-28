FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update -y && \
  apt-get install -y texlive-full && \
  rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Run migrations
RUN python manage.py migrate

CMD gunicorn layoutGenerator.wsgi
