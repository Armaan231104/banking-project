from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, require_admin
from app.schemas.user import UserOut
from app.db.models.user import User

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, role=user.role.value)


@router.get('/admin-check')
def admin_check(user: User = Depends(require_admin)):
    return {'status': 'admin-ok', 'user_id': user.id}
