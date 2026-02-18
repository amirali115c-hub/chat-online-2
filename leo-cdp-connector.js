// Leo's CDP Browser Connector
// Connects to an already-running browser instead of launching a new one

const http = require('http');
const WebSocket = require('ws');

let ws = null;
let targetTab = null;

// Connect to existing Chrome/Brave with debugging port
async function findExistingBrowser() {
  return new Promise((resolve, reject) => {
    http.get('http://localhost:9222/json', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const targets = JSON.parse(data);
          console.log('Found browser tabs:', targets.length);
          resolve(targets);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', (e) => {
      reject(e);
    });
  });
}

function connectToTab(target) {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(target.webSocketDebuggerUrl);
    ws.on('open', () => {
      console.log('Connected to:', target.title || target.url);
      resolve(ws);
    });
    ws.on('message', (data) => {
      // Handle responses
    });
    ws.on('error', reject);
  });
}

function sendCDPCommand(method, params = {}) {
  return new Promise((resolve, reject) => {
    if (!ws) {
      reject(new Error('Not connected'));
      return;
    }
    const id = Math.floor(Math.random() * 100000);
    const msg = { id, method, params };
    ws.send(JSON.stringify(msg));
    
    const timeout = setTimeout(() => {
      reject(new Error('Timeout'));
    }, 10000);
    
    ws.once('message', (data) => {
      clearTimeout(timeout);
      try {
        const response = JSON.parse(data);
        if (response.id === id) {
          resolve(response.result);
        }
      } catch (e) {
        reject(e);
      }
    });
  });
}

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
      
      let result = { success: true };
      
      switch (command.action) {
        case 'connect':
          // Find existing browser
          const targets = await findExistingBrowser();
          if (targets.length === 0) {
            result = { success: false, error: 'No browser found. Start Chrome/Brave with --remote-debugging-port=9222' };
          } else {
            // Connect to first tab
            await connectToTab(targets[0]);
            targetTab = targets[0];
            result = { 
              success: true, 
              title: targets[0].title, 
              url: targets[0].url,
              tabsFound: targets.length
            };
          }
          break;
          
        case 'list':
          const allTabs = await findExistingBrowser();
          result = { tabs: allTabs.map(t => ({ title: t.title, url: t.url })) };
          break;
          
        case 'goto':
          if (!ws) throw new Error('Not connected');
          await sendCDPCommand('Page.navigate', { url: command.url });
          result = { url: command.url };
          break;
          
        case 'click':
          if (!ws) throw new Error('Not connected');
          await sendCDPCommand('Runtime.evaluate', { 
            expression: `document.querySelector('${command.selector}').click()` 
          });
          break;
          
        case 'type':
          if (!ws) throw new Error('Not connected');
          await sendCDPCommand('Runtime.evaluate', { 
            expression: `document.querySelector('${command.selector}').value='${command.text}'` 
          });
          break;
          
        case 'evaluate':
          if (!ws) throw new Error('Not connected');
          result.result = await sendCDPCommand('Runtime.evaluate', { 
            expression: command.code,
            returnByValue: true
          });
          break;
          
        case 'html':
          if (!ws) throw new Error('Not connected');
          const html = await sendCDPCommand('Runtime.evaluate', { 
            expression: 'document.documentElement.outerHTML',
            returnByValue: true 
          });
          result.html = html.result.value;
          break;
          
        case 'title':
          if (!ws) throw new Error('Not connected');
          const title = await sendCDPCommand('Runtime.evaluate', { 
            expression: 'document.title',
            returnByValue: true 
          });
          result.title = title.result.value;
          break;
          
        case 'screenshot':
          if (!ws) throw new Error('Not connected');
          const screenshot = await sendCDPCommand('Page.captureScreenshot', { 
            format: 'base64' 
          });
          result.screenshot = screenshot.data;
          break;
          
        case 'url':
          if (!ws || !targetTab) throw new Error('Not connected');
          result.url = targetTab.url;
          break;
          
        case 'close':
          if (ws) {
            ws.close();
            ws = null;
            targetTab = null;
          }
          break;
          
        default:
          result = { success: false, error: 'Unknown command' };
      }
      
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(result));
      
    } catch (error) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: error.message }));
    }
  });
});

const PORT = 9877;

server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║   Leo's CDP Browser Connector v2                        ║
║                                                           ║
║   URL: http://localhost:${PORT}                            ║
║                                                           ║
║   IMPORTANT: To use, start your browser with:            ║
║   --remote-debugging-port=9222                          ║
║                                                           ║
║   Example:                                              ║
║   "C:\\Program Files\\...\\chrome.exe"                   ║
║   --remote-debugging-port=9222                           ║
║                                                           ║
║   Commands:                                              ║
║   - connect     Connect to existing browser              ║
║   - list        List all tabs                            ║
║   - goto(url)   Navigate to URL                         ║
║   - click(sel)  Click element                           ║
║   - type(sel,t) Type into element                       ║
║   - evaluate    Run JavaScript                          ║
║   - html        Get page HTML                           ║
║   - title       Get page title                          ║
║   - screenshot  Get screenshot                          ║
║   - url         Get current URL                         ║
║   - close       Disconnect                              ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

process.on('SIGINT', () => {
  if (ws) ws.close();
  process.exit();
});
