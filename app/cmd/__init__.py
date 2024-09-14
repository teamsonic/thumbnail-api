from fastapi import FastAPI
from app.adapters.handler import healthcheck, say_hello


app = FastAPI()

app.get("/healthcheck")(healthcheck)
app.get("/hello/{name}")(say_hello)
