from .main.api.api import app


@app.get("/role_root")
def role_root():
    return {"message": "Hello, I am external!"}