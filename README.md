# 🚨 Notifyme

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Lisensi](https://img.shields.io/badge/Lisensi-MIT-green)
![paket](https://img.shields.io/badge/paket-uv-DE5FE9)
![database](https://img.shields.io/badge/database-SQLite-003B57?logo=sqlite&logoColor=white)
![sumber](https://img.shields.io/badge/sumber-The%20Hacker%20News-C8102E)
![enrichment](https://img.shields.io/badge/enrichment-vulnx-orange)
![powered by](https://img.shields.io/badge/powered_by-OSINT-red)

---

> ⚡ Setiap hari ratusan CVE baru muncul. Beberapa di antaranya **sedang dieksploitasi aktif** saat kamu membaca kalimat ini. Pertanyaannya bukan *"kenapa terjadi?"* — tapi *"siapa yang tahu duluan: kamu, atau penyerangnya?"*

---

## 🎯 Mengapa ini ada

Ini dimulai dari observasi lapangan yang menyengat: saat forum resmi BSSN (Badan Siber dan Sandi Negara), seorang peserta dari instansi pemerintah jujur di sesi tanya jawab — instansinya **sangat lambat** mengetahui informasi keamanan terbaru. Sementara itu, zero-day yang sedang dibicarakan publik mungkin sudah lama beredar. ([konsep lengkap → IDE.md](IDE.md))

Fakta lapangannya sederhana: **asimetri informasi adalah keuntungan penyerang.** Berita keamanan publik itu gratis, real-time, dan melimpah — tapi hanya berguna kalau sampai ke orang yang tepat sebelum jendela eksploitasi terbuka. Notifyme menutup celah itu dengan pipeline minimalis:

> **OSINT feed → triage IOC → enrichment → breach notification.**
> Empat tahap. Nol biaya lisensi. Inbox kamu sebagai output.

## 🔥 Yang bikin ini beda

- 🛰️ **IOC-first.** Berita dipindai sebagai sumber IOC — setiap nomor CVE (`CVE-2026-XXXXX`, termasuk variasi penulisan aneh seperti `cve 2026 xxxxx` atau tanda hubung unicode) jadi sinyal yang bisa ditindaklanjuti.
- 🕸️ **KEV-aware & PoC-aware.** Alert-nya gak cuma bilang "ada CVE" — dia nunjukin CVSS, severity, status **KEV** (diketahui dieksploitasi aktif), dan **berapa banyak PoC publik** yang beredar. Angka itu bedanya antara "catat dulu" dan "patch SEKARANG".
- 🔁 **Idempoten by design.** URL artikel unik, `cve_id` unik. CVE yang sama gak pernah alert dua kali. Bisa dijalankan tiap menit tanpa banjir notifikasi.
- 🗄️ **Zero third-party data flow.** Intelijen tersimpan di SQLite lokal — rekam jejak yang bisa di-forensik dan diaudit. Data kamu gak lewat cloud siapa pun selain SMTP-mu sendiri.
- 🧩 **Modular kill chain.** Fetch, extract, persist, enrich, notify — tiap tahap satu modul kecil di `src/`. Ganti sumber, ganti kanal alert, upgrade regex: semuanya terisolasi.
- ⚡ **Three-dependency footprint.** `feedparser` + `yagmail` + `dotenv`. Cukup ringan buat VPS paling murah yang bisa kamu sewa.

## ⚙️ Kill chain-nya

```
   ┌──────────────────────────────────────┐
   │  SOURCE: RSS The Hacker News         │  ← OSINT feed, gratis
   └──────────────────┬───────────────────┘
                      ▼
        [ TRIAGE ] regex scan: cari IOC "CVE-XXXX-XXXXX"
                      │
      ┌── tanpa IOC ──┴── IOC ditemukan ──┐
      ▼                                   ▼
 berita berikutnya            [ PERSIST ] SQLite
                              dedup: URL unik + CVE unik
                                        │
                          baru? ────────┴──── sudah ada?
                            │                   │
                            ▼                   ▼
                    [ ENRICH ] vulnx         no-op (anti-dup)
                    deskripsi · CVSS
                    severity · KEV · PoC
                            │
                            ▼
                    [ NOTIFY ] 📧 email
                    "🚨 THREAT INTEL: CVE-... Terdeteksi!"
```

**Pipeline-nya di kode:**

| Tahap | Modul | Peran |
| --- | --- | --- |
| SOURCE | `src/fetch_news.py` | Parsing RSS The Hacker News via `feedparser` |
| TRIAGE | `src/extraktor.py` | Regex ekstraksi IOC (CVE) dari judul + ringkasan |
| PERSIST | `src/db.py` | SQLite: `articles`, `vuln_events`, relasi `article_vuln_events` |
| ENRICH | `src/enricher.py` | Panggil CLI `vulnx` (timeout 30s) → CVSS, severity, KEV, PoC |
| NOTIFY | `src/notify.py` | Email alert via `yagmail` |
| ORCHESTRATE | `main.py` | Jalankan seluruh siklus sekali eksekusi |

## 🛠️ Deploy

### Ambil + pasang

```bash
# dengan uv (disarankan)
git clone https://github.com/GMJayy/Notifyme.git
cd Notifyme
uv sync

# atau dengan pip
pip install -r req.txt
```

### Konfigurasi kanal alert

```bash
cp .env.example .env
```

| Variabel | Contoh | Keterangan |
| --- | --- | --- |
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP keluar |
| `SMTP_PORT` | `587` | 587 = STARTTLS · 465 = SSL |
| `SMTP_SENDER` | `email.example@gmail.com` | identitas pengirim |
| `SMTP_PASSWORD` | *(App Password)* | 🔑 bukan password akun — App Password |
| `SMTP_RECEIVER` | `soc@target.com` | tujuan alert |

> 🔐 **OPSEC note:** `.env` berisi kredensial dan sudah masuk `.gitignore`. Jangan pernah mengeksposnya — bukan cuma di commit, tapi juga di screenshot.

### Jalankan

```bash
uv run main.py
```

Output-nya kira-kira begini:

```
Menyiapkan database...
Mengambil berita dari The Hacker News...
Berhasil mengambil 20 berita. Memproses...

[*] Mengambil detail CVE-2026-XXXXX dari vulnx...
[ALERT] Ditemukan ['CVE-2026-XXXXX']
        -> Critical Pre-Auth Flaw Can Crash Lagging Servers
Selesai! Total 1 CVE baru diproses dan di-enrich.
```

### Patroli otomatis — systemd timer ⏱️

**1 — Service** · `/etc/systemd/system/notifyme.service`
*(sesuaikan `WorkingDirectory` dengan lokasi clone kamu)*

```ini
[Unit]
Description=Notifyme — threat intel scanner (satu siklus)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/Notifyme
ExecStart=/opt/Notifyme/.venv/bin/python main.py
StandardOutput=append:/opt/Notifyme/notify.log
StandardError=append:/opt/Notifyme/notify.log

# hardening ringan
NoNewPrivileges=true
PrivateTmp=true
```

**2 — Timer** · `/etc/systemd/system/notifyme.timer`

```ini
[Unit]
Description=Patroli Notifyme tiap 30 menit

[Timer]
OnCalendar=*:0/30
Persistent=true
Unit=notifyme.service

[Install]
WantedBy=timers.target
```

**3 — Aktifkan**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now notifyme.timer

# verifikasi
systemctl list-timers notifyme.timer    # jadwal & trigger berikutnya
journalctl -u notifyme.service -n 50    # hasil eksekusi terakhir
```

**Contekan `OnCalendar`:**

| Pattern | Arti |
| --- | --- |
| `*:0/30` | tiap 30 menit |
| `hourly` / `daily` / `weekly` | alias bawaan: tiap jam / hari / minggu |
| `*-*-* 08,20:00:00` | dua kali sehari — 08:00 & 20:00 |
| `Mon..Fri *-*-* 09:00:00` | hari kerja jam 09:00 |

> Note: Tanpa `vulnx` pun pipeline tetap jalan — alert tetap terkirim, hanya tanpa detail CVE. Tapi jelas: dengan enrichment, kualitas intelijennya naik kelas.

## 📜 Lisensi

[MIT](LICENSE) — pakai, modifikasi, deploy. Sekian.
