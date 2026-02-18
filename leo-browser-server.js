// Leo's Browser Control Server
// This gives Leo full control over your browser

const http = require('http');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

let puppeteer;
try {
  puppeteer = require('puppeteer-core');
} catch (e) {
  console.log('Installing puppeteer-core...');
  require('child_process').execSync('npm install puppeteer-core', { stdio: 'inherit' });
  puppeteer = require('puppeteer-core');
}

let browser = null;
let page = null;

// Find Chrome executable
function findChrome() {
  const possiblePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    process.env.LOCALAPPDATA + '\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
    process.env.LOCALAPPDATA + '\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

const chromePath = findChrome();

async function launchBrowser() {
  if (browser) return;
  
  const executablePath = chromePath || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  
  browser = await puppeteer.launch({
    executablePath,
    headless: false,
    defaultViewport: null,
    args: [
      '--start-maximized',
      '--remote-debugging-port=9222'
    ]
  });
  
  const pages = await browser.pages();
  page = pages[0] || await browser.newPage();
  
  console.log('Browser launched successfully!');
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
      let command;
      try {
        command = body ? JSON.parse(body) : {};
      } catch {
        command = {};
      }
      
      if (!browser) {
        await launchBrowser();
      }
      
      let result = { success: true };
      
      switch (command.action) {
        case 'goto':
          await page.goto(command.url, { waitUntil: 'networkidle0' });
          result.url = page.url();
          break;
          
        case 'click':
          await page.click(command.selector);
          break;
          
        case 'type':
          await page.type(command.selector, command.text);
          break;
          
        case 'evaluate':
          result.result = await page.evaluate(command.code);
          break;
          
        case 'screenshot':
          result.screenshot = await page.screenshot({ encoding: 'base64' });
          break;
          
        case 'html':
          result.html = await page.content();
          break;
          
        case 'title':
          result.title = await page.title();
          break;
          
        case 'url':
          result.url = page.url();
          break;
          
        case 'evaluateAsync':
          result.result = await page.evaluate(command.code);
          break;
          
        case 'waitForSelector':
          await page.waitForSelector(command.selector, { timeout: command.timeout || 5000 });
          break;
          
        case 'getText':
          result.text = await page.$eval(command.selector, el => el.textContent);
          break;
          
        case 'close':
          await browser.close();
          browser = null;
          page = null;
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

const PORT = 9876;

server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║   Leo's Browser Control Server is running!                ║
║                                                           ║
║   URL: http://localhost:${PORT}                            ║
║                                                           ║
║   Commands available:                                      ║
║   - goto(url)          Navigate to URL                    ║
║   - click(selector)    Click an element                  ║
║   - type(selector, text) Type into element                ║
║   - evaluate(code)    Run JavaScript                     ║
║   - screenshot        Get page screenshot                 ║
║   - html              Get page HTML                       ║
║   - title             Get page title                      ║
║   - url               Get current URL                     ║
║                                                           ║
║   Press Ctrl+C to stop                                    ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

process.on('SIGINT', async () => {
  console.log('Shutting down...');
  if (browser) await browser.close();
  process.exit();
});
