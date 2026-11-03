// Holdmate board server for Docker: static dist/ + the /api/* the Vite
// dev middleware provides locally (volume, DTMF). No dependencies.
// State files are container-local and ephemeral (live sim link is later).
// Env: PORT (default 80), STATE_DIR (default /tmp/holdmate).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.join(here, 'dist');
const STATE_DIR = process.env.STATE_DIR || '/tmp/holdmate';
const VOLUME_FILE = path.join(STATE_DIR, 'volume');
const DTMF_FILE = path.join(STATE_DIR, 'dtmf');
const VOLUME_RE = /^(0\.[0-9]+|[1-3](\.[0-9]+)?|4(\.0+)?)$/;
const DTMF_RE = /^[0-9*#]$/;
const DEFAULT_VOLUME = '0.7';

const TYPES = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.mp3': 'audio/mpeg',
};

function readBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => resolve(body));
  });
}

function json(res, status, obj) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(obj));
}

function readVolume() {
  try {
    const raw = fs.readFileSync(VOLUME_FILE, 'utf8').trim();
    return VOLUME_RE.test(raw) ? raw : DEFAULT_VOLUME;
  } catch {
    return DEFAULT_VOLUME;
  }
}

async function api(req, res) {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/api/volume') {
    if (req.method === 'GET') {
      json(res, 200, { volume: readVolume() });
      return true;
    }
    if (req.method === 'POST') {
      let value = '';
      try {
        value = String(JSON.parse(await readBody(req)).volume);
      } catch {
        json(res, 400, { error: 'bad json' });
        return true;
      }
      if (!VOLUME_RE.test(value)) {
        json(res, 400, { error: 'volume must be 0.1-4.0' });
        return true;
      }
      fs.mkdirSync(STATE_DIR, { recursive: true });
      fs.writeFileSync(VOLUME_FILE, value);
      json(res, 200, { volume: value });
      return true;
    }
    json(res, 405, { error: 'method not allowed' });
    return true;
  }
  if (url.pathname === '/api/dtmf') {
    if (req.method !== 'POST') {
      json(res, 405, { error: 'method not allowed' });
      return true;
    }
    let digit = '';
    try {
      digit = String(JSON.parse(await readBody(req)).digit);
    } catch {
      json(res, 400, { error: 'bad json' });
      return true;
    }
    if (!DTMF_RE.test(digit)) {
      json(res, 400, { error: 'digit must be 0-9, * or #' });
      return true;
    }
    fs.mkdirSync(STATE_DIR, { recursive: true });
    fs.writeFileSync(DTMF_FILE, digit);
    json(res, 200, { digit });
    return true;
  }
  return false;
}

const server = http.createServer(async (req, res) => {
  try {
    if (await api(req, res)) {
      return;
    }
    const url = new URL(req.url, 'http://x');
    let file = path.normalize(path.join(DIST, url.pathname));
    if (!file.startsWith(DIST)) {
      res.statusCode = 403;
      res.end('forbidden');
      return;
    }
    if (url.pathname.endsWith('/')) {
      file = path.join(file, 'index.html');
    }
    fs.readFile(file, (err, data) => {
      if (err) {
        res.statusCode = 404;
        res.end('not found');
        return;
      }
      res.setHeader('Content-Type', TYPES[path.extname(file)] || 'application/octet-stream');
      res.end(data);
    });
  } catch {
    res.statusCode = 500;
    res.end('error');
  }
});

const port = Number(process.env.PORT || 80);
server.listen(port, () => {
  console.log(`holdmate board on :${port} (dist=${DIST})`);
});
