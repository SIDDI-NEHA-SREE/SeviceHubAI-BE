from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import models, schemas, auth, database
from ..auth import get_password_hash, verify_password, create_access_token, create_refresh_token
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=schemas.UserRead)
async def register_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    # Check if email already exists
    result = await db.execute(select(models.User).where(models.User.email == user_in.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
        department=user_in.department,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
async def login(email: str, password: str, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token({"sub": str(user.user_id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.user_id), "role": user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserRead)
async def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# Password reset flow (request OTP)
@router.post("/password-reset/request")
async def password_reset_request(req: schemas.PasswordResetRequest, db: AsyncSession = Depends(database.get_db)):
    # Find user
    result = await db.execute(select(models.User).where(models.User.email == req.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Generate OTP (6‑digit)
    import random, string
    otp = "".join(random.choices(string.digits, k=6))
    # Store token
    token = models.PasswordResetToken(user_id=user.user_id, otp=otp, expires_at=datetime.utcnow() + timedelta(minutes=10))
    db.add(token)
    await db.commit()
    # Send email (placeholder using SendGrid env var)
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    if sendgrid_key:
        import httpx
        await httpx.AsyncClient().post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {sendgrid_key}", "Content-Type": "application/json"},
            json={
                "personalizations": [{"to": [{"email": req.email}]}],
                "from": {"email": "no-reply@servicedeskai.com"},
                "subject": "Your password reset OTP",
                "content": [{"type": "text/plain", "value": f"Your OTP is {otp}. It expires in 10 minutes."}],
            },
        )
    return {"msg": "OTP sent if email exists"}

@router.post("/password-reset/verify")
async def password_reset_verify(data: schemas.PasswordResetVerify, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(
        select(models.PasswordResetToken).where(
            models.PasswordResetToken.user_id == (await db.execute(select(models.User.user_id).where(models.User.email == data.email))).scalar_one_or_none(),
            models.PasswordResetToken.otp == data.otp,
            models.PasswordResetToken.used == False,
            models.PasswordResetToken.expires_at > datetime.utcnow()
        )
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    # Update password
    result = await db.execute(select(models.User).where(models.User.email == data.email))
    user = result.scalar_one()
    user.password_hash = get_password_hash(data.new_password)
    token.used = True
    await db.commit()
    return {"msg": "Password updated"}
