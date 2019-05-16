FROM python:latest
WORKDIR /app
COPY . /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8080
EXPOSE 5432
CMD ["python", "./docol_demo/main.py"]


