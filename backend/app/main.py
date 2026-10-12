from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Alert, Incident
from app.services.reporter import generate_report

app = FastAPI(title="Threat Intel Platform")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])


def get_db():
    with SessionLocal() as db:
        yield db


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/alerts")
def list_alerts(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.scalars(select(Alert).order_by(Alert.timestamp.desc()).limit(limit)).all()
    return [{"id": a.id, "timestamp": a.timestamp, "signature": a.signature,
             "severity": a.severity, "src_ip": a.src_ip, "dest_ip": a.dest_ip,
             "status": a.status, "incident_id": a.incident_id} for a in rows]


@app.post("/alerts/{alert_id}/report")
def report(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    text = generate_report(alert.raw)
    if alert.incident is None:
        alert.incident = Incident(title=alert.signature[:200],
                                  severity=alert.severity, report=text)
    else:
        alert.incident.report = text
    db.commit()
    return {"incident_id": alert.incident_id, "report": text}
