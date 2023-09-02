
FROM python

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY events_help.py .
COPY easter_egg.py .
COPY dnd_event.py .
COPY amongus.py .
COPY codenames.py .
COPY rps.py .
COPY bot.py .
COPY main.py .

CMD ["python3", "main.py"]