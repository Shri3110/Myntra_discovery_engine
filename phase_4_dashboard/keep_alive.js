const https = require('https');

// Read the URL from environment variable or use the default placeholder
const TARGET_URL = process.env.RENDER_EXTERNAL_URL 
    ? `${process.env.RENDER_EXTERNAL_URL}/health` 
    : 'https://your-app.onrender.com/health';

// Ping every 10 minutes (600,000 milliseconds)
const PING_INTERVAL = 10 * 60 * 1000;

console.log(`Starting Keep-Alive Service...`);
console.log(`Target URL: ${TARGET_URL}`);
console.log(`Ping Interval: ${PING_INTERVAL / 1000 / 60} minutes`);

setInterval(() => {
    https.get(TARGET_URL, (res) => {
        console.log(`[${new Date().toISOString()}] Pinged ${TARGET_URL} - Status Code: ${res.statusCode}`);
    }).on('error', (err) => {
        console.error(`[${new Date().toISOString()}] Error pinging ${TARGET_URL}:`, err.message);
    });
}, PING_INTERVAL);
