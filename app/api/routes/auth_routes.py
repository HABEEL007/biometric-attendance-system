from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# For this demo, we use a static mock token and hardcoded credentials.
# In production, replace this with PyJWT, password hashing (e.g. passlib), and DB lookups.
MOCK_TOKEN = "mock-jwt-token-12345"

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    if request.email == "admin@bioattendance.com" and request.password == "admin123":
        return LoginResponse(
            access_token=MOCK_TOKEN,
            token_type="bearer",
            user={
                "name": "Admin User",
                "email": request.email,
                "role": "Administrator"
            }
        )
    raise HTTPException(status_code=401, detail="Invalid credentials. Please use the demo login provided.")

@router.post("/signup", response_model=LoginResponse)
def signup(request: SignupRequest):
    # In a real app, you would hash the password and save to a DB here.
    # For now, we simulate success and return a mock token.
    return LoginResponse(
        access_token=MOCK_TOKEN,
        token_type="bearer",
        user={
            "name": request.name,
            "email": request.email,
            "role": "Administrator"
        }
    )
