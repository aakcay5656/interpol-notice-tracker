from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import threading
import logging
from database import Database
from models import InterpolNotice
from rabbitmq_client import RabbitMQConsumer
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

db = Database()
latest_notices = []


def process_notice(message):
    global latest_notices

    session = db.get_session()
    try:
        entity_id = message.get('entity_id')
        existing_notice = session.query(InterpolNotice).filter(
            InterpolNotice.entity_id == entity_id
        ).first()

        if existing_notice:
            existing_notice.forename = message.get('forename')
            existing_notice.name = message.get('name')
            existing_notice.date_of_birth = message.get('date_of_birth')
            existing_notice.nationalities = message.get('nationalities')
            existing_notice.arrest_warrants = message.get('arrest_warrants')
            existing_notice.fetch_timestamp = datetime.fromisoformat(
                message.get('fetch_timestamp')
            )
            existing_notice.updated_at = datetime.utcnow()
            existing_notice.is_updated = True
            logger.info(f"Updated existing notice: {entity_id}")
        else:
            new_notice = InterpolNotice(
                entity_id=entity_id,
                forename=message.get('forename'),
                name=message.get('name'),
                date_of_birth=message.get('date_of_birth'),
                nationalities=message.get('nationalities'),
                arrest_warrants=message.get('arrest_warrants'),
                fetch_timestamp=datetime.fromisoformat(
                    message.get('fetch_timestamp')
                )
            )
            session.add(new_notice)
            logger.info(f"Created new notice: {entity_id}")

        session.commit()

        all_notices = session.query(InterpolNotice).order_by(
            InterpolNotice.updated_at.desc()
        ).limit(50).all()
        latest_notices = [notice.to_dict() for notice in all_notices]

    except Exception as e:
        logger.error(f"Database error: {e}")
        session.rollback()
    finally:
        session.close()


def start_consumer():
    consumer = RabbitMQConsumer(callback=process_notice)
    consumer.connect()
    consumer.consume()


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logger.info("Application started")
    yield
    logger.info("Application shutting down")


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session = db.get_session()
    try:
        notices = session.query(InterpolNotice).order_by(
            InterpolNotice.updated_at.desc()
        ).limit(50).all()
        notices_data = [notice.to_dict() for notice in notices]
    finally:
        session.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "notices": notices_data,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}
