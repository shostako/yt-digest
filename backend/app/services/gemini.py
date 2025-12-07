"""Gemini API連携サービス（YouTube URL直接処理）"""
import os
import re
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Gemini APIでYouTube動画の解説を生成するサービス"""

    # モデル優先順位（Pro → Flash）
    MODELS = ["gemini-2.5-pro", "gemini-2.5-flash"]

    # 詳細度別プロンプト（YouTube URL直接処理用）
    PROMPTS = {
        "brief": """このYouTube動画の内容を簡潔に要約してください。

【出力形式】
1. 最初に動画タイトルを # 見出しで記載（「YouTube動画」等の接頭辞は不要）
2. 3〜5個の箇条書きで要点をまとめる
3. 全体で300文字程度
4. 最後に「---」の後、この動画を表すキーワードタグを5〜8個、カンマ区切りで出力
   例: タグ: AI, 機械学習, プログラミング, Python
""",
        "standard": """このYouTube動画の内容を要約してください。

【出力形式】
1. 最初に動画タイトルを # 見出しで記載（「YouTube動画」等の接頭辞は不要）
2. 主要なポイントを箇条書き
3. 重要な点を簡潔に説明
4. 全体で500〜800文字程度
5. 最後に「---」の後、この動画を表すキーワードタグを5〜8個、カンマ区切りで出力
   例: タグ: AI, 機械学習, プログラミング, Python
""",
        "detailed": """このYouTube動画の内容について詳細に解説してください。

【出力形式】
- 最初に動画タイトルを # 見出しで記載（「YouTube動画」等の接頭辞は不要）
- 続いて ## 動画の主題と目的
- ## 主要なポイント（箇条書き）
- ## 重要な概念の詳細な説明
- ## 結論・まとめ
- Markdown形式で見出しや箇条書きを適切に使用
- 最後に「---」の後、この動画を表すキーワードタグを5〜10個、カンマ区切りで出力
  例: タグ: AI, 機械学習, プログラミング, Python, Claude
""",
    }

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")
        genai.configure(api_key=api_key)

    def generate_digest(self, youtube_url: str, detail_level: str = "detailed") -> dict:
        """
        YouTube動画から解説を生成（URLを直接Geminiに渡す）

        Args:
            youtube_url: YouTube動画のURL
            detail_level: 詳細度（brief / standard / detailed）

        Returns:
            {
                "text": str,  # 解説テキスト
                "tags": list[str],  # タグリスト
                "model": str  # 使用したモデル名
            }
        """
        # 詳細度に応じたプロンプトを選択
        prompt = self.PROMPTS.get(detail_level, self.PROMPTS["detailed"])
        last_error = None

        for model_name in self.MODELS:
            try:
                model = genai.GenerativeModel(model_name)

                # YouTube URLを直接Geminiに渡す
                response = model.generate_content(
                    [
                        prompt,
                        {"file_data": {"file_uri": youtube_url}}
                    ],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4096,
                    ),
                )
                text = response.text
                tags = self._extract_tags(text)
                # タグ部分を本文から除去
                text = self._remove_tags_section(text)

                return {
                    "text": text,
                    "tags": tags,
                    "model": model_name,
                }
            except ResourceExhausted as e:
                # Quota超過 → 次のモデルを試す
                last_error = e
                continue
            except Exception as e:
                # 429エラーの文字列チェック（ResourceExhaustedでキャッチできない場合）
                if "429" in str(e) or "quota" in str(e).lower():
                    last_error = e
                    continue
                raise ValueError(f"解説の生成に失敗しました: {str(e)}")

        # 全モデルでQuota超過
        raise ValueError(f"全モデルのQuotaを超過しました。しばらく待ってから再試行してください: {str(last_error)}")

    def _extract_tags(self, text: str) -> list[str]:
        """テキストからタグを抽出"""
        # 末尾300文字のみを対象（本文を巻き込まない）
        tail = text[-300:] if len(text) > 300 else text

        # 様々な形式に対応: 「タグ:」「**タグ**:」「Tags:」など
        patterns = [
            r'\*{0,2}タグ\*{0,2}[:：]\s*(.+?)(?:\n|$)',
            r'\*{0,2}Tags?\*{0,2}[:：]\s*(.+?)(?:\n|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, tail, re.IGNORECASE)
            if match:
                tags_str = match.group(1)
                # カンマまたは、で分割
                tags = re.split(r'[,、]', tags_str)
                # スペース除去してObsidian互換に（Claude Code → ClaudeCode）
                cleaned = []
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        # スペースを除去
                        tag = tag.replace(' ', '')
                        cleaned.append(tag)
                return cleaned
        return []

    def _remove_tags_section(self, text: str) -> str:
        """タグセクションを本文から除去（末尾から行単位で処理）"""
        lines = text.rstrip().split('\n')

        # 末尾から見ていって、タグ行と---と空行を削除
        while lines:
            last_line = lines[-1].strip()
            # タグ行
            if re.match(r'\*{0,2}(タグ|Tags?)\*{0,2}[:：]', last_line, re.IGNORECASE):
                lines.pop()
                continue
            # ---行
            if last_line == '---':
                lines.pop()
                continue
            # 空行
            if last_line == '':
                lines.pop()
                continue
            break

        return '\n'.join(lines)
