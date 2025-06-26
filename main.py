from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from signup import router as signup_router
from product import router as product_router

app = FastAPI()

#  Allow your frontend origins
origins = [
    "https://ideal12.netlify.app",  # Deployed frontend
    "http://127.0.0.1:5500",        # Local dev
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Support GET, POST, and OPTIONS for root
@app.api_route("/", methods=["GET", "POST", "OPTIONS"], include_in_schema=False)
async def read_root(request: Request):
    if request.method == "OPTIONS":
        return JSONResponse(content={"message": "Preflight OK"})
    elif request.method == "POST":
        return JSONResponse(content={"message": "POST not allowed on this route"})
    return {"message": "🌸 Welcome to the Flower Shop API!"}

# Include other route groups
app.include_router(signup_router)
app.include_router(product_router)




