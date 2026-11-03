# Holdmate board: generate state with python, build with node, serve with nginx.
# Build context is the repo root (see docker-compose.yml).
FROM python:3.12-slim AS gen
WORKDIR /repo
COPY src/ ./src/
COPY data/doorkeeper-lines.json data/role-phrasebooks.json ./data/
COPY ui/board/public/board-state.sample.json /sample.json
COPY sh/bake-board.py ./sh/bake-board.py
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e . \
  && mkdir -p /out \
  && (PYTHONPATH=src python3 -m adaptive_ivr_agent.holdmate \
    --phrasebooks data/role-phrasebooks.json \
    --lines data/doorkeeper-lines.json \
    --knowledge /tmp/knowledge.json \
    --lessons /tmp/lessons.jsonl \
    --fresh --depth 2 \
    --board-out /out/board-state.json \
    || cp /sample.json /out/board-state.json) \
  && python3 sh/bake-board.py --board /out/board-state.json --lines data/doorkeeper-lines.json

FROM node:20-alpine AS build
WORKDIR /repo/ui/board
COPY ui/board/package.json ui/board/package-lock.json ./
RUN npm ci
COPY ui/board/. ./
COPY data/doorkeeper-lines.json /data/doorkeeper-lines.json
COPY --from=gen /out/board-state.json ./public/board-state.json
RUN printf '{"version":"docker","built":"%s"}' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > ./public/version.json \
  && npm run build

FROM nginx:1.27-alpine
COPY --from=build /repo/ui/board/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
