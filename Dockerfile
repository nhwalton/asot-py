FROM python:3.9-alpine

# Add your application
COPY ./main.py /app/main.py
COPY ./requirements.txt /app/requirements.txt

# Copy and enable your CRON task
COPY ./mycron /app/mycron
RUN crontab /app/mycron

# Create empty log (TAIL needs this)
RUN touch /tmp/out.log

WORKDIR /app

RUN pip install -r requirements.txt

# Start TAIL - as your always-on process (otherwise - container exits right after start)
CMD crond && tail -f /tmp/out.log