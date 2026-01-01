# Nepal ID Verifier

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![License](https://img.shields.io/badge/License-MIT-green)

A production-grade microservice for automated Nepali Citizenship verification using Hybrid AI.

---

## Introduction

**Nepal ID Verifier** digitizes the KYC process by extracting and verifying data from Citizenship Certificates in real-time.

Refactored from a prototype into a scalable architecture, it utilizes **YOLOv8** for smart detection and **PaddleOCR** for high-precision bilingual extraction (English & Nepali). The system handles cross-calendar conversion (AD/BS) and phonetic matching to ensure accurate verification.


## Key Features

- 🚀 **Production Architecture:** Fully containerized with Docker & PostgreSQL.
- 🧠 **Smart Extraction:** Hybrid pipeline (YOLOv8 + PaddleOCR v5) for bilingual text.
- 📅 **Date Logic:** Automated conversion and verification between Gregorian (AD) and Bikram Sambat (BS).
- 🛡️ **Fuzzy Matching:** Phonetic skeleton analysis to handle spelling variations.
- ⚡ **High Performance:** Optimized inference engine (< 3s average latency).

## Tech Stack

- **Core:** Python 3.10, FastAPI, Gunicorn
- **ML:** Ultralytics YOLOv8, PaddleOCR (Headless)
- **Database:** PostgreSQL, SQLAlchemy
- **Infrastructure:** Docker, Docker Compose

## Quick Start

Run the entire system (API + Database) with a single command.

```bash
# 1. Clone the repository
git clone https://github.com/manjil-budhathoki/nepal-id-verifier.git
```

```bash
cd nepal-id-verifier
```

# 2. Start services

```bash
docker compose up --build
```

The API will be live at: `http://localhost:8000`

## API Documentation

Interactive Swagger documentation is available out-of-the-box.

- **Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

**Developed by Manjil Budhathoki**