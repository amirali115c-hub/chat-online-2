const puppeteer = require('puppeteer');

async function sendJobApplication() {
  const browser = await puppeteer.launch({
    headless: false,
    userDataDir: undefined
  });
  
  const page = await browser.newPage();
  
  // Login to Gmail
  await page.goto('https://mail.google.com/mail/u/0/#inbox', { waitUntil: 'networkidle2' });
  
  console.log('Please login to Gmail manually if needed.');
  console.log('Press Enter in this console when ready to send email...');
  
  await new Promise(resolve => process.stdin.once('data', resolve));
  
  // Open compose
  await page.goto('https://mail.google.com/mail/u/0/?view=cm&fs=1', { waitUntil: 'networkidle2' });
  
  // Fill in email
  await page.type('textarea[type="email"]', 'hello@twine.net');
  await page.type('input[name="subject"]', 'Application for Freelance Copywriter Position');
  
  // Body
  await page.click('div[contenteditable="true"]');
  await page.keyboard.type(`Hi,

I'm Amir Ali, a professional SEO copywriter with 4+ years of experience. I'm interested in the Freelance Copywriter position at Twine.

What I offer:
- SEO content that ranks on Google
- Website copy that converts
- Blog posts and articles
- Experience working with international clients

I'm available for remote work and can deliver quality copy on deadline.

Looking forward to hearing from you.

Best regards,
Amir Ali
amircontentwriter@gmail.com
WhatsApp: +92 320 4779972`);

  console.log('Email filled. Click Send manually or press Enter to send...');
  await new Promise(resolve => process.stdin.once('data', resolve));
  
  // Click send
  await page.click('div[data-actor-id="send"]');
  
  console('Email sent!');
  await browser.close();
}

sendJobApplication().catch(console.error);
