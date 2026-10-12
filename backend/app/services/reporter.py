import httpx

from app.config import OLLAMA_MODEL, OLLAMA_URL


def generate_report(alert_json: dict) -> str:
    prompt = (
        "You are a SOC analyst. Write a short incident report with these sections: "
        "Summary, Affected Hosts, Severity, Recommended Action. "
        "Use ONLY facts present in the alert JSON below. If something is not in the "
        "data, write 'not available' instead of guessing.\n"
        f"{alert_json}"
    )
    r = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["response"]
