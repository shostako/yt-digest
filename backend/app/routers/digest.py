"""Digest APIルーター"""
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from app.services.youtube import YouTubeService
from app.services.gemini import GeminiService

router = APIRouter()


class DigestRequest(BaseModel):
    url: str
    detail_level: Literal["brief", "standard", "detailed"] = "detailed"


class DigestResponse(BaseModel):
    video_id: str
    digest: str
    model: str
    # メタデータ
    title: str
    channel: str
    published: str
    thumbnail: str
    url: str
    tags: list[str]


class ErrorResponse(BaseModel):
    error: str
    message: str


@router.post("/digest", response_model=DigestResponse)
async def create_digest(request: DigestRequest):
    """
    YouTube動画の解説を生成

    - URLから動画IDを抽出
    - メタデータを取得
    - Gemini APIに直接YouTube URLを渡して解説を生成
    """
    # 動画ID抽出
    video_id = YouTubeService.extract_video_id(request.url)
    if not video_id:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_URL", "message": "有効なYouTube URLではありません"},
        )

    youtube = YouTubeService()

    # メタデータ取得
    metadata = youtube.get_video_metadata(video_id)
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # 解説生成（Gemini APIに直接YouTube URLを渡す）
    try:
        gemini = GeminiService()
        result = gemini.generate_digest(video_url, request.detail_level)
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "GENERATION_FAILED", "message": str(e)},
        )

    return DigestResponse(
        video_id=video_id,
        digest=result["text"],
        model=result["model"],
        # メタデータ
        title=metadata["title"],
        channel=metadata["channel"],
        published=metadata["published"],
        thumbnail=metadata["thumbnail"],
        url=video_url,
        tags=result["tags"],
    )
