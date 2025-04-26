# app/schemas/user_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., description="登录用户名")
    password: str = Field(..., description="登录密码")
    admin_key: Optional[str] = Field(
        None,
        description="管理员注册密钥（填写正确可注册为 admin）"
    )

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class UpdateUserIdRequest(BaseModel):
    new_user_id: str

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    
    class Config:
        from_attributes = True