"""YouTubeメタデータ取得サービス"""
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


class YouTubeService:
    """YouTube動画からメタデータを取得するサービス"""

    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        """URLから動画IDを抽出"""
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
            r"^([a-zA-Z0-9_-]{11})$",  # IDのみの場合
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_metadata(self, video_id: str) -> dict:
        """
        YouTube Data APIで動画メタデータを取得

        Returns:
            {
                "title": str,
                "channel": str,
                "published": str (ISO 8601形式),
                "thumbnail": str (URL)
            }
        """
        if not self.api_key:
            # APIキーがない場合はoEmbedにフォールバック
            return self._get_metadata_oembed(video_id)

        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet",
                "id": video_id,
                "key": self.api_key,
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("items"):
                raise ValueError("動画が見つかりません")

            snippet = data["items"][0]["snippet"]
            return {
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published": snippet.get("publishedAt", "")[:10],  # YYYY-MM-DD
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            }
        except requests.RequestException:
            # APIエラー時はoEmbedにフォールバック
            return self._get_metadata_oembed(video_id)

    def _get_metadata_oembed(self, video_id: str) -> dict:
        """oEmbed APIでメタデータを取得（フォールバック用）"""
        try:
            url = f"https://www.youtube.com/oembed?url=https://youtube.com/watch?v={video_id}&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "title": data.get("title", ""),
                "channel": data.get("author_name", ""),
                "published": "",  # oEmbedには日時情報なし
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            }
        except Exception:
            return {
                "title": "",
                "channel": "",
                "published": "",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            }
