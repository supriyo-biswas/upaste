FROM python:3.6-alpine
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt && python setup_tables.py
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "upaste:app"]
