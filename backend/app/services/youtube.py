"""YouTube字幕・メタデータ取得サービス"""
import os
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from dotenv import load_dotenv

load_dotenv()


class YouTubeService:
    """YouTube動画から字幕とメタデータを取得するサービス"""

    # 字幕言語の優先順位
    LANGUAGE_PRIORITY = ["ja", "en"]

    def __init__(self):
        self.api = YouTubeTranscriptApi()
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
        except requests.RequestException as e:
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

    def get_transcript(self, video_id: str) -> dict:
        """
        動画の字幕を取得

        Returns:
            {
                "text": str,  # 結合された字幕テキスト
                "language": str,  # 取得した言語コード
                "is_generated": bool  # 自動生成かどうか
            }

        Raises:
            ValueError: 字幕が取得できない場合
        """
        try:
            # 優先言語順で字幕を取得
            transcript = self.api.fetch(video_id, languages=self.LANGUAGE_PRIORITY)
            text = " ".join([entry.text for entry in transcript])

            # 言語情報を取得するためにlistも呼ぶ
            transcript_list = self.api.list(video_id)
            found_transcript = transcript_list.find_transcript(self.LANGUAGE_PRIORITY)

            return {
                "text": text,
                "language": found_transcript.language_code,
                "is_generated": found_transcript.is_generated,
            }
        except TranscriptsDisabled:
            raise ValueError("この動画では字幕が無効になっています")
        except VideoUnavailable:
            raise ValueError("動画が見つかりません")
        except NoTranscriptFound:
            # 優先言語がない場合、利用可能な字幕を使用
            try:
                transcript_list = self.api.list(video_id)
                available = list(transcript_list)
                if available:
                    first = available[0]
                    fetched = first.fetch()
                    text = " ".join([entry.text for entry in fetched])
                    return {
                        "text": text,
                        "language": first.language_code,
                        "is_generated": first.is_generated,
                    }
            except Exception:
                pass
            raise ValueError("利用可能な字幕がありません")
        except Exception as e:
            raise ValueError(f"字幕の取得に失敗しました: {str(e)}")
