# Use official Railway 
FROM python:3.11

# Set working directory
WORKDIR .

# Install dependencies
RUN apt-get update
RUN apt-get install -y texlive-full
RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
