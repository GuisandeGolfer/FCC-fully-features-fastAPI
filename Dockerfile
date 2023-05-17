ARG DATABASE_URL
ARG PGDATABASE
ARG PGHOST
ARG PGPASSWORD
ARG PGPORT
ARG PGUSER
ARG ACCESS_TOKEN_EXPIRE_MINUTES
ARG ALGORITHM
ARG SECRET_KEY

FROM python:3.9.7

WORKDIR /usr/src/app 

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
