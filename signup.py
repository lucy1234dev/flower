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
from fastapi.responses import JSONResponse
from pydantic import BaseModel,EmailStr,Field

# Initialize FastAPI router for signup-related endpoints
router = APIRouter()

# File paths for data storage
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
OTPS_FILE = os.path.join(DATA_DIR, "otps.json")
os.makedirs(DATA_DIR, exist_ok=True)


def ensure_file_exists(file_path: str) -> None:
    """
    Make sure the JSON file exists, and create it with {} if missing.

    Args:
        file_path (str): Path to the JSON file to check/create.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class OTPVerify(BaseModel):
    """
    Schema for verifying an OTP.

    Attributes:
        email (str): User's email address.
        otp (str): One-time password to verify.
    """
    email: str
    otp: str


class ResendRequest(BaseModel):
    """
    Schema for requesting OTP resend.

    Attributes:
        email (str): User's email address to resend OTP to.
    """
    email: str


class UserLogin(BaseModel):
    """
    Schema for user login.

    Attributes:
        email (str): User's email address.
        password (str): User's password.
    """
    email: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters.")


class UserUpdate(BaseModel):
    """
    Schema for updating user details.

    Attributes:
        name (str): Updated user name.
        password (str): Updated user password.
    """
    name: str
    password: str


def load_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from a file, and create file if file is missing.

    Args:
        file_path (str): Path to the JSON file to load.

    Returns:
        Dict[str, Any]: Loaded data from JSON file or empty dict if file doesn't exist.
    """
    ensure_file_exists(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_data(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save data to a JSON file.

    Args:
        file_path (str): Path to the JSON file to save to.
        data (Dict[str, Any]): Data to save to the file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def is_valid_email(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email (str): Email address to validate.

    Returns:
        bool: True if email format is valid, False otherwise.
    """
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def is_strong_password(password: str) -> bool:
    """
    Check password strength requirements.

    Password must be at least 8 characters long and contain:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Args:
        password (str): Password to validate.

    Returns:
        bool: True if password meets strength requirements, False otherwise.
    """
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password)
    )


def generate_otp() -> str:
    """
    Generate a 6-digit numeric OTP.

    Returns:
        str: A 6-digit numeric string for OTP verification.
    """
    return ''.join(random.choices("0123456789", k=6))


@router.options("/signup")
async def signup_options():
    """
    Handle preflight OPTIONS request for signup endpoint.

    Returns:
        JSONResponse: Simple OK response for CORS preflight.
    """
    return JSONResponse({"message": "OK"})

@router.post("/signup")
def signup(user: UserCreate):
    """
    Register a new user and generate OTP for verification.

    Creates a new user account with unverified status and generates
    a 6-digit OTP for email verification. Allows re-registration
    for unverified users.

    Args:
        user (UserCreate): User registration data containing first_name, last_name, email, and password.

    Returns:
        dict: Response containing success message, OTP, and email.

    Raises:
        HTTPException: 400 error if email format is invalid or already verified.
    """
    print("[Frontend Signup Data]", user.dict())

    # Validate email format
    if not is_valid_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

    # Validate first and last names
    if not user.first_name.strip() or not user.last_name.strip():
        raise HTTPException(status_code=400, detail="First and last name cannot be empty.")

    # Validate password
    if not is_strong_password(user.password):
        raise HTTPException(status_code=400, detail="Password must contain uppercase, lowercase, and digit.")

    users = load_data(USERS_FILE)
    otps = load_data(OTPS_FILE)

    # Check if email already exists
    if user.email in users:
        if users[user.email].get("verified", False):
            raise HTTPException(
                status_code=400,
                detail="Email already registered and verified. Please login instead."
            )
        else:
            print(f"[INFO] Re-registering unverified user: {user.email}")

    # Register or update user
    users[user.email] = {
        "id": str(uuid.uuid4()),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "password": user.password,
        "verified": False
    }
    save_data(USERS_FILE, users)

    # Generate and store OTP
    otp = generate_otp()
    otps[user.email] = {
        "otp": otp,
        "timestamp": time.time()
    }
    save_data(OTPS_FILE, otps)

    print(f"[OTP] Your OTP for {user.email} is: {otp}")

    return {
        "message": "User registered successfully. OTP sent.",
        "otp": otp,
        "email": user.email
    }



@router.options("/verify-otp")
async def verify_otp_options():
    """
    Handle preflight OPTIONS request for verify-otp endpoint.

    Returns:
        JSONResponse: Simple OK response for CORS preflight.
    """
    return JSONResponse({"message": "OK"})


@router.post("/verify-otp")
def verify_otp(data: OTPVerify):
    """
    Verify the user's OTP and mark account as verified.

    Validates the provided OTP against stored OTP for the email.
    If valid, marks the user as verified and removes the OTP.

    Args:
        data (OTPVerify): OTP verification data containing email and OTP.

    Returns:
        dict: Success message confirming OTP verification.

    Raises:
        HTTPException: 404 if no OTP found, 400 if OTP is invalid.
    """
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

    # Delete OTP after successful verification
    del otps[data.email]
    save_data(OTPS_FILE, otps)

    return {"message": "OTP verified successfully. User is now verified."}


@router.options("/resend-otp")
async def resend_otp_options():
    """
    Handle preflight OPTIONS request for resend-otp endpoint.

    Returns:
        JSONResponse: Simple OK response for CORS preflight.
    """
    return JSONResponse({"message": "OK"})


@router.post("/resend-otp")
def resend_otp(data: ResendRequest):
    """
    Resend OTP if 5 minutes have passed since last OTP generation.

    Checks if enough time has elapsed (5 minutes) since the last OTP
    was generated. If so, generates and sends a new OTP.

    Args:
        data (ResendRequest): Request data containing email address.

    Returns:
        dict: Success message with new OTP.

    Raises:
        HTTPException: 404 if no OTP found, 403 if not enough time has passed.
    """
    otps = load_data(OTPS_FILE)

    if data.email not in otps:
        raise HTTPException(status_code=404, detail="No OTP found. Please sign up again.")

    elapsed = time.time() - otps[data.email]["timestamp"]
    if elapsed < 300:  # 300 seconds = 5 minutes
        remaining = int(300 - elapsed)
        raise HTTPException(
            status_code=403,
            detail=f"Wait {remaining} seconds before resending OTP."
        )

    # Generate new OTP
    otp = generate_otp()
    otps[data.email] = {
        "otp": otp,
        "timestamp": time.time()
    }
    save_data(OTPS_FILE, otps)

    print(f"[OTP] Resent OTP for {data.email}: {otp}")
    return {"message": "OTP resent. Check console.", "otp": otp}


@router.options("/login")
async def login_options():
    """
    Handle preflight OPTIONS request for login endpoint.

    Returns:
        JSONResponse: Simple OK response for CORS preflight.
    """
    return JSONResponse({"message": "OK"})


@router.post("/login")
def login(data: UserLogin):
    """
    Authenticate a registered and verified user.
    """
    if not data.password.strip():
        raise HTTPException(status_code=400, detail="Password cannot be empty.")

    users = load_data(USERS_FILE)
    user = users.get(data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user.get("verified"):
        raise HTTPException(status_code=403, detail="Email not verified. Please verify OTP first.")

    if user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Incorrect password.")

    return {"message": f"Login successful. Welcome {user['name']}!"}
    
@router.get("/login")
def login_info():
    """
    Provide information about login endpoint for GET requests.

    Returns:
        dict: Message instructing the user to use POST method.
    """
    return {"message": "Please use POST method to log in with your credentials."}


@router.get("/users")
def list_users():
    """
    List all registered users in the system.

    Returns:
        list: List of all user objects from the users database.
    """
    users = load_data(USERS_FILE)
    return list(users.values())


@router.get("/verified-users")
def get_verified_users():
    """
    List only users who have verified their email addresses.

    Returns:
        list: List of verified user objects only.
    """
    users = load_data(USERS_FILE)
    return [u for u in users.values() if u.get("verified") is True]


@router.get("/")
def home_signup():
    """
    API welcome message for the signup module.

    Returns:
        dict: Welcome message for the Flower Shop Signup API.
    """
    return {"message": "🌼 Welcome to Flower Shop Signup API 🌼"}


from fastapi import Path

@router.delete("/delete-user/{email}")
def delete_user(email: str = Path(..., description="Email of the user to delete")):
    """
    Delete a user account by email address.

    Permanently removes a user from the system based on their email.

    Args:
        email (str): Email address of the user to delete.

    Returns:
        dict: Success message confirming user deletion.

    Raises:
        HTTPException: 404 if user with specified email is not found.
    """
    users = load_data(USERS_FILE)

    if email not in users:
        raise HTTPException(status_code=404, detail="User not found.")

    del users[email]
    save_data(USERS_FILE, users)

    return {"message": f"User with email {email} has been deleted."}


@router.put("/update-user/{email}")
def update_user(email: str, data: UserUpdate):
    """
    Update a user's name and password by email address.

    Allows modification of user's name and password for existing accounts.

    Args:
        email (str): Email address of the user to update.
        data (UserUpdate): New user data containing updated name and password.

    Returns:
        dict: Success message confirming user update.

    Raises:
        HTTPException: 404 if user with specified email is not found.
    """
    users = load_data(USERS_FILE)

    if email not in users:
        raise HTTPException(status_code=404, detail="User not found.")

    users[email]["name"] = data.name
    users[email]["password"] = data.password
    save_data(USERS_FILE, users)

    return {"message": f"User {email} updated successfully."}


