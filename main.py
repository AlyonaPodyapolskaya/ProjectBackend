import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from public.crud import router
from database import create_async_tables, init_db
from datetime import datetime

app = FastAPI()
app.include_router(router, prefix="/api/v1")


# Middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Здесь будут указаны действительные домены, с которых можно будет выполнять все методы
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()
    await create_async_tables()
    with open("log.txt", mode="a") as f:
        f.write(f"Приложение запущено: {datetime.now()}\n")


@app.on_event("shutdown")
def shutdown_event():
     with open("log.txt", mode="a") as f:
         f.write(f"Приложение остановлено: {datetime.now()}\n")

@app.get("/")
def index():
    return "Приложение запущено"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)