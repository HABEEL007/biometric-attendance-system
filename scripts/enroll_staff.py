import argparse
import base64
import requests
import json
from pathlib import Path

def image_to_base64(img_path: Path) -> str:
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description="CLI Tool to Enroll Staff into Biometric System")
    parser.add_argument("--id", required=True, help="Employee ID (e.g. EMP-101)")
    parser.add_argument("--name", required=True, help="Full Name of the employee")
    parser.add_argument("--role", default="Developer", help="Role / Title")
    parser.add_argument("--dept", default="Engineering", help="Department")
    parser.add_argument("--shift", default="09:00", help="Shift Start Time (HH:MM)")
    parser.add_argument("--faces-dir", required=True, help="Directory containing face images")
    parser.add_argument("--eyes-dir", required=True, help="Directory containing eye images")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Central Gateway URL")
    
    args = parser.parse_args()

    faces_path = Path(args.faces_dir)
    eyes_path = Path(args.eyes_dir)

    if not faces_path.exists():
        print(f"Error: Face images directory {faces_path} does not exist.")
        return
    if not eyes_path.exists():
        print(f"Error: Eye images directory {eyes_path} does not exist.")
        return

    # Find images
    face_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        face_images.extend(list(faces_path.glob(ext)))
    
    eye_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        eye_images.extend(list(eyes_path.glob(ext)))

    if not face_images:
        print("Error: No face images (.jpg, .jpeg, .png) found.")
        return
    if not eye_images:
        print("Error: No eye images (.jpg, .jpeg, .png) found.")
        return

    print(f"Loading {len(face_images)} face images...")
    face_payloads = [image_to_base64(p) for p in face_images]

    print(f"Loading {len(eye_images)} eye images...")
    eye_payloads = [image_to_base64(p) for p in eye_images]

    payload = {
        "employee_id": args.id,
        "name": args.name,
        "role": args.role,
        "department": args.dept,
        "shift_start_time": args.shift,
        "face_images": face_payloads,
        "eye_images": eye_payloads
    }

    enroll_url = f"{args.url}/enrollment/enroll"
    print(f"Sending enrollment request to {enroll_url}...")
    try:
        res = requests.post(enroll_url, json=payload, timeout=30.0)
        if res.status_code == 200:
            print("Enrollment successful!")
            print(json.dumps(res.json(), indent=2))
        else:
            print(f"Enrollment failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    main()
