import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import HTTPException

from app.models import Tariff

import json

logger = logging.getLogger(__name__)


async def read_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r') as file:
            data: Dict[str, Any] = json.load(file)
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise


async def save_to_db(data: Dict[str, Any]) -> Dict[str, int]:
    rows, updated = 0, 0
    for date, tariffs in data.items():
        for tariff in tariffs:
            existing_tariff: Optional[Tariff] = await Tariff.get_or_none(
                date=date,
                cargo_type=tariff['cargo_type']
            )
            new_rate = float(tariff['rate'])
            if existing_tariff:
                if existing_tariff.rate != new_rate:
                    existing_tariff.rate = new_rate
                    await existing_tariff.save()
                    updated += 1
            else:
                await Tariff.create(
                    date=date,
                    cargo_type=tariff['cargo_type'],
                    rate=new_rate
                )
                rows += 1
    return {"rows": rows, "updated": updated}


async def str_to_date(date_str: str) -> datetime.date:
    try:
        date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
        return date_object
    except ValueError:
        error_text = "Incorrect date format. Expected format: YYYY-MM-DD"
        logger.error(error_text)
        raise HTTPException(
            status_code=400,
            detail=error_text
        )
