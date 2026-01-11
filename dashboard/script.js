// Chart Configuration
const ctx = document.getElementById('mainMarketChart').getContext('2d');
let marketChart;

function initChart() {
    const data = {
        labels: Array.from({ length: 20 }, (_, i) => ``),
        datasets: [{
            label: 'Confianza de Análisis',
            data: Array.from({ length: 20 }, () => 0),
            borderColor: '#00d9ff',
            backgroundColor: 'rgba(0, 217, 255, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 2,
            borderWidth: 2
        }]
    };

    marketChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: {
                    min: 0, max: 100,
                    grid: { color: 'rgba(48, 54, 61, 0.3)' },
                    ticks: { color: '#8b949e', font: { size: 10 } }
                }
            }
        }
    });
}

// Fetch Real Data from API Bridge
async function fetchBotStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        // Update Stats
        document.getElementById('top-balance').innerText = `$${data.balance.toLocaleString()}`;
        document.getElementById('winrate-pct').innerText = `${data.win_rate}%`;
        document.querySelector('.progress-bar-fill').style.width = `${data.win_rate}%`;
        document.getElementById('ops-count').innerText = data.ops_count;
        document.getElementById('current-phase').innerText = data.current_phase;

        // Update Chart
        if (data.active_asset !== "Ninguno") {
            document.getElementById('active-asset').innerText = data.active_asset;
            document.getElementById('current-confidence').innerText = `${data.confidence}% Confianza`;

            marketChart.data.datasets[0].data.shift();
            marketChart.data.datasets[0].data.push(data.confidence);
            marketChart.update('none');
        }

        // Update Logs
        const logContainer = document.getElementById('bot-logs');
        if (data.logs && data.logs.length > 0) {
            // Solo añadir logs si son nuevos (basado en el texto para simplificar)
            const currentLogs = Array.from(logContainer.children).map(e => e.innerText);
            data.logs.forEach(log => {
                if (!currentLogs.includes(log)) {
                    const entry = document.createElement('div');
                    entry.className = 'log-entry ai';
                    entry.innerText = log;
                    logContainer.appendChild(entry);
                    logContainer.scrollTop = logContainer.scrollHeight;
                }
            });

            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }

        // Load Recent Trades
        if (data.recent_trades && data.recent_trades.length > 0) {
            renderTrades(data.recent_trades);
        }

    } catch (error) {
        console.error("Error fetching bot status:", error);
    }
}

function renderTrades(trades) {
    const list = document.getElementById('recent-trades');
    list.innerHTML = trades.map(trade => `
        <div class="trade-item">
            <div class="trade-info-main">
                <span class="trade-asset">${trade.asset}</span>
                <span class="trade-type">${trade.action} • ${trade.strategy}</span>
            </div>
            <div class="trade-result">
                <span class="trade-amount ${trade.result === 'win' ? 'text-positive' : 'text-danger'}">
                    ${trade.result === 'win' ? '+' : '-'}$${Math.abs(trade.profit).toFixed(2)}
                </span>
                <div class="trade-outcome">${trade.result.toUpperCase()}</div>
            </div>
        </div>
    `).join('');
}

// Start polling
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    lucide.createIcons();
    setInterval(fetchBotStatus, 2000); // Cada 2 segundos
});

