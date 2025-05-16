from fastapi import FastAPI
from apiserver.controllers import user_controller
from apiserver.controllers import auth_controller
from apiserver.controllers import quiz_controller

app = FastAPI(title="FastAPI MVC Example")

# 라우터 등록
app.include_router(user_controller.router)
app.include_router(auth_controller.router)
app.include_router(quiz_controller.router)

def main():
    import uvicorn
    uvicorn.run("apiserver.main:app", host="0.0.0.0", port=8000, reload=True)
