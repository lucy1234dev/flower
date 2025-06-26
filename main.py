from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Add this

from signup import router as signup_router
from product import router as product_router

app = FastAPI()

#  Enable CORS to allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ideal12.nettlify.app"],  #  Replace "*" with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route to avoid "Not Found" on home
@app.get("/")
def read_root():
    """read root of the application"""
    return {"message": "🌸 Welcome to the Flower Shop API!"}

# Include feature-specific routers
app.include_router(signup_router)
app.include_router(product_router)

