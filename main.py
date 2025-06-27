from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from signup import router as signup_router
from product import router as product_router

app = FastAPI()

# CORS Configuration - More permissive for debugging
origins = [
    "https://ideal12.netlify.app",  # Your deployed frontend
    "http://127.0.0.1:5500",        # Local dev
    "http://localhost:5500",
    "https://*.netlify.app",        # Allow all netlify subdomains
    "*"  # Temporarily allow all origins for debugging - remove in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins
    allow_credentials=False,  # Set to False when using "*" for origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Handle preflight requests globally
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse({"message": "OK"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    response = await call_next(request)
    return response

# Root endpoint with proper method handling
@app.get("/")
async def read_root():
    return {"message": "🌸 Welcome to the Flower Shop API!"}

@app.options("/")
async def root_options():
    return JSONResponse({"message": "Preflight OK"})

# Include routers
app.include_router(signup_router)
app.include_router(product_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)




