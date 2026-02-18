const http = require('http');

const postData = JSON.stringify({
  action: 'goto',
  url: 'https://mail.google.com/mail/u/0/#inbox'
});

const req = http.request({
  hostname: 'localhost',
  port: 9877,
  path: '/',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
}, (res) => {
  let r = '';
  res.on('data', (c) => r += c);
  res.on('end', () => console.log(r));
});

req.write(postData);
req.end();
