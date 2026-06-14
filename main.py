import subprocess
import sys
import time
import argparse
from pathlib import Path

def start_microservice(script_path: str, port: int, name: str):
    """Starts a microservice as a background subprocess."""
    print(f"Starting {name} service on port {port}...")
    cmd = [sys.executable, "-m", script_path]
    # Removed stdout=PIPE to prevent OS pipe buffer deadlock during heavy logging (e.g. model downloads)
    process = subprocess.Popen(cmd)
    return process

def main():
    parser = argparse.ArgumentParser(description="AI Biometric Attendance System Runner")
    parser.add_argument("--gateway-only", action="store_true", help="Start only the Central FastAPI Gateway")
    args = parser.parse_args()

    # Add project root to python path for all subprocesses
    root_dir = str(Path(__file__).resolve().parent)
    sys.path.append(root_dir)

    processes = []
    
    if args.gateway_only:
        # Just run Central Gateway synchronously
        import uvicorn
        from app.api.main import app
        from app.config.settings import settings
        print("Starting Central Gateway (Gateway-Only Mode)...")
        uvicorn.run(app, host=settings.CENTRAL_API_HOST, port=settings.CENTRAL_API_PORT)
        return

    try:
        # Start all AI microservices
        face_proc = start_microservice("services.face_service.main", 8001, "Face Recognition")
        processes.append((face_proc, "Face Service"))
        
        iris_proc = start_microservice("services.iris_service.main", 8002, "Iris Verification")
        processes.append((iris_proc, "Iris Service"))
        
        liveness_proc = start_microservice("services.liveness_service.main", 8003, "Liveness & Anti-Spoofing")
        processes.append((liveness_proc, "Liveness Service"))

        # Wait a moment for services to bind ports
        time.sleep(2)

        # Start Central Gateway in the main thread (blocking)
        print("Starting Central FastAPI Gateway...")
        import uvicorn
        from app.api.main import app
        from app.config.settings import settings
        
        # This blocks until server stops
        uvicorn.run(app, host=settings.CENTRAL_API_HOST, port=settings.CENTRAL_API_PORT)

    except KeyboardInterrupt:
        print("\nStopping all services...")
    finally:
        # Terminate background services
        for proc, name in processes:
            print(f"Terminating {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                print(f"Force-killing {name}...")
                proc.kill()
        print("All services stopped.")

if __name__ == "__main__":
    main()
