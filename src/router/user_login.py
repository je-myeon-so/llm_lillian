from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.backend.database_config import get_db
from src.backend.model import User

# API 라우터 초기화
router = APIRouter()

# 로그인 및 회원가입 요청 데이터 모델
class UserLoginRegister(BaseModel):
    username: str  # 사용자 이름
    password: str  # 사용자 비밀번호

# 로그인 및 회원가입 응답 데이터 모델
class LoginResponse(BaseModel):
    username: str  # 사용자 아이디
    success: bool  # 성공 여부
    message: str  # 응답 메시지
    is_new_user: bool  # 신규 사용자 여부 (회원가입인지 로그인인지)

# 통합 로그인/회원가입
@router.post("/auth", response_model=LoginResponse)
def login_or_register(user_data: UserLoginRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.name == user_data.username).first()

    # 사용자가 이미 존재하는 경우 로그인 처리
    if db_user:
        # 비밀번호 검증
        if db_user.password == user_data.password:
            # 비밀번호 일치 - 로그인 성공
            return LoginResponse(
                username=db_user.name,
                success=True,
                message="로그인 성공",
                is_new_user=False
            )
        else:
            # 비밀번호 불일치 - 로그인 실패
            return LoginResponse(
                username=user_data.username,
                success=False,
                message="비밀번호가 일치하지 않습니다",
                is_new_user=False
            )

    # 3. 사용자가 존재하지 않는 경우 - 새 계정 자동 생성
    try:
        # 새 사용자 객체 생성 및 저장
        new_user = User(name=user_data.username, password=user_data.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 회원가입 및 로그인 성공 응답
        return LoginResponse(
            username=new_user.name,
            success=True,
            message="회원가입 및 로그인 성공",
            is_new_user=True
        )
    except Exception as e:
        # 오류 발생 시 트랜잭션 롤백 및 예외 발생
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"계정 생성 중 오류 발생: {str(e)}"
        )