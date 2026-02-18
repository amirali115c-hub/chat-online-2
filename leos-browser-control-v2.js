// ========================================
// LEO'S PERSISTENT BROWSER CONTROL SYSTEM
// Uses Chrome DevTools Protocol (CDP) directly
// More stable than extension-based control
// ========================================

const http = require('http');
const WebSocket = require('ws');

// Configuration
const CDP_PORT = 9222;
const API_PORT = 9876;

// Global state
let ws = null;
let browserTarget = null;
let connectionActive = false;
let reconnectAttempts = 0;
const MAX_RECONNECT = 5;

// ========================================
// CDP CONNECTION FUNCTIONS
// ========================================

// Connect to Chrome via WebSocket
function connectCDP(targetId = null) {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:${CDP_PORT}/json`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', async () => {
        try {
          const targets = JSON.parse(data);
          
          // Find the target (prefer regular pages, not internal ones)
          let target = targets.find(t => t.type === 'page' && !t.url.startsWith('chrome://'));
          if (!target) target = targets.find(t => t.type === 'page');
          if (!target && targetId) target = targets.find(t => t.id === targetId);
          if (!target && targets.length > 0) target = targets[0];
          
          if (!target) {
            reject(new Error('No browser targets found'));
            return;
          }
          
          console.log(`Connecting to: ${target.title} - ${target.url}`);
          
          // Connect via WebSocket
          ws = new WebSocket(target.webSocketDebuggerUrl);
          
          ws.on('open', () => {
            console.log('CDP WebSocket connected!');
            connectionActive = true;
            browserTarget = target;
            reconnectAttempts = 0;
            resolve(target);
          });
          
          ws.on('message', (message) => {
            handleCDPMessage(JSON.parse(message.toString()));
          });
          
          ws.on('close', () => {
            console.log('CDP WebSocket disconnected');
            connectionActive = false;
            attemptReconnect();
          });
          
          ws.on('error', (err) => {
            console.error('CDP WebSocket error:', err.message);
            connectionActive = false;
          });
          
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', (e) => {
      reject(e);
    });
  });
}

// Handle CDP messages
function handleCDPMessage(msg) {
  // Could implement event handling here
}

// Send CDP command and wait for response
function sendCDP(method, params = {}) {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      reject(new Error('Not connected'));
      return;
    }
    
    const id = Math.floor(Math.random() * 100000) + 1;
    const message = { id, method, params };
    
    const timeout = setTimeout(() => {
      reject(new Error('Timeout waiting for response'));
    }, 30000);
    
    // One-time message handler
    const handler = (data) => {
      try {
        const response = JSON.parse(data.toString());
        if (response.id === id) {
          clearTimeout(timeout);
          ws.removeListener('message', handler);
          resolve(response.result || response);
        }
      } catch (e) {
        // Not our response
      }
    };
    
    ws.on('message', handler);
    ws.send(JSON.stringify(message));
  });
}

// Attempt to reconnect
async function attemptReconnect() {
  if (reconnectAttempts >= MAX_RECONNECT) {
    console.log('Max reconnection attempts reached');
    return;
  }
  
  reconnectAttempts++;
  console.log(`Reconnecting... attempt ${reconnectAttempts}`);
  
  try {
    await connectCDP();
  } catch (e) {
    console.log('Reconnection failed:', e.message);
    setTimeout(attemptReconnect, 2000);
  }
}

// ========================================
// HIGH-LEVEL ACTIONS
// ========================================

const actions = {
  // Navigate to URL
  async goto(url) {
    await sendCDP('Page.navigate', { url });
    // Wait for page to load
    await sendCDP('Page.waitUntil', { 
      waitUntil: ['networkidle0', 'domcontentloaded'] 
    });
    return { success: true, url };
  },
  
  // Get page title
  async title() {
    const result = await sendCDP('Runtime.evaluate', { 
      expression: 'document.title',
      returnByValue: true 
    });
    return { success: true, title: result.result.value };
  },
  
  // Get current URL
  async url() {
    return { success: true, url: browserTarget?.url || 'unknown' };
  },
  
  // Get page HTML
  async html() {
    const result = await sendCDP('Runtime.evaluate', { 
      expression: 'document.documentElement.outerHTML',
      returnByValue: true 
    });
    return { success: true, html: result.result.value };
  },
  
  // Click element by selector
  async click(selector) {
    await sendCDP('Runtime.evaluate', { 
      expression: `document.querySelector('${selector}')?.click()`
    });
    return { success: true };
  },
  
  // Type into element
  async type(selector, text) {
    await sendCDP('Runtime.evaluate', { 
      expression: `
        const el = document.querySelector('${selector}');
        el.value = '${text}';
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      `
    });
    return { success: true };
  },
  
  // Take screenshot
  async screenshot() {
    const result = await sendCDP('Page.captureScreenshot', { 
      format: 'png' 
    });
    return { success: true, screenshot: result.data };
  },
  
  // Evaluate JavaScript
  async evaluate(code) {
    const result = await sendCDP('Runtime.evaluate', { 
      expression: code,
      returnByValue: true 
    });
    return { success: true, result: result.result.value };
  },
  
  // List all tabs
  async list() {
    return new Promise((resolve, reject) => {
      http.get(`http://localhost:${CDP_PORT}/json`, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const targets = JSON.parse(data);
            resolve({ 
              success: true, 
              tabs: targets.map(t => ({ title: t.title, url: t.url, type: t.type })) 
            });
          } catch (e) {
            reject(e);
          }
        });
      }).on('error', reject);
    });
  },
  
  // Switch to specific tab
  async switchTab(targetId) {
    await connectCDP(targetId);
    return { success: true };
  },
  
  // Get connection status
  status() {
    return { 
      connected: connectionActive,
      target: browserTarget?.title || 'none',
      url: browserTarget?.url || 'none',
      reconnectAttempts
    };
  }
};

// ========================================
// HTTP API SERVER
// ========================================

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', async () => {
    try {
      let command = {};
      try {
        command = body ? JSON.parse(body) : {};
      } catch {}
      
      const action = command.action?.toLowerCase();
      
      if (action === 'connect') {
        const target = await connectCDP(command.targetId);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, title: target.title, url: target.url }));
        return;
      }
      
      if (!connectionActive) {
        // Try to connect first
        try {
          await connectCDP();
        } catch (e) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Not connected to browser. Start Chrome with --remote-debugging-port=9222' }));
          return;
        }
      }
      
      if (actions[action]) {
        const result = await actions[action](command);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } else {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Unknown action' }));
      }
      
    } catch (error) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: error.message }));
    }
  });
});

// ========================================
// STARTUP
// ========================================

async function start() {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║   LEO'S PERSISTENT BROWSER CONTROL SYSTEM v2          ║
║                                                           ║
║   API Server: http://localhost:${API_PORT}                    ║
║                                                           ║
║   IMPORTANT: Start your browser with:                    ║
║   --remote-debugging-port=${CDP_PORT}                          ║
║                                                           ║
║   Example:                                              ║
║   "C:\\Program Files\\...\\chrome.exe"                  ║
║   --remote-debugging-port=${CDP_PORT}                          ║
║                                                           ║
║   Commands:                                              ║
║   - connect       Connect to browser                     ║
║   - goto(url)     Navigate to URL                       ║
║   - click(sel)    Click element                         ║
║   - type(sel,text) Type into element                   ║
║   - evaluate(code) Run JavaScript                      ║
║   - screenshot    Take screenshot                        ║
║   - html          Get page HTML                         ║
║   - title         Get page title                       ║
║   - url           Get current URL                      ║
║   - list          List all tabs                         ║
║   - status        Connection status                     ║
║                                                           ║
║   Press Ctrl+C to stop                                 ║
╚═══════════════════════════════════════════════════════════╝
  `);
  
  // Try to auto-connect
  try {
    await connectCDP();
    console.log('Auto-connected to browser!');
  } catch (e) {
    console.log('Browser not running with debugging. Start Chrome with --remote-debugging-port=9222');
  }
  
  server.listen(API_PORT, () => {
    console.log(`API server running on port ${API_PORT}`);
  });
}

process.on('SIGINT', () => {
  console.log('\nShutting down...');
  if (ws) ws.close();
  process.exit();
});

start();
