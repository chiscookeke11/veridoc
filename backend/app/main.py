from fastapi import FastAPI


app = FastAPI(
    title="CivicVerify AI Backend",
    version="1.0.0",
    description="Offline AI-powered document verification system"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to CivicVerify AI"
    }