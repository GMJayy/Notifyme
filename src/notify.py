import os

import yagmail


def send_email_alert(news_item: dict, cve_id: str, vuln_data: dict | None):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SMTP_SENDER")
    sender_password = os.getenv("SMTP_PASSWORD")
    receiver_email = os.getenv("SMTP_RECEIVER")

    if not all([sender_email, sender_password, receiver_email]):
        return

    subject = f"🚨 THREAT INTEL: {cve_id} Terdeteksi!"

    if vuln_data:
        desc = vuln_data.get("description", "Tidak ada deskripsi")
        severity = str(vuln_data.get("severity", "unknown")).upper()
        cvss = vuln_data.get("cvss_score", "N/A")
        is_kev = "YA (Aktif Dieksploitasi)" if vuln_data.get("is_kev") else "Tidak"
        is_poc = f"Ya ({vuln_data.get('poc_count', 0)} repositori)" if vuln_data.get("is_poc") else "Tidak"

        detail_text = f"""
    DETAIL CVE:
    Deskripsi : {desc}
    Severity  : {severity}
    CVSS Score: {cvss}
    Status KEV: {is_kev}
    Publik PoC: {is_poc}
        """
    else:
        detail_text = "\n    (Detail CVE belum tersedia di database vulnx)\n"

    body = f"""
    Peringatan! Sistem mendeteksi adanya indikator CVE pada berita terbaru.

    CVE       : {cve_id}
    Judul     : {news_item.get('title')}
    Link      : {news_item.get('link')}
    Tanggal   : {news_item.get('published')}
    {detail_text}
    """

    try:
        use_ssl = True if smtp_port == 465 else False
        yag = yagmail.SMTP(
            user=sender_email, password=sender_password, host=smtp_server,
            port=smtp_port, smtp_ssl=use_ssl, smtp_starttls=not use_ssl
        )
        yag.send(to=receiver_email, subject=subject, contents=body)
        yag.close()
        print(f"[INFO] Email alert {cve_id} berhasil dikirim.")
    except Exception as e:
        print(f"[ERROR] Gagal mengirim email: {e}")
