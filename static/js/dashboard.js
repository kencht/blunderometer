// Global variables
let moveTypesChart = null;
let statsUpdateInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateStats();
    loadRecentGames();
    loadBlunderAnalysis();
    
    // Auto-refresh every 5 seconds
    statsUpdateInterval = setInterval(updateStats, 5000);
    
    // Initialize chart
    initMoveTypesChart();
});

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Update cards
        document.getElementById('total-games').textContent = data.games.total;
        document.getElementById('total-moves').textContent = data.moves.total;
        document.getElementById('total-blunders').textContent = data.moves.blunders;
        document.getElementById('total-mistakes').textContent = data.moves.mistakes;
        
        // Update progress
        const progress = data.games.analysis_progress;
        document.getElementById('games-progress').style.width = progress + '%';
        document.getElementById('games-progress-text').textContent = 
            Math.round(progress) + '% analyzed (' + data.games.analyzed + '/' + data.games.total + ')';
        
        // Update rates
        document.getElementById('blunder-rate').textContent = data.moves.blunder_rate + '% of moves';
        document.getElementById('mistake-rate').textContent = data.moves.mistake_rate + '% of moves';
        
        // Update unanalyzed count
        document.getElementById('unanalyzed-count').textContent = data.games.unanalyzed + ' games';
        
        // Update dates
        if (data.games.latest_date) {
            document.getElementById('latest-date').textContent = 
                new Date(data.games.latest_date).toLocaleDateString();
        }
        if (data.games.oldest_date) {
            document.getElementById('oldest-date').textContent = 
                new Date(data.games.oldest_date).toLocaleDateString();
        }
        
        // Update last updated time
        document.getElementById('last-updated').textContent = 
            'Last updated: ' + new Date().toLocaleTimeString();
        
        // Update button states based on operation status
        updateButtonStates(data.operation_status);
        
        // Update chart
        updateMoveTypesChart(data.moves);
        
        // Update time controls
        updateTimeControls(data.time_controls);
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update button states
function updateButtonStates(operationStatus) {
    const fetchBtn = document.getElementById('fetch-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    if (operationStatus.fetching) {
        fetchBtn.disabled = true;
        fetchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Fetching...';
        analyzeBtn.disabled = true;
    } else if (operationStatus.analyzing) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Analyzing...';
        fetchBtn.disabled = true;
    } else {
        fetchBtn.disabled = false;
        fetchBtn.innerHTML = '<i class="fas fa-download"></i> Fetch Next Batch';
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-brain"></i> Analyze Unanalyzed';
    }
    
    // Show last operation result
    if (operationStatus.last_operation) {
        const op = operationStatus.last_operation;
        if (op.type === 'fetch') {
            const statusDiv = document.getElementById('fetch-status');
            if (op.error) {
                statusDiv.innerHTML = `<div class="alert alert-danger">${op.error}</div>`;
            } else if (op.result) {
                statusDiv.innerHTML = `<div class="alert alert-success">${op.result}</div>`;
            }
        } else if (op.type === 'analyze') {
            const statusDiv = document.getElementById('analyze-status');
            if (op.error) {
                statusDiv.innerHTML = `<div class="alert alert-danger">${op.error}</div>`;
            } else if (op.result) {
                statusDiv.innerHTML = `<div class="alert alert-success">${op.result}</div>`;
            }
        }
    }
}

// Fetch games
async function fetchGames() {
    const batchSize = document.getElementById('batch-size').value;
    const username = document.getElementById('username').value;
    
    try {
        const response = await fetch('/api/fetch-games', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                batch_size: parseInt(batchSize),
                username: username
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('fetch-status').innerHTML = 
                `<div class="alert alert-info">${data.message}</div>`;
        } else {
            document.getElementById('fetch-status').innerHTML = 
                `<div class="alert alert-danger">${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('fetch-status').innerHTML = 
            `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// Analyze games
async function analyzeGames() {
    const timeLimit = document.getElementById('time-limit').value;
    const username = document.getElementById('username').value;
    
    try {
        const response = await fetch('/api/analyze-games', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                time_limit: parseInt(timeLimit),
                username: username
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('analyze-status').innerHTML = 
                `<div class="alert alert-info">${data.message}</div>`;
        } else {
            document.getElementById('analyze-status').innerHTML = 
                `<div class="alert alert-danger">${data.error}</div>`;
        }
    } catch (error) {
        document.getElementById('analyze-status').innerHTML = 
            `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// Load recent games
async function loadRecentGames() {
    try {
        const response = await fetch('/api/recent-games');
        const games = await response.json();
        
        const tbody = document.getElementById('recent-games');
        tbody.innerHTML = '';
        
        games.forEach(game => {
            const row = document.createElement('tr');
            const date = new Date(game.played_at).toLocaleDateString();
            const statusBadge = game.fully_analyzed 
                ? '<span class="badge status-analyzed">Analyzed</span>'
                : '<span class="badge status-pending">Pending</span>';
            
            row.innerHTML = `
                <td>${date}</td>
                <td class="text-truncate" style="max-width: 150px;" title="${game.opening_name}">${game.opening_name || 'Unknown'}</td>
                <td><i class="fas fa-chess-${game.user_color === 'white' ? 'king' : 'queen'}"></i> ${game.user_color}</td>
                <td>${game.user_rating} vs ${game.opponent_rating}</td>
                <td>${game.time_control}</td>
                <td>${statusBadge}</td>
                <td>
                    ${game.blunders_count > 0 
                        ? `<span class="badge bg-danger">${game.blunders_count}</span>`
                        : game.fully_analyzed ? '0' : '-'
                    }
                </td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error loading recent games:', error);
    }
}

// Initialize move types chart
function initMoveTypesChart() {
    const ctx = document.getElementById('moveTypesChart').getContext('2d');
    moveTypesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Good Moves', 'Inaccuracies', 'Mistakes', 'Blunders'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#28a745',
                    '#ffc107',
                    '#fd7e14',
                    '#dc3545'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        fontSize: 12,
                        padding: 10
                    }
                }
            }
        }
    });
}

// Update move types chart
function updateMoveTypesChart(movesData) {
    if (!moveTypesChart) return;
    
    const goodMoves = movesData.total - movesData.inaccuracies;
    const inaccuraciesOnly = movesData.inaccuracies - movesData.mistakes;
    const mistakesOnly = movesData.mistakes - movesData.blunders;
    
    moveTypesChart.data.datasets[0].data = [
        goodMoves,
        inaccuraciesOnly,
        mistakesOnly,
        movesData.blunders
    ];
    moveTypesChart.update();
}

// Update time controls
function updateTimeControls(timeControls) {
    const container = document.getElementById('time-controls');
    if (timeControls.length === 0) {
        container.innerHTML = 'No data available';
        return;
    }
    
    container.innerHTML = '';
    timeControls.forEach(tc => {
        const div = document.createElement('div');
        div.className = 'd-flex justify-content-between';
        div.innerHTML = `
            <span>${tc.name}</span>
            <span class="badge bg-secondary">${tc.count}</span>
        `;
        container.appendChild(div);
    });
}

// Load blunder analysis
async function loadBlunderAnalysis() {
    try {
        const response = await fetch('/api/blunder-analysis');
        const data = await response.json();
        
        // Update recent blunders
        const container = document.getElementById('recent-blunders');
        container.innerHTML = '';
        
        if (data.recent_blunders.length === 0) {
            container.innerHTML = 'No blunders yet';
            return;
        }
        
        data.recent_blunders.slice(0, 5).forEach(blunder => {
            const div = document.createElement('div');
            div.className = 'blunder-item';
            const date = new Date(blunder.played_at).toLocaleDateString();
            div.innerHTML = `
                <strong>${blunder.move_san}</strong> (${blunder.centipawn_loss}cp)<br>
                <small class="text-muted">${blunder.opening_name} - ${date}</small>
            `;
            container.appendChild(div);
        });
        
    } catch (error) {
        console.error('Error loading blunder analysis:', error);
    }
}

// Refresh data manually
function refreshData() {
    updateStats();
    loadRecentGames();
    loadBlunderAnalysis();
}
