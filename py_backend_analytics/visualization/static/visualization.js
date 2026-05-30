let currentPeriod = 'all_time';
let chartInstance = null;

const periodLabels = {
    all_time: "All Time",
    last_24h: "Last 24 Hours",
    last_month: "Last Month",
    last_year: "Last Year"
};

function safeGetData(period) {
    return window.analyticsData?.[period] || {};
}

/* -------------------------
   BUCKET → CHART DATA
-------------------------- */
function getBucketSeries(data) {
    const raw = data.bucket || [];

    return {
        labels: raw.map(x => x.value),
        visits: raw.map(x => x.count)
    };
}

/* -------------------------
   CHART
-------------------------- */
function updateGraph(data) {
    const canvas = document.getElementById('visitsChart');

    if (chartInstance) chartInstance.destroy();

    const series = getBucketSeries(data);

    if (!series.labels.length) {
        canvas.style.display = 'none';
        return;
    }

    canvas.style.display = 'block';

    chartInstance = new Chart(canvas, {
        type: 'line',
        data: {
            labels: series.labels,
            datasets: [{
                label: 'Visits',
                data: series.visits,
                borderColor: '#00d4ff',
                backgroundColor: 'rgba(0, 212, 255, 0.08)',
                fill: true,
                tension: 0.35,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#27272f' },
                    ticks: { color: '#a1a1aa' }
                },
                x: {
                    grid: { color: '#27272f' },
                    ticks: { color: '#a1a1aa' }
                }
            }
        }
    });
}

/* -------------------------
   TILES
-------------------------- */
function createTileHTML(items, title) {
    if (!Array.isArray(items) || items.length === 0) {
        return `
            <div class="tile">
                <h3>${title}</h3>
                <div class="empty-state">No data</div>
            </div>
        `;
    }

    return `
        <div class="tile">
            <h3>${title}</h3>
            <ul>
                ${items.map(i => `
                    <li>
                        <span class="val">${i.value}</span>
                        <span class="cnt">${i.count}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
}

function updateStatsTiles(data) {
    document.getElementById('stats-tiles').innerHTML =
        createTileHTML(data.top_pages, 'Top Pages 📄') +
        createTileHTML(data.top_sources, 'Top Sources 🔗') +
        createTileHTML(data.top_countries, 'Top Countries 🌍');
}

/* -------------------------
   PERIOD SWITCH
-------------------------- */
function switchPeriod(period) {
    currentPeriod = period;

    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.period === period);
    });

    const data = safeGetData(period);

    document.getElementById('graph-title').textContent =
        `Total Visits • ${periodLabels[period]}`;

    updateStatsTiles(data);
    updateGraph(data);
}

/* -------------------------
   INIT
-------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    switchPeriod('all_time');

    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => switchPeriod(btn.dataset.period));
    });
});
