FROM python:3.9

COPY /Configuration/requirements.txt .
COPY /. .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install converter-package==0.7

EXPOSE 7000

CMD ["python", "__main__.py"]
