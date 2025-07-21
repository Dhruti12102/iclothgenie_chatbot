from pydantic import BaseModel, EmailStr
from typing import Optional

class OrderAddress(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    contactNo: str
    postCode: str
    addressLine1: str
    addressLine2: str

class OrderRequest(BaseModel):
    customerId: int
    pickupDate: str
    pickupTime: str
    dropOffDate: str
    dropOffTime: str
    Services: str
    SubServices: str
    collectionOption: str
    deliveryOption: str
    orderAddress: OrderAddress
    offerCode: str = ""

class OrderUpdateRequest(BaseModel):
    id: int
    customerId: int
    pickupDate: str
    pickupTime: str
    collectionOption: str
    dropOffDate: str
    dropOffTime: str
    deliveryOption: str

class OrderDetail(BaseModel):
    id: int
    customerId: int
    pickupDate: str
    pickupTime: str
    dropOffDate: str
    dropOffTime: str
    collectionOption: str
    deliveryOption: str
    status: Optional[str] = None
    totalAmount: Optional[float] = None
    services: Optional[str] = None
    subServices: Optional[str] = None
    orderAddress: Optional[dict] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None