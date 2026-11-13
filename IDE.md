nama : "Notifier"

1. Pendahuluan & Masalah.
Ide project ini bermula dari kekhawatiran saya terkait lambatnya organisasi maupun instansi pemerintah di Indonesia menyadari informasi terbaru di dunia keamanan siber(Cybersecurity), seperti informasi celah keamanan terbaru (Zero Day), Malware, teknik ancaman baru, dan sebagainya. Contoh nyata dari masalah tersebut dapat saya lihat langsung dengan indra saya sendiri di sebuah forum webinar resmi dari instansi BSSN(Badan Siber Dan Sandi Negara). Dalam forum tersebut terdapat peserta yang berasal dari instansi pemerintah tertentu mennyampaikan aspirasinya saat sesi tanya jawab dengan pakar bahwa instansi mereka sangat lambat dalam mengetahui informasi terbaru(kurang update). 

2. Konsep & Cara kerja.
Ide ini sangatlah relevan dengan masalah yang dibahas sebelumnya karena akan sangat memmbantu setiap organisasi maupun instansi dalam memantau perkembangan informasi tentang keamanan siber dan celah keamamanan terbaru.

Berikut adalah alur kerjanya
```
Berita masuk (title, summary, link, published, authors)
        │
        ▼
Scan teks title & summary dengan regex
        │
        ├── Ketemu "CVE-2026-XXXX"  ──▶ diperlakukan sebagai IOC
        │
        └── Tidak ada CVE tapi ada sinyal 0day
            (mis. "zero-day", "actively exploited", "no patch")
                                     ──▶ juga diperlakukan sebagai IOC
        │
        ▼
Alert dikirim (CVE/0day terdeteksi)
        │
        ▼
Cek ke DB CVE → ambil detail (deskripsi, CVSS, CPE, dll)
        │
        ▼
Cocokkan dengan tech stack user
        │
        ├── Cocok  ──▶ alert relevan / prioritas tinggi
        └── Tidak  ──▶ suppress atau prioritas rendah
```

Jadi simplenya kita ambil data dari rss/sumber berita terverifikasi seperti The Hacker News, lalu filed title dan summary dari respons json di scan menggunakan regex untuk mencari apakah sekiranya ada kata2 yang mengandung id CVE seperti CVE-2026-XXXXX atau cve 2026 xxxx, dan kalau misal ada maka akan di kirim ke fungsi yang bertugas untuk mencocokan id cve dengan database resmi seperti nvd, cve.org, dan lainnya. Dan jika dari id tersebut ter indikasi ada teknologi yang kita gunakan terdampak celah keamanan maka akan mengirimkan alert berupa email ke kita sebagai user.  

3. Teknologi yang digunakan.
Python.
