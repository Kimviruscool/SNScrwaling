# backend/services.py
import httpx
from bs4 import BeautifulSoup


async def fetch_sns_data(category: str, url: str) -> dict:
    """실제로 URL에 접속해서 HTML을 긁어오고 JSON 형태로 추출하는 함수"""
    try:
        # 브라우저인 척 속이기 위한 헤더 (봇 차단 방지)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 비동기로 해당 URL에 접속하여 페이지 내용(HTML) 가져오기
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()  # 에러 발생 시 예외 처리
            html_content = response.text

        # BeautifulSoup으로 HTML 분석
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. 페이지 제목(Title) 추출
        title_tag = soup.find("title")
        page_title = title_tag.text.strip() if title_tag else "제목 없음"

        # 2. 메타 설명(Description) 추출
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"].strip() if meta_desc else "설명 없음"

        # 3. 본문 텍스트 일부 추출 (p 태그 안의 글자들)
        paragraphs = soup.find_all("p")
        body_text = " ".join([p.text.strip() for p in paragraphs])[:200] + "..."

        # 🎯 추출한 데이터를 JSON(딕셔너리) 형태로 조립해서 반환
        extracted_data = {
            "source_url": url,
            "category": category,
            "extracted_title": page_title,
            "extracted_description": description,
            "content": body_text,
        }

        return extracted_data

    except Exception as e:
        return {"error": f"스크래핑 실패: {str(e)}"}