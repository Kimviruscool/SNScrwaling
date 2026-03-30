# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# 📌 backend.api 에서 라우터를 가져옵니다.
from backend.api import router as api_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# 라우터 연결
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    sample_reports = [
        {
            "id": 1,
            "logo": "/static/twitter.svg",
            "title": "AI Post on X",
            "url": "twitter.com/ai_news/status/123...",
            "status": "Completed",
            "time": "2h ago",
            "tags": ["AI", "News"]
        }
    ]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_logo": "SNS Summary", "reports": sample_reports}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)