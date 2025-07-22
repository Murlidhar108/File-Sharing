from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.utils.token_service import create_verification_token
from app.utils.email_service import send_verification_email
from passlib.context import CryptContext

router = APIRouter(prefix="/client", tags=["Client Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print("👉 Received signup request")

    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    print("✅ Email is new, creating user...")

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Create new user
    new_user = models.User(
        email=user.email,
        password=hashed_password,
        is_verified=False,
        user_type=user.user_type,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"✅ User created with ID {new_user.id}")

    # Create verification token
    token = create_verification_token(data={"user_id": new_user.id})
    print("🔐 Verification token generated")

    # Prepare verification email
    verification_link = f"http://localhost:8000/client/verify?token={token}"
    body = f"Click the following link to verify your email:\n\n{verification_link}"

    try:
        await send_verification_email(email_to=new_user.email, body=body)
        print(f"📨 Verification email sent to {new_user.email}")
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail="User created, but failed to send verification email.")

    return new_user


from app.utils.token_service import verify_verification_token

@router.get("/client/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        print("👉 Received token for verification:", token)
        payload = verify_verification_token(token)
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "Email already verified ✅"}

        user.is_verified = True
        db.commit()
        print(f"✅ User ID {user_id} verified successfully")
        return {"message": "Email verified successfully ✅"}

    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid or expired token")
