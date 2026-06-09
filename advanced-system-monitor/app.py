"""Flask web application for MyProject"""
from flask import Flask, jsonify, render_template_string, session, redirect, url_for, request
from functools import wraps
from core.logger import setup_logger
from subsystems.network import NetworkManager
from subsystems.sysstat import SystemStats

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
logger = setup_logger(__name__)

# Hardcoded credentials
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'pass'

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login page HTML template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MyProject - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; border-radius: 10px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: bold; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 5px rgba(102, 126, 234, 0.3); }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #764ba2; }
        .error { color: #721c24; background: #f8d7da; padding: 10px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #f5c6cb; }
        .hint { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔐 MyProject Login</h1>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit">Login</button>
        </form>
        
        <div class="hint">
            <p><strong>Demo Credentials:</strong></p>
            <p>Username: <code>admin</code></p>
            <p>Password: <code>pass</code></p>
        </div>
    </div>
</body>
</html>
"""

# Comprehensive Dashboard Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MyProject - Advanced System Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; color: white; }
        h1 { font-size: 32px; }
        .logout-btn { background: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; text-decoration: none; transition: 0.3s; }
        .logout-btn:hover { background: #c82333; }
        
        .card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }
        .card h2 { color: #333; margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        .card h3 { color: #555; margin-top: 20px; margin-bottom: 15px; }
        
        .tabs { display: flex; gap: 5px; margin-bottom: 20px; border-bottom: 2px solid #ddd; flex-wrap: wrap; }
        .tab-btn { background: #f0f0f0; border: none; padding: 12px 20px; cursor: pointer; border-radius: 5px 5px 0 0; font-size: 13px; font-weight: bold; color: #333; transition: all 0.3s; }
        .tab-btn:hover { background: #e0e0e0; }
        .tab-btn.active { background: #667eea; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .info-box { padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; }
        .info-box strong { color: #667eea; display: block; margin-bottom: 5px; font-size: 14px; }
        .info-box span { color: #555; font-size: 16px; font-weight: 500; }
        
        .progress-bar { background: #e0e0e0; height: 25px; border-radius: 10px; overflow: hidden; margin-top: 8px; }
        .progress-fill { background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold; }
        
        .alert { padding: 15px; border-radius: 5px; margin-bottom: 15px; }
        .alert.warning { background: #fff3cd; color: #856404; border: 1px solid #ffc107; }
        .alert.danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert.info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        
        .button { display: inline-block; background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 14px; margin: 5px; transition: 0.3s; }
        .button:hover { background: #764ba2; }
        .button.small { padding: 8px 15px; font-size: 12px; }
        
        .process-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .process-table th { background: #667eea; color: white; padding: 12px; text-align: left; }
        .process-table td { padding: 10px; border-bottom: 1px solid #ddd; }
        .process-table tr:hover { background: #f5f5f5; }
        
        .chart-container { position: relative; height: 300px; margin: 20px 0; }
        .loading { color: #667eea; font-style: italic; }
        .error { color: #721c24; background: #f8d7da; padding: 12px; border-radius: 5px; border: 1px solid #f5c6cb; }
        
        .stat-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        @media (max-width: 1200px) { .stat-row { grid-template-columns: 1fr 1fr; } }
        
        .icon { margin-right: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Advanced System Monitor</h1>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        
        <!-- Alerts Section -->
        <div class="card" id="alerts-section" style="display: none;">
            <h2>⚠️ System Alerts</h2>
            <div id="alerts-list"></div>
        </div>
        
        <!-- Main Dashboard Card -->
        <div class="card">
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('dashboard')">📊 Dashboard</button>
                <button class="tab-btn" onclick="switchTab('cpu')">⚙️ CPU</button>
                <button class="tab-btn" onclick="switchTab('memory')">💾 Memory</button>
                <button class="tab-btn" onclick="switchTab('disk')">💿 Disk</button>
                <button class="tab-btn" onclick="switchTab('network')">🌐 Network</button>
                <button class="tab-btn" onclick="switchTab('hardware')">🔧 Hardware</button>
                <button class="tab-btn" onclick="switchTab('system')">ℹ️ System</button>
            </div>
            
            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <h2>System Dashboard</h2>
                <button class="button" onclick="loadDashboard()">Refresh Dashboard</button>
                
                <div class="stat-row" style="margin-top: 20px;">
                    <div class="info-box">
                        <strong>🔴 CPU Usage</strong>
                        <div id="cpu-usage-display" class="loading">Loading...</div>
                    </div>
                    <div class="info-box">
                        <strong>🟡 Memory Usage</strong>
                        <div id="memory-usage-display" class="loading">Loading...</div>
                    </div>
                    <div class="info-box">
                        <strong>🟠 Disk Usage</strong>
                        <div id="disk-usage-display" class="loading">Loading...</div>
                    </div>
                    <div class="info-box">
                        <strong>🟢 Network Status</strong>
                        <div id="network-status-display" class="loading">Loading...</div>
                    </div>
                </div>
            </div>
            
            <!-- CPU Tab -->
            <div id="cpu" class="tab-content">
                <h2>CPU Information</h2>
                <button class="button" onclick="fetchCPUInfo()">Refresh CPU Info</button>
                <div id="cpu-info" class="loading">Loading...</div>
                <div class="chart-container" id="cpu-chart-container"></div>
            </div>
            
            <!-- Memory Tab -->
            <div id="memory" class="tab-content">
                <h2>Memory Information</h2>
                <button class="button" onclick="fetchMemoryInfo()">Refresh Memory Info</button>
                <div id="memory-info" class="loading">Loading...</div>
                <div class="chart-container" id="memory-chart-container"></div>
            </div>
            
            <!-- Disk Tab -->
            <div id="disk" class="tab-content">
                <h2>Disk Information</h2>
                <button class="button" onclick="fetchDiskInfo()">Refresh Disk Info</button>
                <div id="disk-info" class="loading">Loading...</div>
            </div>
            
            <!-- Network Tab -->
            <div id="network" class="tab-content">
                <h2>Network Information</h2>
                <button class="button" onclick="fetchNetworkInfo()">Refresh Network Info</button>
                <div id="network-info" class="loading">Loading...</div>
            </div>
            
            <!-- Hardware Tab -->
            <div id="hardware" class="tab-content">
                <h2>Hardware Information</h2>
                <button class="button" onclick="fetchHardwareInfo()">Refresh Hardware Info</button>
                
                <h3>Battery Status</h3>
                <div id="battery-info" class="loading">Loading...</div>
                
                <h3>GPU Information</h3>
                <div id="gpu-info" class="loading">Loading...</div>
            </div>
            
            <!-- System Tab -->
            <div id="system" class="tab-content">
                <h2>System Information</h2>
                <button class="button" onclick="fetchSystemInfo()">Refresh System Info</button>
                <div id="system-info" class="loading">Loading...</div>
            </div>
        </div>
    </div>

    <script>
        let cpuChart, memoryChart;
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'dashboard') loadDashboard();
            else if (tabName === 'cpu') fetchCPUInfo();
            else if (tabName === 'memory') fetchMemoryInfo();
            else if (tabName === 'disk') fetchDiskInfo();
            else if (tabName === 'network') fetchNetworkInfo();
            else if (tabName === 'hardware') fetchHardwareInfo();
            else if (tabName === 'system') fetchSystemInfo();
        }
        
        function loadDashboard() {
            fetchCPUInfo();
            fetchMemoryInfo();
            fetchDiskInfo();
            fetchNetworkStatus();
            // Only fetch processes and alerts on demand (not every 30 seconds)
            // to reduce memory usage
        }
        
        function fetchSystemAlerts() {
            fetch('/api/system-alerts')
                .then(r => r.json())
                .then(data => {
                    const alertsSection = document.getElementById('alerts-section');
                    const alertsList = document.getElementById('alerts-list');
                    
                    if (data.alerts && data.alerts.length > 0) {
                        alertsSection.style.display = 'block';
                        alertsList.innerHTML = data.alerts.map(a => 
                            `<div class="alert ${a.type}">${a.message}</div>`
                        ).join('');
                    } else {
                        alertsSection.style.display = 'none';
                    }
                });
        }
        
        function fetchCPUInfo() {
            const div = document.getElementById('cpu-info');
            div.innerHTML = '<p class="loading">Loading...</p>';
            
            fetch('/api/cpu-info')
                .then(r => r.json())
                .then(data => {
                    if (!data.success) throw new Error(data.error);
                    const c = data.data;
                    let html = '<div class="grid">';
                    html += `<div class="info-box"><strong>Physical Cores:</strong> <span>${c.physical_cores}</span></div>`;
                    html += `<div class="info-box"><strong>Logical Cores:</strong> <span>${c.total_cores}</span></div>`;
                    html += `<div class="info-box"><strong>Frequency:</strong> <span>${c.cpu_freq} MHz</span></div>`;
                    html += `<div class="info-box"><strong>Load Average:</strong> <span>${Array.isArray(c.load_average) ? c.load_average.join(', ') : 'N/A'}</span></div>`;
                    html += '</div>';
                    
                    html += '<h3>Overall CPU Usage</h3>';
                    html += `<div class="info-box">
                        <div class="progress-bar"><div class="progress-fill" style="width: ${c.cpu_percent}%">${c.cpu_percent}%</div></div>
                    </div>`;
                    
                    html += '<h3>Per-Core Usage</h3><div class="grid">';
                    c.per_core_percent.forEach((p, i) => {
                        html += `<div class="info-box"><strong>Core ${i}:</strong>
                            <div class="progress-bar"><div class="progress-fill" style="width: ${p}%">${p}%</div></div>
                        </div>`;
                    });
                    html += '</div>';
                    
                    div.innerHTML = html;
                    document.getElementById('cpu-usage-display').innerHTML = `<span>${c.cpu_percent}%</span><div class="progress-bar"><div class="progress-fill" style="width: ${c.cpu_percent}%"></div></div>`;
                })
                .catch(e => div.innerHTML = `<div class="error">Error: ${e.message}</div>`);
        }
        
        function fetchMemoryInfo() {
            const div = document.getElementById('memory-info');
            div.innerHTML = '<p class="loading">Loading...</p>';
            
            fetch('/api/memory-info')
                .then(r => r.json())
                .then(data => {
                    if (!data.success) throw new Error(data.error);
                    const m = data.data;
                    let html = '<div class="grid">';
                    html += `<div class="info-box"><strong>Total:</strong> <span>${m.total} ${m.unit}</span></div>`;
                    html += `<div class="info-box"><strong>Used:</strong> <span>${m.used} ${m.unit}</span></div>`;
                    html += `<div class="info-box"><strong>Available:</strong> <span>${m.available} ${m.unit}</span></div>`;
                    html += `<div class="info-box"><strong>Usage:</strong> <span>${m.percent}%</span></div>`;
                    html += '</div>';
                    
                    html += '<h3>Memory Usage</h3>';
                    html += `<div class="info-box"><div class="progress-bar"><div class="progress-fill" style="width: ${m.percent}%">${m.percent}%</div></div></div>`;
                    
                    html += '<h3>Swap Memory</h3><div class="grid">';
                    html += `<div class="info-box"><strong>Total:</strong> <span>${m.swap_total} ${m.unit}</span></div>`;
                    html += `<div class="info-box"><strong>Used:</strong> <span>${m.swap_used} ${m.unit}</span></div>`;
                    html += `<div class="info-box"><strong>Usage:</strong> <span>${m.swap_percent}%</span></div>`;
                    html += `<div class="info-box"><div class="progress-bar"><div class="progress-fill" style="width: ${m.swap_percent}%">${m.swap_percent}%</div></div></div>`;
                    html += '</div>';
                    
                    div.innerHTML = html;
                    document.getElementById('memory-usage-display').innerHTML = `<span>${m.percent}%</span><div class="progress-bar"><div class="progress-fill" style="width: ${m.percent}%"></div></div>`;
                })
                .catch(e => div.innerHTML = `<div class="error">Error: ${e.message}</div>`);
        }
        
        function fetchDiskInfo() {
            const div = document.getElementById('disk-info');
            div.innerHTML = '<p class="loading">Loading...</p>';
            
            fetch('/api/disk-info')
                .then(r => r.json())
                .then(data => {
                    if (!data.success) throw new Error(data.error);
                    let html = '';
                    for (const [dev, info] of Object.entries(data.data)) {
                        html += `<div style="margin-bottom: 20px;">
                            <h4>${dev} - ${info.mountpoint} (${info.fstype})</h4>
                            <div class="grid">
                                <div class="info-box"><strong>Total:</strong> <span>${info.total} ${info.unit}</span></div>
                                <div class="info-box"><strong>Used:</strong> <span>${info.used} ${info.unit}</span></div>
                                <div class="info-box"><strong>Free:</strong> <span>${info.free} ${info.unit}</span></div>
                                <div class="info-box"><strong>Usage:</strong> <span>${info.percent}%</span></div>
                            </div>
                            <div class="progress-bar"><div class="progress-fill" style="width: ${info.percent}%">${info.percent}%</div></div>
                        </div>`;
                    }
                    div.innerHTML = html;
                })
                .catch(e => div.innerHTML = `<div class="error">Error: ${e.message}</div>`);
        }
        
        function fetchNetworkInfo() {
            const div = document.getElementById('network-info');
            div.innerHTML = '<p class="loading">Loading...</p>';
            
            fetch('/api/network-info')
                .then(r => r.json())
                .then(data => {
                    if (!data.success) throw new Error(data.error);
                    let html = '<h3>Network Statistics</h3>';
                    const stats = data.data.statistics;
                    html += '<div class="grid">';
                    html += `<div class="info-box"><strong>Total Bytes Sent:</strong> <span>${stats.total_bytes_sent}</span></div>`;
                    html += `<div class="info-box"><strong>Total Bytes Received:</strong> <span>${stats.total_bytes_recv}</span></div>`;
                    html += `<div class="info-box"><strong>Total Packets Sent:</strong> <span>${stats.total_packets_sent}</span></div>`;
                    html += `<div class="info-box"><strong>Total Packets Received:</strong> <span>${stats.total_packets_recv}</span></div>`;
                    html += '</div>';
                    
                    html += '<h3>Network Interfaces</h3>';
                    for (const [iface, info] of Object.entries(data.data.interfaces)) {
                        html += `<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h4>🔌 ${iface}</h4>
                            <div class="grid">
                                <div class="info-box"><strong>Status:</strong> <span>${info.status}</span></div>
                                <div class="info-box"><strong>Speed:</strong> <span>${info.speed || 'N/A'}</span></div>
                                <div class="info-box"><strong>MTU:</strong> <span>${info.mtu}</span></div>
                            </div>`;
                        
                        if (info.addresses.length > 0) {
                            html += '<strong style="display: block; margin-top: 10px;">IP Addresses:</strong>';
                            info.addresses.forEach(a => {
                                html += `<div style="padding: 8px; background: white; margin: 5px 0; border-radius: 4px;">
                                    <strong>${a.family}:</strong> ${a.address}${a.netmask ? ' / ' + a.netmask : ''}
                                </div>`;
                            });
                        }
                        html += '</div>';
                    }
                    div.innerHTML = html;
                })
                .catch(e => div.innerHTML = `<div class="error">Error: ${e.message}</div>`);
        }
        
        function fetchHardwareInfo() {
            fetchBatteryInfo();
            fetchGPUInfo();
        }
        
        
        function fetchBatteryInfo() {
            const div = document.getElementById('battery-info');
            div.innerHTML = '<p class="loading">Loading...</p>';
            
            fetch('/api/battery-info')
                .then(r => r.json())
                .then(data => {
                    if (data.info) {
                        div.innerHTML = `<div class="alert info">${data.info}</div>`;
                        return;
                    }
                    
                    const batteryClass = data.is_charging ? 'success' : 'warning';
                    let html = `<div class="alert ${batteryClass}"><strong>${data.status}</strong></div>`;
                    html += '<div class="grid">';
                    html += `<div class="info-box"><strong>Level:</strong> <span>${data.percent}%</span><div class="progress-bar"><div class="progress-fill" style="width: ${data.percent}%"></div></div></div>`;
                    html += `<div class="info-box"><strong>Time Left:</strong> <span>${data.time_left}</span></div>`;
                    html += '</div>';
                    div.innerHTML = html;
                })
                .catch(e => div.innerHTML = `<div class="error">Error: ${e.message}</div>`);
        }
        
        function fetchGPUInfo() {
            const div = document.getElementById('gpu-info');
            div.innerHTML = '<p class="loading">Loading...</p>';
            
            fetch('/api/gpu-info')
                .then(r => r.json())
                .then(data => {
                    if (data.info) {
                        div.innerHTML = `<div class="alert info">${data.info}</div>`;
                        return;
                    }
                    
                    let html = '';
                    for (const [gpu, info] of Object.entries(data)) {
                        html += `<h4>${info.name}</h4><div class="grid">`;
                        html += `<div class="info-box"><strong>Load:</strong> <span>${info.load}%</span><div class="progress-bar"><div class="progress-fill" style="width: ${info.load}%"></div></div></div>`;
                        html += `<div class="info-box"><strong>Memory:</strong> <span>${info.memory_used} / ${info.memory_total}</span><div class="progress-bar"><div class="progress-fill" style="width: ${info.memory_percent}%"></div></div></div>`;
                        html += `<div class="info-box"><strong>Temperature:</strong> <span>${info.temperature}</span></div>`;
                        html += '</div>';
                    }
                    div.innerHTML = html || '<div class="alert info">No GPU data available</div>';
                })
                .catch(e => div.innerHTML = `<div class="error">Error: ${e.message}</div>`);
        }
        
        
        function fetchSystemInfo() {
            const div = document.getElementById('system-info');
            div.innerHTML = '<p class="loading">Loading...</p>';
            
            Promise.all([
                fetch('/api/system-info').then(r => r.json()),
                fetch('/api/uptime-info').then(r => r.json())
            ]).then(([sysData, uptimeData]) => {
                let html = '<div class="grid">';
                
                for (const [k, v] of Object.entries(sysData.data)) {
                    html += `<div class="info-box"><strong>${k}:</strong> <span>${v}</span></div>`;
                }
                
                if (!uptimeData.error) {
                    for (const [k, v] of Object.entries(uptimeData)) {
                        if (k !== 'error') {
                            html += `<div class="info-box"><strong>${k}:</strong> <span>${v}</span></div>`;
                        }
                    }
                }
                
                html += '</div>';
                div.innerHTML = html;
            }).catch(e => div.innerHTML = `<div class="error">Error: ${e.message}</div>`);
        }
        
        function fetchNetworkStatus() {
            fetch('/api/network-status')
                .then(r => r.json())
                .then(data => {
                    const status = data.connected ? '✓ Connected' : '✗ Disconnected';
                    document.getElementById('network-status-display').innerHTML = `<span>${status}</span>`;
                })
                .catch(e => document.getElementById('network-status-display').innerHTML = `<div class="error">Error</div>`);
        }
        
        window.onload = loadDashboard;
        // Auto-refresh every 30 seconds instead of 10 to reduce memory
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Display the main dashboard"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['user'] = username
            logger.info(f"User {username} logged in successfully")
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'
            logger.warning(f"Failed login attempt with username: {username}")
    
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    """Logout the user"""
    user = session.pop('user', None)
    if user:
        logger.info(f"User {user} logged out")
    return redirect(url_for('login'))

@app.route('/api/system-info')
@login_required
def get_system_info():
    """API endpoint for system information"""
    try:
        sys_info = SystemStats.get_system_info()
        return jsonify({'success': True, 'data': sys_info})
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/uptime-info')
@login_required
def get_uptime_info():
    """API endpoint for uptime information"""
    try:
        return jsonify(SystemStats.get_uptime_info())
    except Exception as e:
        logger.error(f"Failed to get uptime info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cpu-info')
@login_required
def get_cpu_info():
    """API endpoint for CPU information"""
    try:
        cpu_info = SystemStats.get_cpu_info()
        if 'error' in cpu_info:
            return jsonify({'success': False, 'error': cpu_info['error']}), 500
        return jsonify({'success': True, 'data': cpu_info})
    except Exception as e:
        logger.error(f"Failed to get CPU info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memory-info')
@login_required
def get_memory_info():
    """API endpoint for memory information"""
    try:
        memory_info = SystemStats.get_memory_info()
        if 'error' in memory_info:
            return jsonify({'success': False, 'error': memory_info['error']}), 500
        return jsonify({'success': True, 'data': memory_info})
    except Exception as e:
        logger.error(f"Failed to get memory info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/disk-info')
@login_required
def get_disk_info():
    """API endpoint for disk information"""
    try:
        disk_info = SystemStats.get_disk_info()
        if 'error' in disk_info:
            return jsonify({'success': False, 'error': disk_info['error']}), 500
        return jsonify({'success': True, 'data': disk_info})
    except Exception as e:
        logger.error(f"Failed to get disk info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/network-info')
@login_required
def get_network_info():
    """API endpoint for network information"""
    try:
        network_info = SystemStats.get_network_info()
        if 'error' in network_info:
            return jsonify({'success': False, 'error': network_info['error']}), 500
        return jsonify({'success': True, 'data': network_info})
    except Exception as e:
        logger.error(f"Failed to get network info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/network-status')
@login_required
def get_network_status():
    """API endpoint for network connectivity check"""
    try:
        network_mgr = NetworkManager("8.8.8.8", 53, timeout=5)
        is_connected = network_mgr.check_connection()
        return jsonify({'connected': is_connected, 'server': '8.8.8.8', 'port': 53})
    except Exception as e:
        logger.error(f"Network test failed: {e}")
        return jsonify({'connected': False, 'error': str(e)}), 500

@app.route('/api/temperature-info')
@login_required
def get_temperature_info():
    """API endpoint for temperature information"""
    try:
        return jsonify(SystemStats.get_temperature_info())
    except Exception as e:
        logger.error(f"Failed to get temperature info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/battery-info')
@login_required
def get_battery_info():
    """API endpoint for battery information"""
    try:
        return jsonify(SystemStats.get_battery_info())
    except Exception as e:
        logger.error(f"Failed to get battery info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gpu-info')
@login_required
def get_gpu_info():
    """API endpoint for GPU information"""
    try:
        return jsonify(SystemStats.get_gpu_info())
    except Exception as e:
        logger.error(f"Failed to get GPU info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-processes')
@login_required
def get_top_processes():
    """API endpoint for top processes"""
    try:
        processes = SystemStats.get_top_processes(sort_by='cpu', limit=10)
        return jsonify({'processes': processes})
    except Exception as e:
        logger.error(f"Failed to get top processes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-alerts')
@login_required
def get_system_alerts():
    """API endpoint for system alerts"""
    try:
        alerts = SystemStats.get_system_alerts()
        return jsonify({'alerts': alerts})
    except Exception as e:
        logger.error(f"Failed to get system alerts: {e}")
        return jsonify({'alerts': []}), 200

if __name__ == '__main__':
    logger.info("Starting Flask web server...")
    # Enable debug mode for development
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)
