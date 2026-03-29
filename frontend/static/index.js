// frontend/static/index.js

document.addEventListener('DOMContentLoaded', () => {
    // HTML에서 필요한 요소들을 찾아서 변수에 저장합니다.
    const form = document.getElementById('generate-form');
    const categorySelect = document.getElementById('category-select');
    const urlInput = document.getElementById('url-input');
    const submitBtn = document.querySelector('.submit-btn');
    const reportsList = document.getElementById('reports-list');

    // 폼이 제출(버튼 클릭)될 때 실행될 함수
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // 페이지가 새로고침되는 기본 동작을 막습니다.

        const category = categorySelect.value;
        const url = urlInput.value;

        // 1. 로딩 상태 UI로 변경
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Generating... ⏳';
        submitBtn.disabled = true; // 중복 클릭 방지
        submitBtn.style.opacity = '0.7';

        try {
            // 2. FastAPI 백엔드로 데이터 전송 (POST 요청)
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ category: category, url: url })
            });

            const result = await response.json();

            // 3. 백엔드에서 성공적으로 응답이 오면
            if(result.success) {
                // 새로운 카드 HTML을 만듭니다.
                const newCard = document.createElement('div');
                newCard.className = 'report-card glass'; // Glassmorphism 클래스 적용

                // 태그 배열을 HTML 문자열로 변환
                const tagsHtml = result.data.tags.map(tag => `<span class="tag">${tag}</span>`).join('');

                newCard.innerHTML = `
                    <div class="card-logo"></div>
                    <div class="card-content">
                        <p class="card-title">${result.data.title} <span class="monochrome-tag">Monochrome</span></p>
                        <p class="card-url">${result.data.url}</p>
                    </div>
                    <div class="card-status Completed">${result.data.status}</div>
                    <div class="card-meta">
                        <p class="card-time">${result.data.time}</p>
                        <div class="card-tags">${tagsHtml}</div>
                    </div>
                    <button class="expand-btn">⌄</button>
                `;

                // 리스트의 맨 위에 새 카드를 자연스럽게 추가합니다.
                reportsList.prepend(newCard);

                // 입력창 비우기
                urlInput.value = '';
            }
        } catch (error) {
            alert('서버와 통신하는 중 오류가 발생했습니다.');
            console.error(error);
        } finally {
            // 4. 통신이 끝나면(성공/실패 무관) 버튼 상태를 원상복구합니다.
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
        }
    });
});