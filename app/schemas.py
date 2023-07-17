from pydantic import BaseModel


class InsuranceInput(BaseModel):
    date: str
    cargo_type: str
    declared_value: float
