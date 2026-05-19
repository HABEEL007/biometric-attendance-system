-- Enable Foreign Key Support
PRAGMA foreign_keys = ON;

-- 1. Staff table
CREATE TABLE IF NOT EXISTS staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT,
    department TEXT,
    shift_start_time TEXT, -- HH:MM format
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Face Embeddings table
CREATE TABLE IF NOT EXISTS face_embeddings (
    embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    embedding BLOB NOT NULL, -- Binary serialized numpy float32 array
    embedding_dimension INTEGER DEFAULT 512,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE
);

-- 3. Iris Templates table
CREATE TABLE IF NOT EXISTS iris_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    left_eye_template BLOB, -- Binary serialized left iris features
    right_eye_template BLOB, -- Binary serialized right iris features
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE
);

-- 4. Attendance Sessions table
CREATE TABLE IF NOT EXISTS attendance_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL, -- YYYY-MM-DD
    current_status TEXT NOT NULL CHECK(current_status IN ('IN', 'OUT')),
    first_check_in TEXT, -- YYYY-MM-DD HH:MM:SS
    last_check_out TEXT, -- YYYY-MM-DD HH:MM:SS
    total_work_minutes REAL DEFAULT 0.0,
    total_break_minutes REAL DEFAULT 0.0,
    is_late INTEGER DEFAULT 0,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE,
    UNIQUE(staff_id, attendance_date)
);

-- 5. Attendance Records table
CREATE TABLE IF NOT EXISTS attendance_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER, -- Can be NULL for unknown people
    session_id INTEGER, -- Can be NULL if registration fails or unknown
    event_type TEXT CHECK(event_type IN ('CHECK_IN', 'CHECK_OUT', 'REJECTED')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    face_score REAL,
    iris_score REAL,
    liveness_score REAL,
    final_confidence REAL,
    snapshot_path TEXT,
    camera_id TEXT,
    status TEXT NOT NULL CHECK(status IN ('APPROVED', 'REJECTED')),
    reject_reason TEXT,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE SET NULL
);

-- 6. Liveness Logs table
CREATE TABLE IF NOT EXISTS liveness_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER,
    blink_detected INTEGER, -- 1 = Yes, 0 = No
    head_movement_detected INTEGER,
    spoof_probability REAL,
    liveness_score REAL,
    attack_type TEXT,
    decision TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE SET NULL
);

-- 7. Raw Detection Logs table (debugging)
CREATE TABLE IF NOT EXISTS raw_detection_logs (
    raw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id TEXT,
    person_detected INTEGER,
    face_detected INTEGER,
    face_score REAL,
    iris_score REAL,
    liveness_score REAL,
    final_decision TEXT,
    frame_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
