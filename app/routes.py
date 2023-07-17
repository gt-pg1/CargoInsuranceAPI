import os
import json
import logging
from datetime import datetime

from fastapi import HTTPException, Depends
from fastapi import APIRouter

from app.models import Tariff
from app.schemas import InsuranceInput

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/loaddata")
async def load_data(json_file: str = os.getenv('RATES_FILE')):
    """
    Load the data from the provided json file into the database.

    :param json_file: The file to load the data from.
    :return: A dict containing the status of the operation.
    """

    try:
        with open(json_file) as f:
            data = json.load(f)

        rows = 0
        updated = 0
        for date, tariffs in data.items():
            for tariff in tariffs:
                existing_tariff = await Tariff.get_or_none(
                    date=date,
                    cargo_type=tariff['cargo_type']
                )
                if existing_tariff:
                    existing_tariff.rate = float(tariff['rate'])
                    await existing_tariff.save()
                    updated += 1
                else:
                    await Tariff.create(
                        date=date,
                        cargo_type=tariff['cargo_type'],
                        rate=float(tariff['rate'])
                    )
                    rows += 1

        text = f"Data loaded successfully. Written {rows} new records, {updated} records updated."
        return {"status": text}

    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise


@router.get("/calculate_insurance")
async def calculate_insurance(insurance_input: InsuranceInput = Depends()):
    """
    Calculate the insurance based on the input parameters.

    :param insurance_input: The input parameters.
    :return: A dict containing the calculated insurance cost.
    """
    try:
        date_object = datetime.strptime(insurance_input.date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Incorrect date format. Expected format: YYYY-MM-DD"
        )

    tariff = await Tariff.get_or_none(
        date=date_object,
        cargo_type=insurance_input.cargo_type
    )
    if tariff is None:
        raise HTTPException(
            status_code=404,
            detail="Tariff not found"
        )

    return {"insurance_cost": insurance_input.declared_value * tariff.rate}
