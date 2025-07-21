from pydantic import BaseModel
from typing import List, Optional

class SubService(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None

class Service(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    subServices: Optional[List[SubService]] = []

class ServiceResponse(BaseModel):
    message: str
    statusCode: int
    data: List[Service]
    isSuccess: bool
    ex: Optional[str] = None

class PostcodeValidationResponse(BaseModel):
    message: str
    statusCode: int
    data: Optional[dict] = None
    isSuccess: bool
    ex: Optional[str] = None