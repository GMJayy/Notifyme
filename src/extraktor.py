import re

CVE_RE = re.compile(r"\bCVE[-‐‑–—\s]?(\d{4})[-‐‑–—\s]?(\d{4,7})\b", re.IGNORECASE)

def extract_ioc(news_item: dict) -> list[str]:
    """Mengekstrak CVE dari title dan summary, mengembalikan list CVE unik."""
    text = f"{news_item.get('title', '')} {news_item.get('summary', '')}"

    matches = CVE_RE.findall(text)

    unique_cves = set()
    for year, seq in matches:
        unique_cves.add(f"CVE-{year}-{seq}")

    return list(unique_cves)
