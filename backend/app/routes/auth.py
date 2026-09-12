from app.config import get_settings
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.security import create_access_token, get_current_user, hash_password, normalize_email, verify_password
from app.database.mongodb import get_database
from app.schemas.auth import LoginRequest, RegistrationResponse, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


def _user_response(user: dict) -> UserResponse:
    return UserResponse(id=str(user["_id"]), name=user["name"], email=user["email"], created_at=user["created_at"], role=user.get("role", "USER"))


def _ensure_user_index(collection) -> None:
    collection.create_index("email", unique=True)


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserCreate) -> RegistrationResponse:
    collection = get_database()["users"]
    _ensure_user_index(collection)
    now = datetime.now(timezone.utc)
    document = {"name": request.name, "email": normalize_email(str(request.email)), "password_hash": hash_password(request.password), "role": "USER", "is_active": True, "created_at": now, "updated_at": now}
    try:
        collection.insert_one(document)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.") from error
    except PyMongoError as error:
        raise HTTPException(status_code=500, detail="Account storage is temporarily unavailable.") from error
    return RegistrationResponse(message="Registration successful.")


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    user = get_database()["users"].find_one({"email": normalize_email(str(request.email))})
    if user is None or not verify_password(request.password, user.get("password_hash", "")) or not user.get("is_active", False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.", headers={"WWW-Authenticate": "Bearer"})
    now = datetime.now(timezone.utc)
    get_database()["users"].update_one({"_id": user["_id"]}, {"$set": {"last_login_at": now, "updated_at": now}})
    return TokenResponse(access_token=create_access_token(str(user["_id"])), user=_user_response(user))


@router.get("/me", response_model=UserResponse)
def current_user(user: dict = Depends(get_current_user)) -> UserResponse:
    return _user_response(user)


@router.post("/logout", response_model=RegistrationResponse)
def logout(_: dict = Depends(get_current_user)) -> RegistrationResponse:
    return RegistrationResponse(message="Logout acknowledged. Remove the bearer token from the client.")


@router.post("/admin-setup", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def admin_setup(request: UserCreate, setup_secret: str, current_user: dict | None = None) -> RegistrationResponse:
    settings = get_settings()
    if not settings.admin_setup_secret or setup_secret != settings.admin_setup_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin setup is not available.")
    collection = get_database()["users"]
    _ensure_user_index(collection)
    now = datetime.now(timezone.utc)
    try:
        collection.insert_one({"name": request.name, "email": normalize_email(str(request.email)), "password_hash": hash_password(request.password), "role": "ADMIN", "is_active": True, "created_at": now, "updated_at": now})
    except DuplicateKeyError as error:
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from error
    return RegistrationResponse(message="Administrator account created.")