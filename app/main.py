import sys
sys.path.append("./")

from fastapi import FastAPI
from app.routes import router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Idea Inbox API is running!"}

# Include the router
app.include_router(router)