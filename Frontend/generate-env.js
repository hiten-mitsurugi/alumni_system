import os from 'os';
import fs from 'fs';
import path from 'path';

// Get local IP address automatically
function getLocalIp() {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        return net.address;
      }
    }
  }
  return 'localhost';
}

const localIP = getLocalIp();
const backendPort = process.env.BACKEND_PORT || '8000';
const envPath = path.join(process.cwd(), '.env');

// Read existing .env file
let envContent = '';
if (fs.existsSync(envPath)) {
  envContent = fs.readFileSync(envPath, 'utf8');
}

// Update or add the dynamic variables
const updates = {
  VITE_API_URL: `http://${localIP}:${backendPort}/api`,
  VITE_API_BASE_URL: `http://${localIP}:${backendPort}`,
  VITE_WS_URL: `ws://${localIP}:${backendPort}/ws/notifications/`,
};

// Parse existing env and update
const lines = envContent.split('\n');
const updatedLines = [];
const processedKeys = new Set();

for (const line of lines) {
  const trimmed = line.trim();
  
  // Skip comments and empty lines initially
  if (trimmed.startsWith('#') || trimmed === '') {
    updatedLines.push(line);
    continue;
  }
  
  // Check if this line is a key=value pair
  const match = trimmed.match(/^([^=]+)=/);
  if (match) {
    const key = match[1].trim();
    if (updates[key]) {
      updatedLines.push(`${key}=${updates[key]}`);
      processedKeys.add(key);
    } else {
      updatedLines.push(line);
    }
  } else {
    updatedLines.push(line);
  }
}

// Add any new keys that weren't in the file
for (const [key, value] of Object.entries(updates)) {
  if (!processedKeys.has(key)) {
    updatedLines.push(`${key}=${value}`);
  }
}

// Write back to .env
fs.writeFileSync(envPath, updatedLines.join('\n'), 'utf8');

console.log(`\n🌐 Dynamic IP Configuration Generated:`);
console.log(`   IP Address: ${localIP}`);
console.log(`   Backend: http://${localIP}:${backendPort}`);
console.log(`   Frontend will connect to this backend automatically\n`);
