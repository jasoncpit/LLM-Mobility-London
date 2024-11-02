import uvicorn
from fastapi import FastAPI
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

