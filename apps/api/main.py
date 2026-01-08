from fastapi import FastAPI

app = FastAPI(title="Lemonfive CRM API")

@app.get("/health")
def health():
    return {"status": "ok"}
