
from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Idea Inbox API")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Idea Inbox API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
