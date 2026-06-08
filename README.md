# Artificial Civilization Architecture (ACA) OS - v1.3.2

[![License: MIT](https://img.shields.io/badge/License-MIT-06b6d4.svg)](https://opensource.org/licenses/MIT)
[![Framework: ROS 2](https://img.shields.io/badge/Framework-ROS_2_Jazzy-blue.svg)](https://docs.ros.org/)
[![Message Broker: Kafka](https://img.shields.io/badge/Infrastructure-Apache_Kafka-orange.svg)](https://kafka.apache.org/)
[![Vector DB: Qdrant](https://img.shields.io/badge/Database-Qdrant_Vector-red.svg)](https://qdrant.tech/)
[![Time-Series DB: Timescale](https://img.shields.io/badge/Database-TimescaleDB-darkblue.svg)](https://www.timescale.com/)

---

**Conceptualized & Designed by:** `@ghalangwh.official`  
**Classification:** Open Research Manifesto & Production System Architecture  
**Status:** Conceptual Research Draft & Deployment Specification Base

> "Individual intelligence is temporary. Civilization intelligence is cumulative. Stop building chatbots. Start engineering robotic civilizations."

ACA OS (Artificial Civilization Architecture Operating System) adalah arsitektur sistem operasi hibrida cloud-to-edge untuk mengoordinasikan armada robot fisik di lapangan agar bergerak di bawah satu kesadaran peradaban kolektif yang kumulatif.

Proyek ini menolak status quo pengembangan AI modern yang terjebak pada pembesaran skala model tunggal atau bot kosmetik. ACA OS mengadopsi logika sosial ke tingkat instruksi mesin: pengetahuan diwariskan, kesalahan dicatat, dan generasi baru tidak memulai dari nol.

### Blueprint Reference

- [ACA Civilization Blueprint v1.0](docs/00_civilization_blueprint_v1.md)
- [Open Civilization Blueprint v1.3 - Cyber-Physical Robot OS Specs](docs/05_civilization_blueprint_v1_3_robot_os.md)
- [ACA Blueprint Changelog v1.0 to v1.3](docs/06_changelog_v1_to_v1_3.md)

### Docs Series

- `docs/00_civilization_blueprint_v1.md` - civilization foundation
- `docs/01_architecture_overview.md` - system architecture baseline
- `docs/02_mathematical_core.md` - reputation and dissent model
- `docs/03_security_threat_model.md` - threat model and mitigations
- `docs/04_data_contracts_schema.md` - telemetry payload contract
- `docs/05_civilization_blueprint_v1_3_robot_os.md` - robot OS spec from blueprint v1.3
- `docs/06_changelog_v1_to_v1_3.md` - version evolution summary

## 1. Arsitektur Komputasi: Cloud-to-Edge Stack

```text
[Server Pusat / Cloud Kernel Core]
├── Ingestion Queue      : Apache Kafka Cluster (Penyerapan data telemetri massal, zero packet loss)
├── Semantic Vector Store: Qdrant Cluster (HNSW Indexing untuk Skill & Spatial Memories)
├── Time-Series Ledger   : TimescaleDB (Audit forensik kinematik, log anomali, & mutasi reputasi)
└── Runtime Isolation    : gVisor Sandbox Container (Isolasi runtime host dari instruksi dinamis agen AI)
│
(Zenoh / MQTT Network Bridge via Wireless/Satellite Link)
│
[Perangkat Lapangan / Embedded Edge Stack]
├── Hardware Controller  : ROS 2 (Jazzy/Humble Node Drivers untuk LiDAR, Depth Camera, SLAM, & Servos)
├── Safety Filtering     : Hard-coded Kinematic Constraints Firmware (safety_gate di tingkat ROS 2)
└── Offline Resiliency   : Local Redis Cache (Penyimpanan salinan SOP keselamatan aktif saat offline)
```

## 2. Struktur Kontainer Proyek

```text
aca-civilization-os/
├── docs/
│   ├── 01_architecture_overview.md
│   ├── 02_mathematical_core.md
│   ├── 03_security_threat_model.md
│   └── 04_data_contracts_schema.md
├── aca-kernel-core/
│   ├── src/
│   │   ├── court/
│   │   ├── memory/
│   │   └── gateway/
│   ├── Dockerfile
│   └── docker-compose.yml
├── aca-edge-ros2/
│   ├── src/
│   │   ├── telemetry_bridge/
│   │   └── safety_gate/
│   └── config/
└── README.md
```

## 3. Matematika Peradaban: Kebijakan Epistemik & Reputasi

Untuk mencegah dominasi tirani mayoritas atau pembekuan inovasi radikal oleh agen berreputasi tinggi, ACA OS merombak logika makro sosialnya.

### A. Formula Pajak Reputasi Dinamis

- Agen atau robot dengan reputasi tinggi (`R_t >= 0.90`) otomatis dipotong reputasinya sebesar `alpha = 0.02` tiap siklus jika stagnan.
- Satu-satunya cara mempertahankan posisi elit adalah dengan melahirkan atau mensponsori inovasi baru (`Delta Frontier`).
- Agen generasi muda dibekali grace period untuk meredam penalti kegagalan selama fase eksplorasi awal.

### B. Sub-rutin Galileo & Dissenting Layers

Jika suatu penemuan taktis atau SOP baru ditolak oleh voting mayoritas pengadilan agen, objek tersebut tidak dihapus. Data dikunci sebagai `Dissenting Hypothesis` di klaster laboratorium AI University. Agen baru boleh menguji hipotesis ini dalam simulasi terisolasi. Jika terbukti lebih efisien, sistem memicu `Epistemic Revolution`.

## 4. Kontrak Data Komunikasi

### Ingestion Telemetry Payload (`aca.builder.telemetry`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RobotTelemetryPayload",
  "type": "object",
  "properties": {
    "robot_id": { "type": "string" },
    "timestamp": { "type": "integer" },
    "battery_voltage": { "type": "number" },
    "kinematics": {
      "type": "object",
      "properties": {
        "current_velocity_rps": { "type": "number" },
        "heading_deg": { "type": "number" }
      },
      "required": ["current_velocity_rps", "heading_deg"]
    },
    "spatial_anomaly": {
      "type": "object",
      "properties": {
        "detected": { "type": "boolean" },
        "vector_embedding_clip": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 128,
          "maxItems": 512
        }
      },
      "required": ["detected"]
    }
  },
  "required": ["robot_id", "timestamp", "battery_voltage", "kinematics", "spatial_anomaly"]
}
```

## 5. Keamanan Berlapis Tingkat Hardware

ACA OS menerapkan mitigasi brutal untuk mencegah instruksi cloud yang salah merusak perangkat fisik.

- **Strict Dual-LLM Gating:** memvalidasi seluruh teks input/output lewat checker deterministik di luar sandbox.
- **Cryptographic Provenance:** memverifikasi tanda tangan digital kunci privat agen pencipta pada setiap blok memori di Qdrant.
- **Firmware Safety Gate (`safety_gate`):** firmware memutus aliran perintah gerakan jika melanggar batas torsi statis mekanis dan memicu `SAFE_STATE_LOCK`.

## 6. Langkah Awal Memulai Infrastruktur Lokal

### Kebutuhan Sistem

- Docker
- Docker Compose
- Linux Ubuntu 22.04 LTS atau lebih baru

### Inisialisasi Klaster Pusat Cloud

1. Kloning repositori ini:
```bash
git clone git@github.com:ghalangwh-official/aca-civilization-os.git
cd aca-civilization-os/aca-kernel-core
```

2. Nyalakan seluruh infrastruktur:
```bash
docker-compose up -d
```

3. Pastikan port berikut aktif:
- Kafka broker: `9092`
- Qdrant Vector DB: `6333`
- TimescaleDB: `5432`

## 7. Undangan Terbuka untuk Kontributor

Proyek ini dilepas ke publik sebagai `Conceptual Research Draft`. Ini adalah undangan kolaborasi paradigma baru untuk memindahkan kecerdasan artifisial dari layar monitor menuju dunia fisik secara mandiri.

Kami mencari core-developer global di bidang:

- **Distributed Data Engineer:** manajemen partisi Kafka dan indexing Qdrant jarak jauh pada kondisi jaringan fluktuatif.
- **Embedded & Robotics Engineer:** optimasi node navigasi lokal ROS 2 dan penguatan logika kinematik kaku komponen `safety_gate`.
- **Cybersecurity Specialist:** audit enkripsi asimetris pada silsilah genetik `Knowledge DNA Schema`.

**An architecture conceptualized and designed by @ghalangwh.official.**  
For official inquiries, engineering collaborations, or hardware integration partnerships, please open an issue or reach out via official social media channels.
