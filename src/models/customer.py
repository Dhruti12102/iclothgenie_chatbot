from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginDetails(BaseModel):
    username: str
    password: str

class Customer(BaseModel):
    firstname: str
    lastname: str
    mobileNo: str
    email: EmailStr
    loginDetails: LoginDetails

class CustomerLoginRequest(BaseModel):
    username: str
    password: str

class CustomerData(BaseModel):
    id: int
    firstname: str
    lastname: str
    displayname: str
    email: str
    mobileNo: str
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postCode: Optional[str] = None
    plateform: Optional[str] = None
    url: str = ""
    notificationToken: Optional[str] = None
    isActive: bool = True
    isDelete: bool = False
    totalOrder: int = 0
    loginDetails: Optional[dict] = None
    providerName: Optional[str] = None
    providerId: Optional[str] = None
    accessToken: Optional[str] = None
    reimbursed: int = 0
    secondaryEmail: str
    otp: Optional[str] = None

class LoginResponse(BaseModel):
    message: str
    statusCode: int
    data1: str  # Token
    data2: CustomerData
    data3: str  # Additional token
    data4: Optional[str] = None
    data5: Optional[str] = None
    isSuccess: bool
    ex: Optional[str] = None