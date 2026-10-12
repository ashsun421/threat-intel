# Threat Intel Platform

FastAPI + TimescaleDB backend, MQTT ingest, Ollama incident reports, React dashboard.

## Prerequisites
- Docker Desktop, Python 3.12, Node 20+ (22 preferred)
- Ollama: `brew install ollama && brew services start ollama && ollama pull llama3.2`
- Suricata (optional, for real detections): `brew install suricata`

## First-time setup
```bash
cp .env.example .env            # set your own password in BOTH places
docker compose --env-file .env -f infra/docker-compose.yml up -d
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
cd ../dashboard && npm install
```

## Run (one terminal each; backend tabs need the venv active)
```bash
cd backend && python -m app.services.mqtt_listener
cd backend && python -m app.services.eve_publisher
cd backend && fastapi dev app/main.py
cd dashboard && npm run dev
```
API docs: http://localhost:8000/docs, dashboard: http://localhost:5173

## Send a test alert
```bash
mkdir -p ~/suricata-logs && touch ~/suricata-logs/eve.json
echo '{"timestamp":"2026-10-12T12:00:00.000000+0000","event_type":"alert","src_ip":"192.168.1.50","dest_ip":"192.168.1.10","alert":{"signature":"TEST alert","severity":1}}' >> ~/suricata-logs/eve.json
```

## Team rules
- Each person runs their own local stack. The database and broker are local-only dev settings, so never expose them.
- Never commit `.env` or any token or password.
- Work on a branch, open a pull request, and wait for CI to pass before merging to `main`.
- Database changes: edit `backend/app/models.py`, run `alembic revision --autogenerate -m "message"`, read the generated file, then commit the model and migration together. Tell the team before generating one, so two people don't create competing migrations. Never edit a migration that's already pushed.

