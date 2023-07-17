import json

from fastapi import APIRouter

from tortoise.exceptions import IntegrityError

from app.models import Tariff

router = APIRouter()


@router.post("/loaddata")
async def load_data():
    try:
        with open('rates.json') as f:
            data = json.load(f)

        for date, tariffs in data.items():
            for tariff in tariffs:
                try:
                    await Tariff.create(
                        date=date,
                        cargo_type=tariff['cargo_type'],
                        rate=float(tariff['rate'])
                    )
                except IntegrityError:
                    pass

        return {"status": "data loaded successfully"}
    except Exception as e:
        print(f"Failed to load data: {e}")
