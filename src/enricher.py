import subprocess
import json

from src.db import get_unenriched_cves, save_enrichment


def enrich_single_cve(cve_id: str) -> dict | None:
    """Mengambil detail satu CVE dari vulnx."""
    try:
        result = subprocess.run(
            ["vulnx", "id", cve_id, "-j", "--silent"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        data = json.loads(result.stdout)

        if isinstance(data, dict):
            return data
        elif isinstance(data, list) and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"[ERROR] Gagal menjalankan vulnx untuk {cve_id}: {e}")
        return None

def enrich_cves():
    """Fungsi batch untuk CVE lama yang belum ter-enrich (opsional)."""
    cves = get_unenriched_cves()
    if not cves:
        return

    print(f"[INFO] Memproses enrichment untuk {len(cves)} CVE...")
    for cve_id in cves:
        vuln_data = enrich_single_cve(cve_id)
        if vuln_data:
            save_enrichment(cve_id, vuln_data)
            print(f"[OK] {cve_id} berhasil di-enrich (Severity: {vuln_data.get('severity', 'N/A')})")
