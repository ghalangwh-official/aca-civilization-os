# ACA Gap Analysis and Next Steps

Dokumen ini merangkum kekurangan yang masih tersisa di repositori ACA setelah upgrade terakhir. Tujuannya bukan untuk mengecilkan progres, tetapi untuk membuat status proyek jujur, terukur, dan mudah diprioritaskan di GitHub.

## Ringkasan Status

- Visi dan dokumentasi sudah kuat.
- Cloud ingestion gateway sudah functional dan teruji.
- Memory, court, dan audit trail sudah ada dalam bentuk minimal.
- Edge logic untuk telemetry bridge dan safety gate sudah ada, tetapi belum terhubung penuh ke runtime ROS 2 hidup.
- Beberapa area masih berupa scaffold atau belum punya jalur deployment production-grade.

## Kekurangan Utama

### 1. ROS 2 Runtime Belum Live

**Status saat ini**

- `telemetry_bridge` dan `safety_gate` punya logic Python yang bisa dites.
- Launch file dan package layout sudah mulai disiapkan.
- Integrasi dengan ROS 2 runtime asli belum diverifikasi di hardware atau simulator.

**Gap**

- belum ada subscriber/publisher ROS 2 yang benar-benar terhubung ke sensor stream
- belum ada demo menjalankan node ROS 2 secara penuh
- belum ada validasi topic, QoS, dan lifecycle node di runtime asli

**Dampak**

- edge stack masih terasa seperti scaffold yang rapi, bukan sistem robot yang matang

**Next step**

- wiring `rclpy` end-to-end
- test publish/subscribe minimal
- buat launch yang benar-benar bisa jalan di device target atau simulator

### 2. Observability Masih Minim

**Status saat ini**

- ada logging dasar di gateway
- ada test suite lokal
- belum ada metrics service atau dashboard

**Gap**

- belum ada metrik ingest rate
- belum ada metrik parse failure, DB failure, or broker reconnect
- belum ada health endpoint atau readiness surface

**Dampak**

- debugging produksi akan lebih lambat
- sulit menilai apakah pipeline benar-benar stabil

**Next step**

- tambah structured metrics
- tampilkan status service per komponen
- buat dashboard sederhana atau export format Prometheus

### 3. Fault Tolerance Kafka/DB Belum Lengkap

**Status saat ini**

- ada retry dasar saat broker/database belum siap
- consumer sudah handle beberapa error parsing

**Gap**

- belum ada circuit breaker formal
- belum ada backoff policy yang terukur
- belum ada strategi reprocessing atau dead-letter queue

**Dampak**

- kalau broker flapping atau DB tidak stabil, recovery masih terlalu sederhana

**Next step**

- implement circuit breaker
- tambah dead-letter path untuk payload yang rusak
- dokumentasikan recovery behavior

### 4. Persistence Masih Minimal

**Status saat ini**

- memory dan court sudah punya JSONL audit trail lokal
- Qdrant masih best-effort

**Gap**

- belum ada persistence terstruktur untuk semua entitas ACA
- belum ada migration atau schema versioning
- belum ada export/import resmi untuk memory history

**Dampak**

- bagus untuk prototyping, tapi belum cukup untuk deployment jangka panjang

**Next step**

- tambah schema/versioning
- sinkronkan memory dan court ke audit ledger yang lebih formal
- siapkan backup/export tool

### 5. Service/API Boundary Belum Ekspos

**Status saat ini**

- ada `CivilizationService` sebagai boundary internal
- belum ada HTTP API atau local daemon wrapper

**Gap**

- belum ada service interface yang bisa dipakai UI, CLI lain, atau dashboard
- belum ada auth atau transport layer untuk external access

**Dampak**

- integrasi komunitas masih harus import file Python langsung

**Next step**

- expose service boundary lewat local API
- tambah command surface yang konsisten
- pisahkan core logic dari transport

### 6. Community Workflow Belum Lengkap

**Status saat ini**

- sudah ada CONTRIBUTING, roadmap, dan issue templates
- belum ada project board nyata atau issue tracking yang terisi

**Gap**

- belum ada milestone resmi
- belum ada issue breakdown prioritas
- belum ada labels dan board yang benar-benar dipakai

**Dampak**

- kontribusi eksternal masih akan bingung harus mulai dari mana

**Next step**

- buka issue milestone
- isi board backlog
- label pekerjaan menjadi cloud, edge, docs, tests, safety

### 7. Benchmarks Belum Formal

**Status saat ini**

- ada test unit dan smoke demo
- belum ada benchmark kuantitatif

**Gap**

- belum ada target latency ingest
- belum ada target memory retrieval
- belum ada target safety rejection precision/recall

**Dampak**

- sulit membuktikan peningkatan kualitas secara objektif

**Next step**

- definisikan benchmark minimum
- simpan baseline hasil pengujian
- bandingkan versi antar rilis

## Prioritas Pengerjaan

### P0

- ROS 2 runtime live wiring
- metrics / observability
- fault tolerance untuk ingest pipeline

### P1

- service/API boundary
- formal persistence/versioning
- benchmark harness

### P2

- komunitas: issue board, milestones, labels
- release packaging yang lebih rapi
- export/import tool untuk knowledge base

## Kesimpulan

ACA sekarang sudah melewati fase "hanya blueprint".

Namun, untuk naik dari 9.1 ke 9.5+, proyek ini masih perlu:

- runtime edge yang benar-benar hidup
- observability yang terukur
- recovery behavior yang lebih matang
- cara akses service yang lebih formal
- kontribusi komunitas yang lebih terstruktur

Ini adalah gap yang sehat, bukan kegagalan. Artinya proyek sudah cukup matang untuk dikritik secara teknis, dan itu justru tanda bahwa fondasinya mulai kuat.
