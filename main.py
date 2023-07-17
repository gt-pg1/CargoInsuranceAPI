from fastapi import FastAPI

from tortoise.contrib.fastapi import register_tortoise

from app.routes import router as api_router

app = FastAPI()

app.include_router(api_router)

register_tortoise(
    app,
    db_url='postgres://admin:admin@db:5432/CargoInsurance',
    modules={'models': ['app.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

