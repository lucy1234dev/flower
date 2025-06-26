from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from signup import router as signup_router
from product import router as product_router

app = FastAPI()

#  Allow both local and Netlify frontend during development & production
origins = [
    "https://ideal12.netlify.app",  # Netlify deployed frontend
    "http://127.0.0.1:5500",         # Local frontend dev server
    "http://localhost:5500",        # Sometimes used instead of 127.0.0.1
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root welcome route that supports GET and HEAD."""
    return {"message": "🌸 Welcome to the Flower Shop API!"}

app.include_router(signup_router)
app.include_router(product_router)


