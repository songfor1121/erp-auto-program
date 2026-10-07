from fastapi import FastAPI

app = FastAPI(title="Invoice AI MVP API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Invoice AI MVP API"}
