"""Digest APIルーター"""
import os
import re
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional

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


class SaveRequest(BaseModel):
    video_id: str
    content: str
    output_path: str  # Windowsパス形式（C:\...）
    # メタデータ（フロントマター生成用）
    title: str = ""
    channel: str = ""
    published: str = ""
    url: str = ""
    thumbnail: str = ""
    tags: list[str] = []
    model: str = ""


class SaveResponse(BaseModel):
    success: bool
    filename: str
    path: str


class ErrorResponse(BaseModel):
    error: str
    message: str


def windows_to_wsl_path(windows_path: str) -> str:
    """Windowsパスを WSLパスに変換"""
    # C:\Users\... → /mnt/c/Users/...
    if re.match(r'^[A-Za-z]:\\', windows_path):
        drive = windows_path[0].lower()
        rest = windows_path[3:].replace('\\', '/')
        return f'/mnt/{drive}/{rest}'
    return windows_path


def sanitize_filename(text: str) -> str:
    """ファイル名として安全な文字列に変換"""
    # 最初の見出し（# で始まる行）からタイトルを抽出
    lines = text.split('\n')
    title = None
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    if not title:
        title = "untitled"

    # ファイル名に使えない文字を除去
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title[:50]  # 長すぎる場合は切り詰め
    return title


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


def generate_frontmatter(request: SaveRequest) -> str:
    """Obsidian用YAMLフロントマターを生成"""
    created = datetime.now().strftime("%Y-%m-%d")

    # タグをYAML形式に
    tags_yaml = ""
    if request.tags:
        tags_list = "\n".join([f"  - {tag}" for tag in request.tags])
        tags_yaml = f"tags:\n{tags_list}"

    frontmatter = f"""---
title: "{request.title}"
channel: "{request.channel}"
published: {request.published or "unknown"}
url: {request.url}
thumbnail: {request.thumbnail}
model: {request.model}
created: {created}
{tags_yaml}
---

"""
    return frontmatter


@router.post("/save", response_model=SaveResponse)
async def save_to_file(request: SaveRequest):
    """
    解説をMarkdownファイルとして保存（Obsidianフロントマター付き）
    """
    try:
        # Windowsパス → WSLパスに変換
        wsl_path = windows_to_wsl_path(request.output_path)
        output_dir = Path(wsl_path)

        # ディレクトリがなければ作成
        output_dir.mkdir(parents=True, exist_ok=True)

        # ファイル名生成
        title = sanitize_filename(request.content)
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{title}_{date_str}.md"
        filepath = output_dir / filename

        # フロントマター生成
        frontmatter = generate_frontmatter(request)

        # コンテンツ結合して保存
        full_content = frontmatter + request.content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return SaveResponse(
            success=True,
            filename=filename,
            path=str(filepath),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "SAVE_FAILED", "message": f"保存に失敗しました: {str(e)}"},
        )
