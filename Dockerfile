FROM python:3.10

WORKDIR /usr/src/app
 
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

COPY . /usr/src/app/

EXPOSE 80
CMD ["gunicorn", "src.app:app", "--bind", "0.0.0.0:80", "--timeout", "30"]