---
title: Attendance Backend
emoji: 📊
colorFrom: gray
colorTo: green
sdk: docker
pinned: false
---
# AI Biometric Attendance System (v2.0)

A modular, production-level biometric attendance system with a **microservices-based architecture**. It uses:
- **FastAPI** for all server interfaces.
- **MediaPipe** for face landmarks and iris/eye extraction.
- **ONNXRuntime** for running ArcFace (face embeddings) and anti-spoofing classifiers.
- **SQLite** for database logs, records, and sessions.

## Project Structure

```text
├── app/
│   ├── config/          # Environment configuration
│   ├── database/        # SQLite schema and manager
│   ├── camera/          # Multi-camera background thread managers
│   ├── services/        # API clients for microservices
│   ├── pipeline/        # Verification workflow & Decision engine
│   ├── attendance/      # Attendance logic, check-in/out logic
│   ├── enrollment/      # Staff registration handlers
│   └── utils/           # Logging, image, and GPU utility helpers
│
├── services/
│   ├── face_service/    # Face recognition microservice (Port 8001)
│   ├── iris_service/    # Iris texture matching microservice (Port 8002)
│   └── liveness_service/# Anti-spoofing and blink detection (Port 8003)
│
├── scripts/             # Init DB, CLI enrollment, and testing scripts
└── main.py              # Root script to run all services concurrently
```

## Setup & Running

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python scripts/init_db.py
   ```

3. **Start All Services**:
   ```bash
   python main.py
   ```

4. **Access Swagger Documentation**:
   Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.
