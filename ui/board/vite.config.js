import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const VOLUME_FILE = path.join(here, '..', '..', '.talk-volume');
const VOLUME_RE = /^(0\.[0-9]+|[1-3](\.[0-9]+)?|4(\.0+)?)$/;
const DEFAULT_VOLUME = '0.7';
const DTMF_FILE = path.join(here, '..', '..', '.talk-dtmf');
const DTMF_RE = /^[0-9*#]$/;

function readVolume() {
  try {
    const raw = fs.readFileSync(VOLUME_FILE, 'utf8').trim();
    return VOLUME_RE.test(raw) ? raw : DEFAULT_VOLUME;
  } catch {
    return DEFAULT_VOLUME;
  }
}

function volumeApi() {
  return {
    name: 'talk-volume-api',
    configureServer(server) {
      server.middlewares.use('/api/volume', (req, res) => {
        if (req.method === 'GET') {
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ volume: readVolume() }));
          return;
        }
        if (req.method === 'POST') {
          let body = '';
          req.on('data', (chunk) => { body += chunk; });
          req.on('end', () => {
            res.setHeader('Content-Type', 'application/json');
            let value = '';
            try {
              value = String(JSON.parse(body).volume);
            } catch {
              res.statusCode = 400;
              res.end(JSON.stringify({ error: 'bad json' }));
              return;
            }
            if (!VOLUME_RE.test(value)) {
              res.statusCode = 400;
              res.end(JSON.stringify({ error: 'volume must be 0.1-4.0' }));
              return;
            }
            fs.writeFileSync(VOLUME_FILE, value);
            res.end(JSON.stringify({ volume: value }));
          });
          return;
        }
        res.statusCode = 405;
        res.end(JSON.stringify({ error: 'method not allowed' }));
      });
    },
  };
}

function dtmfApi() {
  return {
    name: 'talk-dtmf-api',
    configureServer(server) {
      server.middlewares.use('/api/dtmf', (req, res) => {
        if (req.method !== 'POST') {
          res.statusCode = 405;
          res.end(JSON.stringify({ error: 'method not allowed' }));
          return;
        }
        let body = '';
        req.on('data', (chunk) => { body += chunk; });
        req.on('end', () => {
          res.setHeader('Content-Type', 'application/json');
          let digit = '';
          try {
            digit = String(JSON.parse(body).digit);
          } catch {
            res.statusCode = 400;
            res.end(JSON.stringify({ error: 'bad json' }));
            return;
          }
          if (!DTMF_RE.test(digit)) {
            res.statusCode = 400;
            res.end(JSON.stringify({ error: 'digit must be 0-9, * or #' }));
            return;
          }
          fs.writeFileSync(DTMF_FILE, digit);
          res.end(JSON.stringify({ digit }));
        });
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), volumeApi(), dtmfApi()],
  base: './',
});
