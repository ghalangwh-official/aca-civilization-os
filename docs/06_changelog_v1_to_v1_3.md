# ACA Blueprint Changelog v1.0 to v1.3

Dokumen ini merangkum evolusi blueprint ACA dari versi konseptual awal sampai versi robot fisik yang paling akhir ditemukan di folder `downloads`.

## Scope

- `v1.0` adalah fondasi peradaban digital dan memory-driven civilization.
- `v1.3` adalah perluasan ke spesifikasi robot fisik, cloud-to-edge, dan safety hardware.
- File artefak `v1.1` dan `v1.2` memang ada di folder `downloads`, tetapi isi lengkapnya belum diekstrak ke repo ini. Karena itu, changelog di bawah menjaga detail hanya pada versi yang sudah terverifikasi.

## v1.0 - Civilization Core

Fokus utama:

- knowledge must outlive individuals
- agent lifecycle dan civilization structure
- memory layers
- reputation system
- confidence system
- school / university / court / government / hospital
- marketplace, economy, evolution lab, mentorship, recovery protocol, metrics
- physical integration masih berupa visi tingkat tinggi

Karakter v1.0:

- blueprint masih dominan sebagai kerangka peradaban digital
- belum terfokus pada robot fisik tertentu
- belum ada spesifikasi hardware edge yang rinci

## v1.1 - Intermediate Artifact

Status:

- ada sebagai artefak PDF terpisah di `downloads`
- isi lengkap belum dimigrasikan ke repo

Catatan:

- v1.1 diperlakukan sebagai versi transisi di antara blueprint awal dan perluasan berikutnya
- karena belum diekstrak penuh, dokumen ini tidak mengklaim detail spesifik v1.1

## v1.2 - Intermediate Epistemic Artifact

Status:

- ada sebagai artefak PDF terpisah di `downloads`
- isi lengkap belum dimigrasikan ke repo

Catatan:

- v1.2 diperlakukan sebagai iterasi penguatan epistemik di jalur menuju robot OS
- karena belum diekstrak penuh, dokumen ini tidak mengklaim detail spesifik v1.2

## v1.3 - Cyber-Physical Robot OS

Perubahan utama:

- ACA bergeser dari framework peradaban digital umum menjadi spesifikasi robot fisik
- edge stack berbasis `ROS 2` diperjelas sebagai runtime utama di perangkat lapangan
- bridge komunikasi `Zenoh` / `MQTT` ditetapkan untuk jaringan nirkabel yang tidak stabil
- cache lokal `Redis Light` / `SQLite` ditambahkan untuk offline resilience
- ingestion telemetry ke `Kafka` menjadi jalur resmi sinkronisasi pengetahuan fisik
- server pusat memvalidasi dan mengubah telemetri menjadi SOP baru
- sandbox `gVisor` mengisolasi logika dinamis dari aktuator fisik
- `Hard-coded Kinematic Constraints` menutup jalur perintah berbahaya ke hardware
- resource economy diperjelas:
  - battery and energy quota
  - bandwidth throttling
  - idle robot pruning
- manifest `agent_dna` v1.3 menambahkan metadata hardware, constraints, skill, reputation, dan cryptographic provenance
- roadmap MVP difokuskan pada validasi lab robot fisik

## Ringkasan Evolusi

- `v1.0`: peradaban digital, memory, governance, reputation
- `v1.1`: versi transisi
- `v1.2`: versi transisi epistemik
- `v1.3`: robot OS, edge safety, sync fisik, dan integrasi hardware

## Kesimpulan

- v1.0 memberi filosofi dan struktur inti
- v1.3 memberi bentuk operasional untuk robot fisik
- repo ini sekarang memakai v1.3 sebagai referensi terakhir untuk implementasi robotika, sambil mempertahankan v1.0 sebagai fondasi konseptual
