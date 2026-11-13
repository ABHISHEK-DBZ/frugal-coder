from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.entities import User, Budget, UserRole
from app.schemas.api_models import UserRegister, UserLogin, UserOut, TokenOut

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenOut)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Registers a new developer user and assigns an independent budget."""
    existing_user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    pw_hash, salt = hash_password(user_in.password)
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=pw_hash,
        password_salt=salt,
        role=UserRole.DEVELOPER
    )
    db.add(new_user)
    db.flush()

    # Create user budget
    user_budget = Budget(
        user_id=new_user.id,
        limit_usd=10.00,
        spent_usd=0.00,
        reserved_usd=0.00
    )
    db.add(user_budget)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(subject=new_user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=TokenOut)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user via username and PBKDF2 hash comparison."""
    user = db.query(User).filter(User.username == login_in.username).first()
    if not user or not verify_password(login_in.password, user.password_hash, user.password_salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user."""
    return current_user

