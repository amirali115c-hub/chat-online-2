// ========================================
// LEO'S DIRECT CDP BROWSER CONTROL - V3
// Robust, stable browser control using direct CDP
// No dependency on OpenClaw gateway
// ========================================

const http = require('http');
const WebSocket = require('ws');

// Configuration
const CDP_HTTP_PORT = 9222;  // Browser debugging port
const MY_API_PORT = 9878;    // My API port

// CDP Connection
let ws = null;
let msgId = 0;
let pending = {};
let connected = false;
let currentTargetId = null;

// ========================================
// CDP PROTOCOL
// ========================================

function getId() {
  return ++msgId;
}

function connect() {
  return new Promise((resolve, reject) => {
    // Get list of targets
    http.get(`http://localhost:${CDP_HTTP_PORT}/json`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const targets = JSON.parse(data);
          
          // Find first page target
          const target = targets.find(t => t.type === 'page');
          
          if (!target) {
            reject(new Error('No page targets found'));
            return;
          }
          
          console.log('Target:', target.title, target.url);
          currentTargetId = target.id;
          
          // Connect via WebSocket
          ws = new WebSocket(target.webSocketDebuggerUrl);
          
          ws.on('open', () => {
            console.log('Connected to browser!');
            connected = true;
            
            // Enable necessary domains
            sendCommand('Runtime.enable').catch(() => {});
            sendCommand('Page.enable').catch(() => {});
            sendCommand('Log.enable').catch(() => {});
            
            resolve(target);
          });
          
          ws.on('message', (buf) => {
            const msg = JSON.parse(buf.toString());
            
            // Handle responses
            if (msg.id && pending[msg.id]) {
              const { resolve, reject } = pending[msg.id];
              delete pending[msg.id];
              if (msg.result) resolve(msg.result);
              else if (msg.error) reject(new Error(msg.error.message));
            }
            
            // Handle events
            if (msg.method) {
              handleEvent(msg);
            }
          });
          
          ws.on('error', (e) => {
            console.error('WebSocket error:', e.message);
            connected = false;
          });
          
          ws.on('close', () => {
            console.log('Disconnected');
            connected = false;
          });
          
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

function sendCommand(method, params = {}) {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      reject(new Error('Not connected'));
      return;
    }
    
    const id = getId();
    pending[id] = { resolve, reject };
    
    ws.send(JSON.stringify({
      id,
      method,
      params
    }));
    
    // Timeout after 30 seconds
    setTimeout(() => {
      if (pending[id]) {
        delete pending[id];
        reject(new Error('Timeout'));
      }
    }, 30000);
  });
}

function handleEvent(msg) {
  // Console logs
  if (msg.method === 'Runtime.consoleAPICalled') {
    // Could log console messages here
  }
}

// ========================================
// NAVIGATION & PAGE CONTROL
// ========================================

async function navigate(url) {
  const result = await sendCommand('Page.navigate', { url });
  await sendCommand('Page.waitUntil', { 
    waitUntil: ['networkidle0', 'domcontentloaded'] 
  });
  return { success: true, url };
}

async function getHTML() {
  const result = await sendCommand('Runtime.evaluate', {
    expression: 'document.documentElement.outerHTML',
    returnByValue: true
  });
  return { success: true, html: result.result.value };
}

async function getTitle() {
  const result = await sendCommand('Runtime.evaluate', {
    expression: 'document.title',
    returnByValue: true
  });
  return { success: true, title: result.result.value };
}

async function getURL() {
  const result = await sendCommand('Page.getFrameTree');
  return { success: true, url: result.frameTree.frame.url };
}

// ========================================
// ACTIONS
// ========================================

async function click(selector) {
  // First find the element
  const result = await sendCommand('Runtime.evaluate', {
    expression: `
      (() => {
        const el = document.querySelector('${selector}');
        if (!el) return null;
        el.scrollIntoView();
        const box = el.getBoundingClientRect();
        return {
          x: box.x + box.width / 2,
          y: box.y + box.height / 2
        };
      })()
    `,
    returnByValue: true
  });
  
  if (!result.result.value) {
    throw new Error('Element not found');
  }
  
  const { x, y } = result.result.value;
  
  // Click using Input.dispatchMouseEvent
  await sendCommand('Input.dispatchMouseEvent', {
    type: 'mousePressed',
    x, y,
    button: 'left',
    clickCount: 1
  });
  
  await sendCommand('Input.dispatchMouseEvent', {
    type: 'mouseReleased',
    x, y,
    button: 'left',
    clickCount: 1
  });
  
  return { success: true };
}

async function type(selector, text) {
  await sendCommand('Runtime.evaluate', {
    expression: `
      const el = document.querySelector('${selector}');
      if (el) {
        el.value = '${text.replace(/'/g, "\\'")}';
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        'ok';
      } else {
        'not found';
      }
    `,
    returnByValue: true
  });
  
  return { success: true };
}

async function evaluate(code) {
  const result = await sendCommand('Runtime.evaluate', {
    expression: code,
    returnByValue: true
  });
  return { success: true, result: result.result.value };
}

async function screenshot() {
  const result = await sendCommand('Page.captureScreenshot', {
    format: 'png'
  });
  return { success: true, screenshot: result.data };
}

async function listTabs() {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:${CDP_HTTP_PORT}/json`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const targets = JSON.parse(data);
          resolve({
            success: true,
            tabs: targets.filter(t => t.type === 'page').map(t => ({
              id: t.id,
              title: t.title,
              url: t.url
            }))
          });
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function switchTab(targetId) {
  await connect();
  return { success: true };
}

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
    let cmd = {};
    try {
      cmd = body ? JSON.parse(body) : {};
    } catch {}
    
    const action = (cmd.action || '').toLowerCase();
    
    try {
      // Auto-connect if needed
      if (!connected && action !== 'list' && action !== 'status') {
        await connect();
      }
      
      switch (action) {
        case 'connect':
          const target = await connect();
          res.end(JSON.stringify({ 
            success: true, 
            title: target.title,
            url: target.url 
          }));
          break;
          
        case 'goto':
          const r = await navigate(cmd.url);
          res.end(JSON.stringify(r));
          break;
          
        case 'html':
          res.end(JSON.stringify(await getHTML()));
          break;
          
        case 'title':
          res.end(JSON.stringify(await getTitle()));
          break;
          
        case 'url':
          res.end(JSON.stringify(await getURL()));
          break;
          
        case 'click':
          await click(cmd.selector);
          res.end(JSON.stringify({ success: true }));
          break;
          
        case 'type':
          await type(cmd.selector, cmd.text);
          res.end(JSON.stringify({ success: true }));
          break;
          
        case 'evaluate':
          res.end(JSON.stringify(await evaluate(cmd.code)));
          break;
          
        case 'screenshot':
          res.end(JSON.stringify(await screenshot()));
          break;
          
        case 'list':
          res.end(JSON.stringify(await listTabs()));
          break;
          
        case 'status':
          res.end(JSON.stringify({ 
            connected,
            targetId: currentTargetId
          }));
          break;
          
        default:
          res.end(JSON.stringify({ error: 'Unknown action' }));
      }
    } catch (e) {
      res.end(JSON.stringify({ error: e.message }));
    }
  });
});

// ========================================
// MAIN
// ========================================

async function main() {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║         LEO'S DIRECT CDP CONTROL - V3                     ║
║                                                           ║
║   Browser must be running with:                           ║
║   --remote-debugging-port=${CDP_HTTP_PORT}                              ║
║                                                           ║
║   API: http://localhost:${MY_API_PORT}                             ║
║                                                           ║
║   Commands:                                              ║
║   - connect       Connect to browser                     ║
║   - goto(url)     Navigate to URL                        ║
║   - click(sel)    Click element by CSS selector         ║
║   - type(sel,txt) Type into element                     ║
║   - evaluate(code) Execute JavaScript                    ║
║   - html          Get page HTML                          ║
║   - title         Get page title                         ║
║   - url           Get current URL                        ║
║   - screenshot    Get screenshot (base64)               ║
║   - list          List all tabs                          ║
║   - status        Connection status                      ║
╚═══════════════════════════════════════════════════════════╝
  `);
  
  // Try to connect
  try {
    await connect();
    console.log('Auto-connected!');
  } catch (e) {
    console.log('Not connected:', e.message);
    console.log('Start browser with --remote-debugging-port=9222');
  }
  
  server.listen(MY_API_PORT, () => {
    console.log(`API ready on http://localhost:${MY_API_PORT}`);
  });
}

main().catch(console.error);
