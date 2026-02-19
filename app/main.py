from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from sqlmodel import Session, create_engine, select
import uuid

# Import your modules
from app.config import settings
from app.models import SQLModel, ScanHistory, Session as UserSession
from app.services.storage import upload_image_to_s3
from app.services.vision import identify_books
from app.services.recommendations import generate_recommendations

# --- DATABASE SETUP ---
engine = create_engine(settings.DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create Tables
    SQLModel.metadata.create_all(engine)
    # 2. Connect Redis for Rate Limiting
    redis_connection = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    yield
    # 3. Cleanup
    await redis_connection.close()

app = FastAPI(lifespan=lifespan)

# --- MOUNT STATIC FILES & TEMPLATES ---
# CRITICAL FIX: These must be initialized BEFORE your routes use them!
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- DEPENDENCIES ---
def get_session():
    with Session(engine) as session:
        yield session

def get_user_id(request: Request, response: Response, db: Session = Depends(get_session)):
    """
    Retrieves or Creates a persistent Device ID (User ID).
    Stored in a secure, long-lived HTTP cookie.
    """
    session_id = request.cookies.get("device_session_id")
    
    if not session_id:
        new_sess = UserSession()
        db.add(new_sess)
        db.commit()
        db.refresh(new_sess)
        session_id = str(new_sess.session_id)
        # Set cookie for 1 year
        response.set_cookie(key="device_session_id", value=session_id, max_age=31536000, httponly=True)
    
    return session_id

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, response: Response, user_id: str = Depends(get_user_id)):
    """Serve the Camera UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan-ui", response_class=HTMLResponse, dependencies=[Depends(RateLimiter(times=5, seconds=3600))])
async def scan_ui_handler(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_session)
):
    """
    Handles HTMX form submission.
    1. Uploads Image
    2. Runs AI Vision
    3. Generates Recommendations
    4. Saves History
    5. Returns HTML Partial
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # 1. Upload to S3
    unique_filename = f"{user_id}/{uuid.uuid4()}.jpg"
    image_url = await upload_image_to_s3(file, unique_filename)

    # 2. Vision Pipeline: Identify Books
    books_found = await identify_books(image_url)

    # 3. Handle Empty Scans
    if not books_found or len(books_found) == 0:
        return templates.TemplateResponse(
            "components/empty_state.html",
            {"request": request}
        )

    # 4. Generate Recommendations
    recommended_books = await generate_recommendations(books_found)

    # 5. Save History
    try:
        history = ScanHistory(
            session_id=uuid.UUID(user_id),
            image_url=image_url,
            detected_books=recommended_books 
        ) 
        db.add(history)
        db.commit()
    except Exception as e:
        print(f"Failed to save history: {e}") 

    # 6. Return HTML Fragment
    return templates.TemplateResponse(
        "components/book_list.html", 
        {
            "request": request, 
            "books": recommended_books 
        }
    )