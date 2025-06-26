from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from signup import router as signup_router
from product import router as product_router

app = FastAPI()

# ✅ This list must contain your frontend domain
origins = [
    "https://ideal12.netlify.app",  # Your frontend (Netlify)
    "http://127.0.0.1:5500",        # Local testing (optional)
    "http://localhost:5500"
]

#  This is what actually allows the browser to talk to your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Only allow these origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET","HEAD"])
def read_root():
    return {"message": "🌸 Welcome to the Flower Shop API!"}

# Include routers
app.include_router(signup_router)
app.include_router(product_router)



