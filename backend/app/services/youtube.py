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
                "thumbnail": self._best_thumbnail(video_id),
            }
        except requests.RequestException:
            # APIエラー時はoEmbedにフォールバック
            return self._get_metadata_oembed(video_id)

    @staticmethod
    def _best_thumbnail(video_id: str) -> str:
        """高画質のサムネイル（maxresdefault）があればそれを、無ければ hqdefault を返す。

        古い動画や低解像度の動画には maxresdefault が無く、YouTube は 404 と灰色の仮の絵を返す。
        hqdefault（480x360）はどの動画にもある。
        """
        maxres = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        try:
            if requests.head(maxres, timeout=5).status_code == 200:
                return maxres
        except requests.RequestException:
            pass
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

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
                "thumbnail": self._best_thumbnail(video_id),
            }
        except Exception:
            return {
                "title": "",
                "channel": "",
                "published": "",
                "thumbnail": self._best_thumbnail(video_id),
            }
