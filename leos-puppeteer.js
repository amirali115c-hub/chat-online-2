// ========================================
// LEO'S DIRECT PUPPETEER CONTROL
// Direct connection to Chrome with debugging
// ========================================

const puppeteer = require('puppeteer-core');

let browser = null;
let page = null;

async function initBrowser() {
  // Find Chrome
  const chromePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Users\\HP\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Users\\HP\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
    process.env.LOCALAPPDATA + '\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
  ];
  
  let chromePath = chromePaths.find(p => {
    try {
      require('fs').accessSync(p);
      return true;
    } catch {
      return false;
    }
  });
  
  if (!chromePath) {
    console.log('Chrome not found');
    return false;
  }
  
  try {
    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      defaultViewport: null,
      args: [
        '--remote-debugging-port=9222',
        '--no-first-run',
        '--no-default-browser-check'
      ],
      protocol: 'webdriver',
      product: 'chrome'
    });
    
    // Connect to existing debugging port instead of launching new
    const browserWSEndpoint = 'http://localhost:9222';
    browser = await puppeteer.connect({
      browserWSEndpoint: browserWSEndpoint.replace('http', 'ws') + '/devtools/browser',
    });
    
    const pages = await browser.pages();
    page = pages[0] || await browser.newPage();
    
    console.log('Connected to browser!');
    return true;
  } catch (e) {
    console.log('Connection error:', e.message);
    return false;
  }
}

// Start the browser controller
initBrowser().then(success => {
  if (success) {
    console.log('Browser control ready!');
  }
});
