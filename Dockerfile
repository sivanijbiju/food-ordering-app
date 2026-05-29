FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install flask flask_sqlalchemy werkzeug pillow flask-limiter

EXPOSE 9000

CMD ["python3", "app.py"]
