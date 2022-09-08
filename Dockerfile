FROM python:3.9-slim-buster

COPY /Configuration/requirements.txt .
COPY /. .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7000

CMD ["python", "__main__.py"]
