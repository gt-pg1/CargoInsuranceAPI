import os
import logging
from dotenv import load_dotenv

from fastapi import FastAPI

from tortoise.contrib.fastapi import register_tortoise

from app.routes import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.include_router(api_router)

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')


register_tortoise(
    app,
    db_url=f"postgres://{user}:{password}@{host}:{port}/{db_name}",
    modules={'models': ['app.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)
