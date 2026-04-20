// frontend/static/index.js

const form       = document.getElementById('analyze-form');
const urlInput   = document.getElementById('url-input');
const topnInput  = document.getElementById('topn-input');
const topnDisplay = document.getElementById('topn-display');
const submitBtn  = document.getElementById('submit-btn');
const btnText    = document.getElementById('btn-text');
const historyList = document.getElementById('history-list');
const totalCount  = document.getElementById('total-count');

// 결과 패널 영역들
const resultEmpty   = document.getElementById('result-empty');
const resultLoading = document.getElementById('result-loading');
const resultError   = document.getElementById('result-error');
const resultContent = document.getElementById('result-content');
const errorMsg      = document.getElementById('error-msg');

// 인메모리 이력 저장소
let history = [];

// ── 슬라이더 숫자 연동 ──
topnInput.addEventListener('input', () => {
    const v = topnInput.value;
    topnDisplay.textContent = v;
    // 슬라이더 채워진 비율 색상 업데이트
    const pct = ((v - 5) / (30 - 5)) * 100;
    topnInput.style.background =
        `linear-gradient(to right, #e11d48 0%, #e11d48 ${pct}%, #e2e8f0 ${pct}%)`;
});

// ── 폼 제출 ──
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url   = urlInput.value.trim();
    const top_n = parseInt(topnInput.value, 10);

    if (!url) return;

    setLoading(true);
    showPanel('loading');

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, top_n }),
        });

        const data = await res.json();

        if (!res.ok) {
            // FastAPI HTTPException → data.detail
            throw new Error(data.detail || '분석에 실패했습니다.');
        }

        renderResult(data, url);
        addHistory(data, url);
        urlInput.value = '';

    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
    }
});

// ── 결과 렌더링 ──
function renderResult(data, url) {
    // 썸네일
    const thumb = document.getElementById('video-thumb');
    thumb.innerHTML = `<img src="https://img.youtube.com/vi/${data.video_id}/mqdefault.jpg" alt="썸네일">`;

    document.getElementById('result-title').textContent = data.title;

    const link = document.getElementById('result-link');
    link.href = url;
    link.textContent = url.length > 50 ? url.slice(0, 50) + '...' : url;

    // 키워드 바 차트
    renderKeywordChart(data.keywords);

    // 자막 미리보기
    document.getElementById('transcript-preview').textContent = data.transcript_preview;

    showPanel('content');
}

function renderKeywordChart(keywords) {
    const chart = document.getElementById('keyword-chart');
    chart.innerHTML = '';

    const maxScore = keywords[0]?.score || 1;

    keywords.forEach((kw, i) => {
        const pct = ((kw.score / maxScore) * 100).toFixed(1);

        // 색상: 상위 3개는 빨강, 나머지는 보라
        const color = i < 3
            ? 'linear-gradient(90deg, #e11d48, #f43f5e)'
            : 'linear-gradient(90deg, #a78bfa, #818cf8)';

        const row = document.createElement('div');
        row.className = 'kw-row';
        row.innerHTML = `
            <span class="kw-label" title="${kw.keyword}">${kw.keyword}</span>
            <div class="kw-bar-bg">
                <div class="kw-bar-fill" style="width:0%; background:${color}" data-target="${pct}%"></div>
            </div>
            <span class="kw-score">${(kw.score * 100).toFixed(2)}%</span>
        `;
        chart.appendChild(row);
    });

    // 바 애니메이션 (다음 프레임에서 너비 적용)
    requestAnimationFrame(() => {
        chart.querySelectorAll('.kw-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.target;
        });
    });
}

// ── 분석 이력 ──
function addHistory(data, url) {
    history.unshift({ data, url, time: new Date() });
    totalCount.textContent = history.length;
    renderHistory();
}

function renderHistory() {
    if (history.length === 0) {
        historyList.innerHTML = '<p class="empty-msg">아직 분석 이력이 없습니다.</p>';
        return;
    }

    historyList.innerHTML = '';
    history.forEach((item, i) => {
        const topKeywords = item.data.keywords.slice(0, 3).map(k => k.keyword).join(', ');
        const el = document.createElement('div');
        el.className = 'history-item';
        el.innerHTML = `
            <div class="history-thumb">
                <img src="https://img.youtube.com/vi/${item.data.video_id}/mqdefault.jpg" alt="">
            </div>
            <div class="history-info">
                <div class="history-title">${item.data.title}</div>
                <div class="history-kw">🔑 ${topKeywords}</div>
            </div>
        `;
        el.addEventListener('click', () => renderResult(item.data, item.url));
        historyList.appendChild(el);
    });
}

// 전체 삭제
document.getElementById('clear-btn').addEventListener('click', () => {
    history = [];
    totalCount.textContent = 0;
    renderHistory();
    showPanel('empty');
});

// ── 패널 표시 제어 ──
function showPanel(name) {
    resultEmpty.classList.add('hidden');
    resultLoading.classList.add('hidden');
    resultError.classList.add('hidden');
    resultContent.classList.add('hidden');

    if (name === 'empty')   resultEmpty.classList.remove('hidden');
    if (name === 'loading') resultLoading.classList.remove('hidden');
    if (name === 'error')   resultError.classList.remove('hidden');
    if (name === 'content') resultContent.classList.remove('hidden');
}

function showError(msg) {
    errorMsg.textContent = msg;
    showPanel('error');
}

function setLoading(on) {
    submitBtn.disabled = on;
    btnText.textContent = on ? '분석 중... ⏳' : '▶ 분석 시작';
}
