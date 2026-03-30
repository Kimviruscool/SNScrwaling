# backend/services.py
import asyncio
import httpx

EXTERNAL_SCRAPER_API_KEY = ""


async def fetch_sns_data(category: str, url: str) -> dict:
    if not EXTERNAL_SCRAPER_API_KEY:
        await asyncio.sleep(2)
        return {
            "author": f"@{category}_user",
            "content": f"이것은 {url} 에서 외부 API가 긁어온 원본 게시물 텍스트입니다.",
            "comments": ["정말 유익하네요!", "퍼갑니다", "이건 몰랐네요"],
            "likes": 1500
        }

    api_url = f"https://api.scraper-service.com/extract/{category.lower()}"
    headers = {
        "Authorization": f"Bearer {EXTERNAL_SCRAPER_API_KEY}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, headers=headers, json={"url": url})
        return response.json()