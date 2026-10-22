# yt-digest

YouTube の動画の URL を入れると、Gemini が動画を見て解説を書く Web アプリ。解説は Markdown で表示し、タグを付けて Obsidian に保存できる。

## 構成

| 部分 | 中身 | 置き場所（Render） |
|---|---|---|
| `frontend/` | Next.js 15（App Router）、React 19 | yt-digest-web |
| `backend/` | FastAPI、Gemini（`gemini-3.8-flash`、SDK は `google-genai`） | yt-digest-api |

配信の設定は `render.yaml` にある。

## 環境変数

- バックエンド
  - `GEMINI_API_KEY`（必須）
  - `YOUTUBE_API_KEY`（任意。無いときはタイトルなどを oEmbed で取る）
  - `FRONTEND_URL`（CORS 用）
- 画面: `NEXT_PUBLIC_API_URL`（バックエンドの URL）

## 手元で動かす

```bash
# バックエンド
cd backend && pip install -r requirements.txt && uvicorn app.main:app --port 8000
# 画面（別の端末）
cd frontend && npm install && npm run dev
```

## 変更履歴

[CHANGELOG.md](CHANGELOG.md) を見る。
