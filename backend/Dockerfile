# use the official Python image from the Docker Hub
FROM python:3.12-slim

# set environment variables to ensure Python outputs everything to the console
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# install dependencies
RUN apt-get update && apt-get install -y gettext

# set the working directory inside the Docker image
WORKDIR /app

# copy the requirements.txt file into the image
COPY requirements.txt /app/

# install the dependencies.
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# copy the entire Django project into the image
COPY . /app/

# collect static files
RUN python manage.py collectstatic --noinput

# expose the port the app runs on
EXPOSE 8000

# run the Gunicorn server
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "api_server.wsgi:application"]
