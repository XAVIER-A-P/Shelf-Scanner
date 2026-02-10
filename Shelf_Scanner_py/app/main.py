from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, Response
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from sqlmodel import Session, create_engine, select
import uuid

from app.config import settings
from app.models import SQLModel, ScanHistory, Session as UserSession
from app.services.storage import upload_image_to_s3
from app.services.vision import identify_books

# Database Setup
engine = create_engine(settings.DATABASE_URL)

# Lifecycle: Connect to Redis on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine) # Create table
    redis_connection = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    yield
    await redis_connection.close()

app = FastAPI(lifespan=lifespan)

# Dependency: Get DB Session
def get_session():
    with Session(engine) as session:
        yield session

# Dependency: Manager User Session (Device Cookie)
def get_user_id(request: Request, response: Response, db: Session = Depends(get_session)):
    session_id = request.cookies.get("device_session_id")
    if not session_id:
        # Create new session
        new_sess = UserSession()
        db.add(new_sess)
        db.commit()
        db.refresh(new_sess)
        session_id = str(new_sess.session_id)
        # Set cookie for 1 year
        response.set_cookie(key="device_session_id", value=session_id, max_age=31536000)
    return session_id

# --- ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "shelf-scanner-active"}

@app.post("/scan", dependencies=[Depends(RateLimiter(times=5, seconds=3600))])
async def scan_bookshelf(
    response: Response,
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_session)
):
    """
    1. Rate Limit: 5 scan/hour
    2. Upload to S3
    3. Process with AI
    4. Save to DB
    """
    # 1. Validation
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # 2. Upload
    unique_filename = f"{user_id}/{uuid.uuid4()}.jpg"
    image_url = await upload_image_to_s3(file, unique_filename)

    # 3. AI Processing
    book = await identify_books(image_url)

    # 4. Save History
    history = ScanHistory(
        session_id=uuid.UUID(user_id),
        image_url=image_url,
        detected_book=book
    ) 
    db.add(history)
    db.commit()

    return {"image_url": image_url, "book": book}