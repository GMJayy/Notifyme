import os
from dotenv import load_dotenv

from src.fetch_news import FetchNews
from src.extraktor import extract_ioc
from src.db import init_db, save_to_db, save_enrichment
from src.notify import send_email_alert
from src.enricher import enrich_single_cve

load_dotenv()

def main():
    print("Menyiapkan database...")
    init_db()

    print("Mengambil berita dari The Hacker News...")
    news_list = FetchNews().the_hacker_news()

    if not news_list:
        return

    print(f"Berhasil mengambil {len(news_list)} berita. Memproses...\n")

    total_cve = 0
    for news in news_list:
        cves = extract_ioc(news)

        if cves:
            new_cves = save_to_db(news, cves, source="TheHackerNews")

            if new_cves:
                for cve in new_cves:
                    print(f"[*] Mengambil detail {cve} dari vulnx...")

                    vuln_data = enrich_single_cve(cve)
                    if vuln_data:
                        save_enrichment(cve, vuln_data)

                    send_email_alert(news, cve, vuln_data)

                total_cve += len(new_cves)
                print(f"[ALERT] Ditemukan {new_cves}")
                print(f"        -> {news.get('title')}\n")

    print(f"Selesai! Total {total_cve} CVE baru diproses dan di-enrich.")

if __name__ == "__main__":
    main()
