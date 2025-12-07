"""yt-digest バックエンドAPI"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import digest

app = FastAPI(
    title="yt-digest API",
    description="YouTube動画の字幕を取得し、Gemini APIで詳細な解説を生成するAPI",
    version="0.1.0",
)

# CORS設定（開発時は全許可、本番では適切に制限）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番ではフロントエンドのURLに制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(digest.router, prefix="/api", tags=["digest"])


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}
