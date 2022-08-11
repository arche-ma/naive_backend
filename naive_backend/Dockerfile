FROM python:3.11.0b5-buster
WORKDIR /app
COPY . ./
RUN pip3 install -r /app/requirements.txt --no-cache-dir
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
CMD ["python3", "manage.py",  "runserver", "0.0.0.0:8000"]

