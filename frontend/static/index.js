// frontend/static/index.js

// ── 요소 참조 ──
const form        = document.getElementById('analyze-form');
const urlInput    = document.getElementById('url-input');
const topnInput   = document.getElementById('topn-input');
const topnDisplay = document.getElementById('topn-display');
const submitBtn   = document.getElementById('submit-btn');
const btnText     = document.getElementById('btn-text');
const historyList = document.getElementById('history-list');
const totalCount  = document.getElementById('total-count');

const panels = {
    empty:   document.getElementById('result-empty'),
    loading: document.getElementById('result-loading'),
    error:   document.getElementById('result-error'),
    content: document.getElementById('result-content'),
};
const errorMsg = document.getElementById('error-msg');

let analysisHistory = [];

// ── 슬라이더 ──
topnInput.addEventListener('input', () => {
    const v = Number(topnInput.value);
    topnDisplay.textContent = v;
    const pct = ((v - 5) / 25) * 100;
    topnInput.style.background =
        `linear-gradient(to right,#e11d48 ${pct}%,#e2e8f0 ${pct}%)`;
});

// ── 탭 전환 ──
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.remove('hidden');
    });
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
        const res  = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, top_n }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || '분석 실패');

        renderResult(data, url);
        addHistory(data, url);
        urlInput.value = '';

    } catch (err) {
        showPanel('error');
        errorMsg.textContent = err.message;
    } finally {
        setLoading(false);
    }
});

// ── 결과 렌더링 ──
function renderResult(data, url) {
    // 영상 헤더
    document.getElementById('video-thumb').innerHTML =
        `<img src="https://img.youtube.com/vi/${data.video_id}/mqdefault.jpg" alt="썸네일">`;
    document.getElementById('result-title').textContent = data.title;
    const link = document.getElementById('result-link');
    link.href = url;
    link.textContent = url.length > 55 ? url.slice(0, 55) + '...' : url;

    // 통계
    document.getElementById('stat-words').textContent     = data.stats.word_count.toLocaleString();
    document.getElementById('stat-sentences').textContent = data.stats.sentence_count.toLocaleString();
    document.getElementById('stat-readtime').textContent  = data.stats.read_time_min + '분';

    // 탭 내용
    renderKeywordChart(data.keywords);
    renderGemini(data.gemini);
    document.getElementById('transcript-preview').textContent = data.transcript_preview;

    // 키워드 탭 기본 활성화
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.querySelector('[data-tab="keywords"]').classList.add('active');
    document.getElementById('tab-keywords').classList.remove('hidden');

    showPanel('content');
}

function renderKeywordChart(keywords) {
    const chart = document.getElementById('keyword-chart');
    chart.innerHTML = '';
    const maxScore = keywords[0]?.score || 1;

    keywords.forEach((kw, i) => {
        const pct   = ((kw.score / maxScore) * 100).toFixed(1);
        const color = i < 3
            ? 'linear-gradient(90deg,#e11d48,#f43f5e)'
            : 'linear-gradient(90deg,#a78bfa,#818cf8)';

        const row = document.createElement('div');
        row.className = 'kw-row';
        row.innerHTML = `
            <span class="kw-label" title="${kw.keyword}">${kw.keyword}</span>
            <div class="kw-bar-bg">
                <div class="kw-bar-fill" style="width:0%;background:${color}" data-target="${pct}%"></div>
            </div>
            <span class="kw-score">${(kw.score * 100).toFixed(2)}%</span>`;
        chart.appendChild(row);
    });

    requestAnimationFrame(() => {
        chart.querySelectorAll('.kw-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.target;
        });
    });
}

function renderGemini(gemini) {
    // 한 줄 요약
    document.getElementById('gemini-oneline').textContent =
        gemini.one_line || '요약 결과가 없습니다.';

    // 핵심 포인트
    const pointsList = document.getElementById('gemini-points');
    pointsList.innerHTML = '';
    if (gemini.points && gemini.points.length > 0) {
        gemini.points.forEach((point, i) => {
            const li = document.createElement('li');
            li.className = 'summary-item';
            li.innerHTML = `<span class="summary-num">${i + 1}</span><span>${point}</span>`;
            pointsList.appendChild(li);
        });
    } else {
        pointsList.innerHTML = '<p class="empty-msg">포인트를 추출하지 못했습니다.</p>';
    }

    // 주제어 태그
    const topicsEl = document.getElementById('gemini-topics');
    topicsEl.innerHTML = '';
    if (gemini.topics && gemini.topics.length > 0) {
        gemini.topics.forEach(topic => {
            const span = document.createElement('span');
            span.className = 'topic-tag';
            span.textContent = topic;
            topicsEl.appendChild(span);
        });
    }
}

// ── 분석 이력 ──
function addHistory(data, url) {
    analysisHistory.unshift({ data, url });
    totalCount.textContent = analysisHistory.length;
    renderHistory();
}

function renderHistory() {
    if (analysisHistory.length === 0) {
        historyList.innerHTML = '<p class="empty-msg">아직 분석 이력이 없습니다.</p>';
        return;
    }
    historyList.innerHTML = '';
    analysisHistory.forEach(item => {
        const topKw = item.data.keywords.slice(0, 3).map(k => k.keyword).join(', ');
        const el = document.createElement('div');
        el.className = 'history-item';
        el.innerHTML = `
            <div class="history-thumb">
                <img src="https://img.youtube.com/vi/${item.data.video_id}/mqdefault.jpg" alt="">
            </div>
            <div class="history-info">
                <div class="history-title">${item.data.title}</div>
                <div class="history-kw">🔑 ${topKw}</div>
            </div>`;
        el.addEventListener('click', () => renderResult(item.data, item.url));
        historyList.appendChild(el);
    });
}

document.getElementById('clear-btn').addEventListener('click', () => {
    analysisHistory = [];
    totalCount.textContent = 0;
    renderHistory();
    showPanel('empty');
});

// ── 유틸 ──
function showPanel(name) {
    Object.values(panels).forEach(p => p.classList.add('hidden'));
    panels[name].classList.remove('hidden');
}

function setLoading(on) {
    submitBtn.disabled = on;
    btnText.textContent = on ? '분석 중... ⏳' : '▶ 분석 시작';
}
