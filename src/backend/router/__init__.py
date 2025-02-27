from src.backend.router.db_question_routes import router as question_router
from src.backend.router.db_analysis_routes import router as analysis_router

# 필요할 경우 라우터를 한 번에 가져오기 위한 리스트
routers = [question_router, analysis_router]