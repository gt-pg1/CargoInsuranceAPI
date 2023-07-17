import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class InsuranceInput(BaseModel):
    date: str
    cargo_type: str
    declared_value: float
