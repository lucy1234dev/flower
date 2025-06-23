from fastapi import FastAPI
from signup import router as signup_router
from product import router as product_router

app = FastAPI()

# Register routers
app.include_router(signup_router)
app.include_router(product_router)

@app.get("/")
def home():
    return {"message": "🌼 Welcome to Flower Shop Signup API 🌼"}
