FROM python:3.11.1

COPY ./code /usr/src/app

WORKDIR /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "VehicleDigitalTwin.py"]
