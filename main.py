"""
FastAPI application for Flower Shop API with CORS configuration.

This module sets up the main FastAPI application with proper CORS middleware
to handle cross-origin requests from the frontend deployed on Netlify.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from signup import router as signup_router
from product import router as product_router

# Initialize FastAPI application
app = FastAPI(
    title="Flower Shop API",
    description="A REST API for flower shop operations including user signup and product management",
    version="1.0.0"
)

# CORS Configuration - Production Ready
origins = [
    "https://ideal12.netlify.app",  # Your deployed frontend
    "http://127.0.0.1:5500",        # Local development
    "http://localhost:5500",
    "http://localhost:3000",        # Common React dev server
    "http://localhost:8000",        # Common Vue/other dev servers
]

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Use specific origins for security
    allow_credentials=True,         # Allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# For debugging only - you can temporarily use this instead:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,  # Must be False with "*"
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )


@app.get("/")
async def read_root():
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        dict: A welcome message for the Flower Shop API
    """
    return {"message": "🌸 Welcome to the Flower Shop API!"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring API status.
    
    Returns:
        dict: Status information indicating if the API is running
    """
    return {"status": "healthy", "message": "API is running"}


# Include routers for different functionalities
app.include_router(signup_router)
app.include_router(product_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)




