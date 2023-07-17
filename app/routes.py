import os
import logging
from typing import Dict, Optional

from fastapi import HTTPException, Depends
from fastapi import APIRouter

from app.models import Tariff
from app.schemas import InsuranceInput
from app import operations

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/loaddata")
async def load_data(json_file: str = os.getenv('RATES_FILE')) -> Dict[str, str]:
    data = await operations.read_file(json_file)
    results = await operations.save_to_db(data)
    text = f"Data loaded successfully. Written {results['rows']} new records, {results['updated']} records updated."
    return {"status": text}


@router.get("/calculate_insurance")
async def calculate_insurance(insurance_input: InsuranceInput = Depends()) -> Dict[str, float]:
    date_object = await operations.str_to_date(insurance_input.date)
    tariff: Optional[Tariff] = await Tariff.get_or_none(
        date=date_object,
        cargo_type=insurance_input.cargo_type
    )
    if tariff is None:
        raise HTTPException(
            status_code=404,
            detail="Tariff not found"
        )
    return {"insurance_cost": insurance_input.declared_value * tariff.rate}
