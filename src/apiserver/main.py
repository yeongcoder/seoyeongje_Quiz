from fastapi import FastAPI
from apiserver.controllers import user_controller
from apiserver.controllers import auth_controller
from apiserver.controllers import quiz_controller

app = FastAPI(title="seoyeongje_Quiz")

# 라우터 등록
app.include_router(user_controller.router)
app.include_router(auth_controller.router)
app.include_router(quiz_controller.router)

def main():
    import uvicorn
    uvicorn.run("apiserver.main:app", host="127.0.0.1", port=8000, reload=True)
