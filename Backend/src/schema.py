from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Dict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr

    class Config:
        model_config = ConfigDict(from_attributes=True)

class InferenceInput(BaseModel):
    image_path: str

class InferenceOutput(BaseModel):
    disease: str
    solution: Optional[Dict[str, str]] = None
    confidence: float

class InferenceResponse(BaseModel):
    error: Optional[str] = None
    result: Optional[InferenceOutput] = None

class ErrorResponse(BaseModel):
    error: str
