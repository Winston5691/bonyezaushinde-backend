from pydantic import BaseModel

class CustomerBase(BaseModel):
    name: str
    phone_number: str
    location: str = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int

    class Config:
        orm_mode = True
