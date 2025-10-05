// Global function to test access from any form
async function testAccess(initiator, target, resultElementId) {
    console.log('Testing access:', initiator, '→', target);
    
    if (!initiator || !target) {
        alert('Please select both initiator and target');
        return;
    }

    try {
        const response = await fetch('/api/request_access', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                initiator: initiator,
                target: target,
                access_type: 'read'
            })
        });
        
        const result = await response.json();
        console.log('Server response:', result);
        
        const resultDiv = document.getElementById(resultElementId);
        if (resultDiv) {
            if (result.granted) {
                resultDiv.className = 'access-granted';
                resultDiv.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">✅</span>
                        <div>
                            <strong style="font-size: 16px;">ACCESS GRANTED</strong><br>
                            <span style="font-size: 14px;">${result.message}</span><br>
                            <small>${new Date(result.timestamp).toLocaleString()}</small>
                        </div>
                    </div>
                `;
            } else {
                resultDiv.className = 'access-denied';
                resultDiv.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">❌</span>
                        <div>
                            <strong style="font-size: 16px;">ACCESS DENIED</strong><br>
                            <span style="font-size: 14px;">${result.message}</span><br>
                            <small>${new Date(result.timestamp).toLocaleString()}</small>
                        </div>
                    </div>
                `;
            }
            
            // Make sure the result div is visible
            resultDiv.style.display = 'block';
            resultDiv.style.opacity = '1';
            
            // Refresh access log if on dashboard
            if (window.location.pathname === '/dashboard') {
                setTimeout(loadAccessLog, 500);
            }
        } else {
            console.error('Result element not found:', resultElementId);
        }
    } catch (error) {
        console.error('Access test failed:', error);
        const resultDiv = document.getElementById(resultElementId);
        if (resultDiv) {
            resultDiv.className = 'access-denied';
            resultDiv.innerHTML = `❌ <strong>ERROR</strong><br>Failed to test access: ${error}`;
            resultDiv.style.display = 'block';
        }
    }
}

// Toggle emergency mode
async function toggleEmergencyMode() {
    const currentMode = document.querySelector('.emergency-btn').textContent.includes('Activate');
    const action = currentMode ? 'ACTIVATING' : 'DEACTIVATING';
    
    if (currentMode && !confirm('⚠️ Are you sure you want to activate EMERGENCY MODE? This will grant Admin full access to all zones.')) {
        return;
    }
    
    try {
        const button = document.querySelector('.emergency-btn');
        button.textContent = 'Loading...';
        button.disabled = true;
        
        const response = await fetch('/api/emergency_mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                activate: currentMode
            })
        });
        
        const result = await response.json();
        
        // Update emergency mode display
        const statusElement = document.querySelector('.status-value.emergency, .status-value.normal');
        if (statusElement) {
            statusElement.textContent = result.emergency_mode ? 'ACTIVE' : 'INACTIVE';
            statusElement.className = result.emergency_mode ? 'status-value emergency' : 'status-value normal';
        }
        
        // Update button
        button.textContent = result.emergency_mode ? 'Deactivate Emergency' : 'Activate Emergency';
        button.disabled = false;
        
        // Show visual feedback
        if (result.emergency_mode) {
            document.querySelector('.status-card').classList.add('emergency-pulse');
        } else {
            document.querySelector('.status-card').classList.remove('emergency-pulse');
        }
        
        alert(`🛡️ EMERGENCY MODE ${result.emergency_mode ? 'ACTIVATED' : 'DEACTIVATED'}\n\n${result.message}`);
        
        // Refresh access log
        if (window.location.pathname === '/dashboard') {
            setTimeout(loadAccessLog, 1000);
        }
    } catch (error) {
        alert('Error toggling emergency mode: ' + error);
        const button = document.querySelector('.emergency-btn');
        button.textContent = currentMode ? 'Activate Emergency' : 'Deactivate Emergency';
        button.disabled = false;
    }
}

// Load access log
async function loadAccessLog() {
    try {
        const response = await fetch('/api/access_log');
        const logs = await response.json();
        
        const logContainer = document.getElementById('accessLog');
        if (logContainer) {
            if (logs.length === 0) {
                logContainer.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">No access attempts yet. Try testing some access requests!</p>';
                return;
            }
            
            logContainer.innerHTML = logs.reverse().map(log => {
                const timestamp = new Date(log.timestamp).toLocaleTimeString();
                const emergencyBadge = log.emergency_mode ? ' <span class="emergency-badge">EMERGENCY</span>' : '';
                
                return `
                    <div class="log-entry ${log.granted ? 'granted' : 'denied'}">
                        <div class="log-time">${timestamp}</div>
                        <div class="log-details">
                            <strong>${log.initiator}</strong> → <strong>${log.target}</strong>
                            <div class="log-reason">${log.reason}${emergencyBadge}</div>
                        </div>
                        <div class="log-status ${log.granted ? 'status-granted' : 'status-denied'}">
                            ${log.granted ? '✅' : '❌'}
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading access log:', error);
    }
}

// Load security report
async function loadSecurityReport() {
    try {
        const reportContainer = document.getElementById('securityReport');
        if (reportContainer) {
            reportContainer.innerHTML = '<div style="text-align: center; padding: 2rem;"><em>🔍 Generating security report... Please wait</em></div>';
        }
        
        const response = await fetch('/api/security_report');
        const data = await response.json();
        
        if (reportContainer) {
            reportContainer.innerHTML = `
                <div class="report-section">
                    <h4>📊 Security Report</h4>
                    <div class="report-content">${data.report.replace(/\n/g, '<br>')}</div>
                </div>
                <div class="report-section">
                    <h4>🔍 Pattern Analysis</h4>
                    <div class="report-content">${data.analysis.replace(/\n/g, '<br>').replace(/⚠️/g, '⚠️')}</div>
                </div>
            `;
        }
    } catch (error) {
        const reportContainer = document.getElementById('securityReport');
        if (reportContainer) {
            reportContainer.innerHTML = `<div style="color: red; text-align: center; padding: 1rem;">Error generating report: ${error}</div>`;
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded, initializing event listeners...');
    
    // Home page form
    const homeForm = document.getElementById('accessForm');
    if (homeForm) {
        console.log('Found home page form');
        homeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Home form submitted');
            
            const initiator = document.getElementById('initiator').value;
            const target = document.getElementById('target').value;
            
            testAccess(initiator, target, 'result');
        });
    }
    
    // Dashboard form
    const dashboardForm = document.getElementById('dashboardAccessForm');
    if (dashboardForm) {
        console.log('Found dashboard form');
        dashboardForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Dashboard form submitted');
            
            const initiator = document.getElementById('dashboardInitiator').value;
            const target = document.getElementById('dashboardTarget').value;
            
            testAccess(initiator, target, 'dashboardResult');
        });
    }
    
    // Emergency mode button
    const emergencyBtn = document.querySelector('.emergency-btn');
    if (emergencyBtn) {
        emergencyBtn.addEventListener('click', toggleEmergencyMode);
    }
    
    // Report button
    const reportBtn = document.querySelector('.report-btn');
    if (reportBtn) {
        reportBtn.addEventListener('click', loadSecurityReport);
    }
    
    // Initialize dashboard features
    if (window.location.pathname === '/dashboard') {
        console.log('Initializing dashboard...');
        loadAccessLog();
        setInterval(loadAccessLog, 3000);
        
        // Add emergency demo info
        setTimeout(() => {
            const quickTest = document.querySelector('.quick-test');
            if (quickTest && !document.getElementById('emergency-demo')) {
                const demoInfo = document.createElement('div');
                demoInfo.id = 'emergency-demo';
                demoInfo.innerHTML = `
                    <div style="background: #fff3cd; border: 2px solid #ffeaa7; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <h4 style="color: #856404; margin-bottom: 0.5rem;">🚨 Emergency Mode Demonstration</h4>
                        <p style="margin-bottom: 0.5rem;"><strong>To test Emergency Mode:</strong></p>
                        <ol style="margin-left: 1.5rem; margin-bottom: 0;">
                            <li>Click "Activate Emergency" button above</li>
                            <li>Try: <strong>Admin_Workstation → Financial_DB</strong> (will work during emergency)</li>
                            <li>Try: <strong>Web_Server_01 → Financial_DB</strong> (will still fail - zones still enforced)</li>
                            <li>Click "Deactivate Emergency" to return to normal</li>
                        </ol>
                    </div>
                `;
                quickTest.appendChild(demoInfo);
            }
        }, 1000);
    }
    
    console.log('Event listeners initialized');
});