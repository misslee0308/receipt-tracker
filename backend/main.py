from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import upload, expenses, summary

app = FastAPI(title="Receipt Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(summary.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "message": "Receipt Tracker API"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Receipt Tracker API is running"}
