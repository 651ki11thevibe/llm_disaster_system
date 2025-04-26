# app/api/user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UpdateUserIdRequest, ChangePasswordRequest, UserOut
from app.api.deps import require_active_user  
from app.db.session import get_db
from app.core.security import verify_password, get_password_hash

router = APIRouter()

@router.post("/update_user_id")
def update_user_id(
    data: UpdateUserIdRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.username = data.new_user_id
    db.commit()
    db.refresh(user)
    return {"message": "用户ID更新成功"}

@router.post("/change_password", dependencies=[Depends(require_active_user)])
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_active_user)
):
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="旧密码不正确")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"msg": "密码更新成功"}

@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(require_active_user)):
    return current_user 
