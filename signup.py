"""
Flower Shop Signup API using FastAPI.

This module provides endpoints to register new users, verify OTPs,
resend OTPs after 5 minutes, and list users. All data is stored in local
JSON files.

Author: Your Name
Date: 2025-06-19
"""

import os
import re
import json
import time
import uuid
import random
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# File paths
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
OTPS_FILE = os.path.join(DATA_DIR, "otps.json")
os.makedirs(DATA_DIR, exist_ok=True)

def ensure_file_exists(file_path: str) -> None:
    """Make sure the JSON file exists, and create it with {} if missing."""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)


class UserCreate(BaseModel):
    """Schema for creating a user."""
    name: str
    email: str
    password: str


class OTPVerify(BaseModel):
    """Schema for verifying an OTP."""
    email: str
    otp: str


class ResendRequest(BaseModel):
    """Schema for requesting OTP resend."""
    email: str


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str


def load_data(file_path: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    ensure_file_exists(file_path)
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_data(file_path: str, data: Dict[str, Any]) -> None:
    """Save data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def is_strong_password(password: str) -> bool:
    """Check password strength."""
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password)
    )


def generate_otp() -> str:
    """Generate a 6-digit numeric OTP."""
    return ''.join(random.choices("0123456789", k=6))


@router.post("/signup")
def signup(user: UserCreate):
    """Register a new user and store OTP."""
    users = load_data(USERS_FILE)
    otps = load_data(OTPS_FILE)

    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered.")

    users[user.email] = {
        "id": str(uuid.uuid4()),
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "verified": False
    }
    save_data(USERS_FILE, users)

    otp = generate_otp()
    otps[user.email] = {
        "otp": otp,
        "timestamp": time.time()
    }
    save_data(OTPS_FILE, otps)

    print(f"[OTP] Your OTP for {user.email} is: {otp}")
    return {"message": "User registered. OTP sent to console."}


@router.post("/verify-otp")
def verify_otp(data: OTPVerify):
    """Verify the user's OTP."""
    otps = load_data(OTPS_FILE)

    if data.email not in otps:
        raise HTTPException(status_code=404, detail="No OTP found for this email.")

    if otps[data.email]["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    # Mark user as verified
    users = load_data(USERS_FILE)
    if data.email in users:
        users[data.email]["verified"] = True
        save_data(USERS_FILE, users)

    # Delete OTP
    del otps[data.email]
    save_data(OTPS_FILE, otps)

    return {"message": "OTP verified successfully. User is now verified."}


@router.post("/resend-otp")
def resend_otp(data: ResendRequest):
    """Resend OTP if 5 minutes have passed."""
    otps = load_data(OTPS_FILE)

    if data.email not in otps:
        raise HTTPException(status_code=404, detail="No OTP found. Please sign up again.")

    elapsed = time.time() - otps[data.email]["timestamp"]
    if elapsed < 300:
        remaining = int(300 - elapsed)
        raise HTTPException(
            status_code=403,
            detail=f"Wait {remaining} seconds before resending OTP."
        )

    otp = generate_otp()
    otps[data.email] = {
        "otp": otp,
        "timestamp": time.time()
    }
    save_data(OTPS_FILE, otps)

    print(f"[OTP] Resent OTP for {data.email}: {otp}")
    return {"message": "OTP resent. Check console."}


@router.post("/login")
def login(data: UserLogin):
    """Login a registered user."""
    users = load_data(USERS_FILE)
    user = users.get(data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user.get("verified"):
        raise HTTPException(status_code=403, detail="Email not verified. Please verify OTP first.")

    if user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Incorrect password.")

    return {"message": f"Login successful. Welcome {user['name']}!"}


@router.get("/users")
def list_users():
    """List all registered users."""
    users = load_data(USERS_FILE)
    return list(users.values())


@router.get("/verified-users")
def get_verified_users():
    """List users who are verified."""
    users = load_data(USERS_FILE)
    return [u for u in users.values() if u.get("verified") is True]


@router.get("/")
def home():
    """API welcome message."""
    return {"message": "🌼 Welcome to Flower Shop Signup API 🌼"}

from fastapi import Path

@router.delete("/delete-user/{email}")
def delete_user(email: str = Path(..., description="Email of the user to delete")):
    """Delete a user by email."""
    users = load_data(USERS_FILE)

    if email not in users:
        raise HTTPException(status_code=404, detail="User not found.")

    del users[email]
    save_data(USERS_FILE, users)

    return {"message": f"User with email {email} has been deleted."}

