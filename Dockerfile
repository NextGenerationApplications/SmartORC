FROM python:3.9

COPY /Configuration/requirements.txt .
COPY /. .

RUN python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 7000

CMD ["python", "__main__.py"]
