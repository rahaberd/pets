/* ================================================================
   QUANT PORTFOLIO — Frontend Logic
   ================================================================ */

'use strict';

// ================================================================
// Tab Navigation
// ================================================================

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;

    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(`panel-${tab}`).classList.add('active');
  });
});


// ================================================================
// Utilities
// ================================================================

function showResult(boxId, value) {
  const box = document.getElementById(boxId);
  box.innerHTML = `<span class="result-value">${formatLargeNumber(value)}</span>`;
}

function showError(boxId, msg) {
  const box = document.getElementById(boxId);
  box.innerHTML = `<span class="result-error">${msg}</span>`;
}

function formatLargeNumber(n) {
  if (typeof n !== 'number' && typeof n !== 'bigint') return n;
  const s = n.toString();
  // If the number is very large, just format with commas
  if (s.length > 30) return s;
  return n.toLocaleString();
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Unknown error');
  return data;
}


// ================================================================
// Factorial
// ================================================================

async function calcFactorial() {
  const n = document.getElementById('fact-n').value.trim();
  if (n === '') { showError('fact-result', 'Please enter a value for n.'); return; }

  try {
    const data = await postJSON('/api/math/factorial/', { n: parseInt(n, 10) });
    showResult('fact-result', data.result);
  } catch (e) {
    showError('fact-result', e.message);
  }
}


// ================================================================
// Combination
// ================================================================

async function calcCombination() {
  const n = document.getElementById('comb-n').value.trim();
  const k = document.getElementById('comb-k').value.trim();
  if (!n || !k) { showError('comb-result', 'Please enter values for both n and k.'); return; }

  try {
    const data = await postJSON('/api/math/combination/', {
      n: parseInt(n, 10),
      k: parseInt(k, 10),
    });
    showResult('comb-result', data.result);
  } catch (e) {
    showError('comb-result', e.message);
  }
}


// ================================================================
// Permutations
// ================================================================

async function calcPermutations() {
  const word = document.getElementById('perm-word').value.trim();
  if (!word) { showError('perm-result', 'Please enter a word.'); return; }

  try {
    const data = await postJSON('/api/math/permutations/', { word });
    showResult('perm-result', data.result);
  } catch (e) {
    showError('perm-result', e.message);
  }
}


// ================================================================
// Combination Product
// ================================================================

function addPair() {
  const container = document.getElementById('pair-list');
  const row = document.createElement('div');
  row.className = 'pair-row';
  row.innerHTML = `
    <div class="pair-inputs">
      <div class="form-field">
        <label>n</label>
        <input type="number" class="pair-n" min="0" placeholder="n" />
      </div>
      <div class="form-field">
        <label>k</label>
        <input type="number" class="pair-k" min="0" placeholder="k" />
      </div>
    </div>
    <button class="btn-remove" onclick="removePair(this)" title="Remove">&#x2715;</button>
  `;
  container.appendChild(row);
}

function removePair(btn) {
  const rows = document.querySelectorAll('#pair-list .pair-row');
  if (rows.length === 1) return; // keep at least one
  btn.closest('.pair-row').remove();
}

async function calcCombProduct() {
  const pairs = [];
  let valid = true;

  document.querySelectorAll('#pair-list .pair-row').forEach(row => {
    const n = row.querySelector('.pair-n').value.trim();
    const k = row.querySelector('.pair-k').value.trim();
    if (n === '' || k === '') valid = false;
    else pairs.push({ n: parseInt(n, 10), k: parseInt(k, 10) });
  });

  if (!valid || pairs.length === 0) {
    showError('prod-result', 'Please fill in all n and k values.');
    return;
  }

  try {
    const data = await postJSON('/api/math/combination-product/', { pairs });
    showResult('prod-result', data.result);
  } catch (e) {
    showError('prod-result', e.message);
  }
}


// ================================================================
// Backtest Engine
// ================================================================

let equityChart = null;

async function runBacktest() {
  const ticker    = document.getElementById('bt-ticker').value.trim().toUpperCase();
  const startDate = document.getElementById('bt-start').value;
  const endDate   = document.getElementById('bt-end').value;
  const window_   = parseInt(document.getElementById('bt-window').value, 10);
  const zThresh   = parseFloat(document.getElementById('bt-zthresh').value);

  const errEl = document.getElementById('bt-error');
  errEl.style.display = 'none';

  if (!ticker) { showBtError('Ticker is required.'); return; }
  if (!startDate || !endDate) { showBtError('Please select start and end dates.'); return; }
  if (startDate >= endDate) { showBtError('Start date must be before end date.'); return; }

  const resultsWrap = document.getElementById('bt-results');
  const loadingEl   = document.getElementById('bt-loading');
  const outputEl    = document.getElementById('bt-output');
  const runBtn      = document.getElementById('bt-run-btn');

  resultsWrap.style.display = 'block';
  loadingEl.style.display   = 'flex';
  outputEl.style.display    = 'none';
  runBtn.disabled = true;
  runBtn.textContent = 'Running\u2026';

  try {
    const data = await postJSON('/api/backtest/run/', {
      ticker,
      start_date: startDate,
      end_date: endDate,
      window: window_,
      z_threshold: zThresh,
    });

    renderBacktestResults(data);

  } catch (e) {
    loadingEl.style.display = 'none';
    showBtError(e.message);
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = 'Run Backtest';
  }
}

function showBtError(msg) {
  const el = document.getElementById('bt-error');
  el.textContent = msg;
  el.style.display = 'block';
}

function renderBacktestResults(data) {
  const loadingEl = document.getElementById('bt-loading');
  const outputEl  = document.getElementById('bt-output');

  loadingEl.style.display = 'none';
  outputEl.style.display  = 'block';

  // ---- Metrics
  const mRet  = data.market_cumulative_return;
  const sRet  = data.strategy_cumulative_return;
  const mShrp = data.market_sharpe;
  const sShrp = data.strategy_sharpe;

  document.getElementById('bt-metrics').innerHTML = `
    ${metricCard('Market Return', formatPct(mRet), colorClass(mRet))}
    ${metricCard('Strategy Return', formatPct(sRet), colorClass(sRet))}
    ${metricCard('Market Sharpe', mShrp.toFixed(2), sharpeColor(mShrp))}
    ${metricCard('Strategy Sharpe', sShrp.toFixed(2), sharpeColor(sShrp))}
  `;

  // ---- Chart
  document.getElementById('bt-chart-title').textContent =
    `${data.ticker} \u2022 ${data.start_date} \u2013 ${data.end_date}`;

  renderEquityChart(data.chart.dates, data.chart.market, data.chart.strategy);
}

function metricCard(label, value, cls) {
  return `
    <div class="metric-card">
      <div class="metric-label">${label}</div>
      <div class="metric-value ${cls}">${value}</div>
    </div>
  `;
}

function formatPct(val) {
  const sign = val >= 0 ? '+' : '';
  return `${sign}${(val * 100).toFixed(2)}%`;
}

function colorClass(val) {
  if (val > 0) return 'positive';
  if (val < 0) return 'negative';
  return 'neutral';
}

function sharpeColor(val) {
  if (val >= 1) return 'positive';
  if (val < 0) return 'negative';
  return 'neutral';
}

function renderEquityChart(dates, market, strategy) {
  const ctx = document.getElementById('bt-chart').getContext('2d');

  if (equityChart) {
    equityChart.destroy();
    equityChart = null;
  }

  // Subsample dates for the X-axis labels to avoid crowding
  const tickCount = 10;
  const step = Math.max(1, Math.floor(dates.length / tickCount));

  equityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: 'Market (Buy & Hold)',
          data: market,
          borderColor: '#58a6ff',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.1,
          fill: false,
        },
        {
          label: 'Strategy',
          data: strategy,
          borderColor: '#3fb950',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.1,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#8b949e',
            usePointStyle: true,
            pointStyle: 'line',
            padding: 20,
            font: { size: 12 },
          },
        },
        tooltip: {
          backgroundColor: '#21262d',
          borderColor: '#30363d',
          borderWidth: 1,
          titleColor: '#e6edf3',
          bodyColor: '#8b949e',
          callbacks: {
            label: ctx => {
              const val = ctx.parsed.y;
              const pct = ((val - 1) * 100).toFixed(2);
              const sign = pct >= 0 ? '+' : '';
              return ` ${ctx.dataset.label}: ${val.toFixed(4)}x (${sign}${pct}%)`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { color: '#21262d' },
          ticks: {
            color: '#6e7681',
            maxTicksLimit: tickCount,
            maxRotation: 0,
            font: { size: 11 },
          },
        },
        y: {
          grid: { color: '#21262d' },
          ticks: {
            color: '#6e7681',
            font: { size: 11 },
            callback: val => `${val.toFixed(2)}x`,
          },
          title: {
            display: true,
            text: 'Cumulative Growth (1x = initial investment)',
            color: '#6e7681',
            font: { size: 11 },
          },
        },
      },
    },
  });
}


// ================================================================
// Enter key support for math inputs
// ================================================================

document.getElementById('fact-n').addEventListener('keydown', e => { if (e.key === 'Enter') calcFactorial(); });
document.getElementById('comb-n').addEventListener('keydown', e => { if (e.key === 'Enter') calcCombination(); });
document.getElementById('comb-k').addEventListener('keydown', e => { if (e.key === 'Enter') calcCombination(); });
document.getElementById('perm-word').addEventListener('keydown', e => { if (e.key === 'Enter') calcPermutations(); });
