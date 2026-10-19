# 🏙️ Municipal Camera Surveillance System
<img width="812" height="575" alt="Screenshot 2026-06-04 212336" src="https://github.com/user-attachments/assets/9e792071-d410-4aa6-8cf0-ddf49f56de23" />

An AI-powered multi-module urban camera analysis platform designed to be integrated into municipal infrastructure. It offers people counting, vehicle tracking, traffic density analysis, weather condition detection, and automatic license plate recognition (ANPR) from YouTube live streams and RTSP cameras via a central API.

---

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the System](#running-the-system)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Architecture Overview](#architecture-overview)
- [License](#license)

---

## System Overview

This system uses municipal camera infrastructure (RTSP) or public YouTube live streams as sources to perform real-time people counting, vehicle tracking, traffic density estimation, weather/visibility condition detection, and license plate recognition. All data is saved to PostgreSQL to generate minute/hourly/daily reports. The interface (HTML/C#) and API operate independently of each other.

---

## Features

### 👥 People Counting

**`1_yt_kisisayma.py`** — YouTube & RTSP people counter (full-featured)
- Real-time human detection with YOLOv8
- `yt-dlp` + `ffmpeg` pipeline for YouTube live streams
- RTSP camera support (TCP transport, automatic reconnection)
- Minute-based statistical records (instantaneous, average, maximum, minimum)
- Instant measurement every 10 seconds, batch recording at the end of each minute
- Graceful shutdown with signal management (SIGINT/SIGTERM)

**`2_yt_yari_kisisayma.py`** — Semi-optimized counter (memory-friendly)

**`3_ornek_mobes_kisisayma.py`** — Sample CCTV/MOBESE camera integration

**`4_ornek_mobes_Idli_kisisayma.py`** — ID-based (re-ID) people counting (prevents recounting the same person)

**`5_opt_yonlu_Idli_kisisayma.py`** — Direction-based (entry/exit) optimized counter

### 🌤️ Weather Condition Detection

**`6_havadurumu_tespiti_img.py`** — Weather condition analysis on images
- Zero-shot classification with OpenAI CLIP model (`clip-vit-base-patch32`)
- 7 weather categories: Sunny, Partly Cloudy, Cloudy, Rainy, Snowy/Foggy, Night, Low Visibility/Dirty Lens
- Percentage-based decision distribution in terminal output
- Camera lens smudging and view obstruction are also detected

**`7_havadurumu_tespiti_vid.py`** — Continuous weather tracking on video/live stream

### 🚗 Vehicle Tracking and Counting

**`9_aracTakip.py`** — Real-time vehicle counter
- Custom trained YOLOv8 model (`arac2.pt`)
- RTSP, YouTube, and local video support (resolved with `yt-dlp`)
- Separate classification and counting according to vehicle type
- Frame-based vehicle count overlay panel
- Summary report based on vehicle type at the end of the session
- Option to save output video

### 🚦 Traffic Density Analysis

**`10_trafik_yogunluk.py`** — Background subtraction-based traffic analysis
- Does not require a YOLOv8 model — works entirely with computer vision
- Automatic background learning (first 30 frames)
- Three-level classification (`CLEAR / NORMAL / HEAVY`) based on pixel change ratio
- Focus on the road area using ROI (Region of Interest) settings
- Real-time density chart in the bottom right corner
- Noise cleaning with CLAHE + morphological filter

### 🔢 License Plate Recognition (ANPR)

**`8_plaka_okuma.py`** — ANPR system for Turkish license plates
- Two-stage YOLOv8 pipeline: license plate detection (`plaka_bulma.pt`) + character recognition (`plaka_okuma.pt`)
- Image preprocessing: CLAHE, bilateral filter, unsharp masking, adaptive thresholding
- Smart OCR error correction (letter↔digit confusion: `0↔O`, `1↔I`, `8↔B`)
- Format validation according to Turkey's 81 city province codes
- Forbidden Turkish character check (İ, Ş, Ç, Ğ, Ü, Ö, Q, W, X)
- Exporting results to a JSON file

### 🌐 Central API

**`api.py`** — FastAPI-based 1139-line main hub
- Multi-camera management (registered in PostgreSQL)
- Minute/hourly/daily reports
- Live MJPEG video stream (vehicles + traffic)
- Real-time statistics stream with SSE (Server-Sent Events)
- Thread-based `StreamWorker` and `TrafikWorker` architecture
- License plate processing REST endpoint (file upload)
- Weather history and single query for all cameras
- CSV/JSON data export
- CORS middleware (web/mobile compatibility)

---

## Project Structure

```
Belediye-Kamera-Takip-Sistemi/
│
├── api.py                          # Main FastAPI application (central hub)
├── database.py                     # Database connection and operation class
├── database_test.py                # Database connection test script
│
├── 1_yt_kisisayma.py               # YouTube/RTSP people counter (full-featured)
├── 2_yt_yari_kisisayma.py          # Semi-optimized people counter
├── 3_ornek_mobes_kisisayma.py      # Sample MOBESE camera integration example
├── 4_ornek_mobes_Idli_kisisayma.py # ID-based people counter (re-ID)
├── 5_opt_yonlu_Idli_kisisayma.py   # Direction-based optimized counter
│
├── 6_havadurumu_tespiti_img.py     # Image weather detection (CLIP)
├── 7_havadurumu_tespiti_vid.py     # Video/live stream weather detection
│
├── 8_plaka_okuma.py                # Turkish license plate ANPR system
├── 9_aracTakip.py                  # Vehicle counter and tracker
├── 10_trafik_yogunluk.py           # Traffic analysis with background subtraction
│
├── Arayuz/                         # Web interface (HTML/C#)
└── README.md
```

---

## Technologies Used

| Layer | Technology |
|-------|------------|
| Language | Python 3.x |
| Image Processing | OpenCV, NumPy |
| Object/Vehicle/Plate Detection | YOLOv8 (Ultralytics) |
| Image Classification | Hugging Face Transformers (CLIP) |
| Video Stream Demuxing | yt-dlp, ffmpeg |
| Web API | FastAPI + Uvicorn |
| Real-Time Streaming | MJPEG (video), SSE (statistics) |
| Database | PostgreSQL |
| DB Driver | psycopg 3 |
| Web Interface | HTML + C# |

---

## Installation

### Prerequisites

```bash
pip install ultralytics opencv-python numpy
pip install fastapi uvicorn psycopg[binary] python-dotenv
pip install transformers torch pillow
pip install yt-dlp
```

> **Note:** `ffmpeg` must be installed in system PATH. Download: https://ffmpeg.org/download.html

### Model Files

Place the following model files in the project root directory:

| File | Usage |
|------|-------|
| `yolov8n.pt` | People counting (YOLO nano model) |
| `arac2.pt` | Vehicle detection and counting |
| `plaka_bulma.pt` | Find license plate on vehicle |
| `plaka_okuma.pt` | Read characters on license plate |

---

## Database Setup

### Create a database in PostgreSQL:

```sql
CREATE DATABASE belediye_kamera_db;
```

### Tables are automatically created when the system runs for the first time. To create them manually:

```sql
-- Camera definitions
CREATE TABLE kameralar (
    id SERIAL PRIMARY KEY,
    ad VARCHAR(100),
    konum VARCHAR(200),
    rtsp_url TEXT,
    aktif BOOLEAN DEFAULT true,
    olusturma_tarihi TIMESTAMP DEFAULT NOW()
);

-- Minute measurements
CREATE TABLE dakikalik_olculer (
    id SERIAL PRIMARY KEY,
    kamera_id INTEGER REFERENCES kameralar(id),
    baslangic_zamani TIMESTAMP,
    bitis_zamani TIMESTAMP,
    toplam_kisi INTEGER,
    ortalama_kisi FLOAT,
    maksimum_kisi INTEGER,
    minimum_kisi INTEGER,
    detaylar JSONB
);

-- Instant measurements
CREATE TABLE anlik_olcumler (
    id SERIAL PRIMARY KEY,
    kamera_id INTEGER REFERENCES kameralar(id),
    olcum_zamani TIMESTAMP DEFAULT NOW(),
    anlik_kisi INTEGER
);

-- Weather records
CREATE TABLE hava_durumu (
    id SERIAL PRIMARY KEY,
    kamera_id INTEGER REFERENCES kameralar(id),
    durum VARCHAR(50),
    guven_orani FLOAT,
    tespit_zamani TIMESTAMP DEFAULT NOW()
);
```

### Connection Configuration:

The database connection in the project is defined inside `database.py` and `api.py`. Update it according to your own server:

```python
PG_CONFIG = {
    'host': 'localhost',
    'database': 'belediye_kamera_db',
    'user': 'postgres',
    'password': 'YOUR_PASSWORD',
    'port': 5432
}
```

---

## Running the System

### 1. Start the API Server

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Swagger documentation: `http://localhost:8000/docs`

### 2. Add Camera to System

Add a YouTube live stream or RTSP camera while the API is running:

```bash
# To add YouTube live stream:
curl -X POST "http://localhost:8000/youtube-ekle?ad=Merkez+Meydani&konum=Merkez&youtube_url=https://youtube.com/watch?v=..."

# Real RTSP camera:
# Update the rtsp_url field with the camera IP address
```

### 3. Start People Counting

```bash
# Counting from YouTube:
python 1_yt_kisisayma.py

# To change source type in the file:
# KAYNAK_TIPI = "youtube"  # or "rtsp"
# YOUTUBE_URL = "https://www.youtube.com/watch?v=..."
# RTSP_URL = "rtsp://kamera.belediye.gov.tr:554/stream"
# KAMERA_ID = 1  # Camera ID in database
```

### 4. Start Vehicle Tracking

```bash
python 9_aracTakip.py
# You will be asked to enter RTSP or YouTube URL when the program starts
```

### 5. Start Traffic Density Analysis

```bash
python 10_trafik_yogunluk.py
# You will be asked to enter HLS (m3u8) or RTSP URL when the program starts
```

### 6. Weather Condition Detection

```bash
# On an image:
python 6_havadurumu_tespiti_img.py
# Update FOTOGRAF_YOLU variable in the file

# On video/live stream:
python 7_havadurumu_tespiti_vid.py
```

### 7. License Plate Recognition

```bash
python 8_plaka_okuma.py
# Put test images into TEST_FOLDER directory
# Results will be written to results/plaka_sonuclari.json file
```

---

## API Documentation

### Camera Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/kameralar` | List all active cameras |
| GET | `/api/kameralar` | Camera list in API format |
| POST | `/youtube-ekle` | Add new YouTube/RTSP camera |

### People Counting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/son-dakika/{kamera_id}` | Last minute measurement |
| GET | `/api/son-dakika?kamera_id=1` | Last minute measurement in API format |
| GET | `/canli/{kamera_id}` | Last 10 instant measurements |
| GET | `/api/canli-veri?kamera_id=1` | Live data in API format |
| GET | `/tum-dakikalar/{kamera_id}` | All minute records |
| GET | `/saatlik-rapor/{kamera_id}?tarih=2025-01-01` | Hourly summary |
| GET | `/gunluk-rapor/{kamera_id}?baslangic=...&bitis=...` | Daily report |
| GET | `/veri-export/{kamera_id}?format=csv` | CSV/JSON data export |

### Vehicle Tracking

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/arac-video-stream?kaynak=URL` | MJPEG live video stream |
| GET | `/api/arac-istatistik-stream?kaynak=URL` | SSE statistics stream |
| DELETE | `/api/arac-stream-durdur?kaynak=URL` | Stop stream and save |

### Traffic Density

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trafik-stream?kaynak=URL` | MJPEG traffic analysis stream |
| GET | `/api/trafik-istatistik-stream?kaynak=URL` | SSE traffic statistics stream |
| DELETE | `/api/trafik-stream-durdur?kaynak=URL` | Stop traffic stream |

### Weather Condition

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hava-durumu/{kamera_id}` | Latest weather condition of a camera |
| GET | `/hava-durumu-gecmis/{kamera_id}?tarih=...` | Daily weather condition history |
| GET | `/hava-durumu-tum-kameralar` | Latest status of all cameras |
| GET | `/api/hava-durumu/son?kamera_id=1` | Latest status in API format |

### License Plate

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/plaka/isle` | Upload image, read plates |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and endpoint list |
| DELETE | `/veri-temizle/{gun}` | Clean up old records in the background |

---

## Database Schema

```
kameralar           → Registered camera definitions (RTSP URL, location, status)
dakikalik_olculer   → Minute-based people count (total, avg, max, min, details JSONB)
anlik_olcumler      → Instantaneous person count every 10 seconds
hava_durumu         → Weather/visibility condition records per camera
```

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                  api.py (FastAPI :8000)                      │
│   /kameralar  /canli  /saatlik  /arac-stream  /trafik-stream │
│   /hava-durumu  /plaka  /veri-export                         │
└────────┬──────────┬──────────┬──────────┬────────────────────┘
         │          │          │          │
    ┌────┘     ┌────┘     ┌────┘     ┌────┘
    ▼          ▼          ▼          ▼
 People     StreamWorker TrafikWorker Plate
Counting   (vehicle,MJPEG)(traffic,MJPEG) System
 (YOLO)     (thread)   (thread)     (2x YOLO)
    │          │          │          │
    └──────────┴──────────┴──────────┘
                        │
                    PostgreSQL
               (belediye_kamera_db)
```

All stream workers run independently in background threads. The API's async loop is non-blocking. A single worker instance runs for each source URL; multiple clients share the same stream.

---

## License

This project was developed for educational purposes.
