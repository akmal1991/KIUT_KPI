FROM python:3.8-buster
ENV PYTHONUNBUFFERED=1
#RUN #pip install poetry
#RUN #poetry config virtualenvs.create false
RUN mkdir /code
WORKDIR /code
#COPY pyproject.toml /code/
COPY requirements.txt /code/
#RUN #poetry install
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/

#CMD python manage.py runserver