from fastapi import fastapi

app = FastAPI()

@app.get("/")
def welcome():
    return {"Hello": "World"}