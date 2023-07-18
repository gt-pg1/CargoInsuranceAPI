import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import HTTPException

from app.models import Tariff

import json

logger = logging.getLogger(__name__)


def validate_json(data: Dict[str, Any]) -> None:
    """
    Validate the structure of JSON data.

    :param data: JSON data to validate
    :raises ValueError: If the JSON structure is invalid
    """
    if not isinstance(data, dict):
        raise ValueError("Invalid JSON structure: Root should be a dictionary")

    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError("Invalid JSON structure: Date should be a string")
        if not isinstance(value, list):
            raise ValueError("Invalid JSON structure: Tariffs should be a list")
        for tariff in value:
            if not isinstance(tariff, dict) or not all(k in tariff for k in ['cargo_type', 'rate']):
                raise ValueError("Invalid JSON structure: Tariff should be a dictionary with 'cargo_type' and 'rate'")


def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read JSON file

    :param file_path: File path
    :return: Dictionary with data from the file
    :raises: Error when reading the file
    """
    try:
        with open(file_path, 'r') as file:
            data: Dict[str, Any] = json.load(file)
            validate_json(data)
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Could not parse the JSON file: {file_path}, error: {str(e)}")
        raise ValueError(f"Invalid JSON format in the file: {file_path}")


async def process_tariff(tariff: Dict[str, Any], date: str) -> Dict[str, int]:
    """
    Process each tariff. Create new records or update existing ones.

    :param tariff: Dictionary with tariff information
    :param date: Tariff date
    :return: Dictionary with the number of new and updated records
    """
    rows, updated = 0, 0
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


async def save_to_db(data: Dict[str, Any]) -> Dict[str, int]:
    """
    Save data to the database.

    :param data: Dictionary with data to be saved
    :return: Dictionary with the total number of new and updated records
    """
    rows, updated = 0, 0
    for date, tariffs in data.items():
        for tariff in tariffs:
            result = await process_tariff(tariff, date)
            rows += result["rows"]
            updated += result["updated"]
    return {"rows": rows, "updated": updated}


async def str_to_date(date_str: str) -> datetime.date:
    """
    Convert a date string to a datetime.date object

    :param date_str: Date string in the format YYYY-MM-DD
    :return: datetime.date object
    :raises: Error when the date format is incorrect
    """
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
