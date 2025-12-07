# プロジェクト進捗状況

## 現在の状態
- **最終更新**: 2025-12-07
- **ステータス**: ✅ 本番稼働中

## 完了済み
- [x] プロジェクト作成
- [x] 技術スタック決定（Next.js + FastAPI + Gemini）
- [x] 仕様書作成
- [x] バックエンド実装（FastAPI + Gemini）
- [x] フロントエンド実装（Next.js + ReactMarkdown）
- [x] ローカル動作確認
- [x] Renderデプロイ
- [x] youtube-transcript-api廃止 → Gemini直接URL処理に移行
- [x] Flashモデルのみに変更（Quota最適化）

## 本番環境
- **フロントエンド**: https://yt-digest-web.onrender.com
- **バックエンド**: https://yt-digest-api.onrender.com

## 技術的な決定事項

### YouTube動画処理方式
- **採用**: Gemini APIにYouTube URLを直接渡す方式
- **理由**: youtube-transcript-apiはクラウドIPがYouTubeにブロックされる
- **参考**: https://ai.google.dev/gemini-api/docs/video-understanding

### モデル選択
- **採用**: gemini-2.5-flash のみ
- **理由**: YouTube動画処理はトークン消費が大きい、Pro→Flashフォールバックだと2倍消費

## 制限事項
- Gemini無料プランの制限（1分あたり250,000トークン）
- YouTube動画処理は1日8時間分まで（Geminiプレビュー機能）

## 起動方法（ローカル開発）

### バックエンド
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

### フロントエンド
```bash
cd frontend
npm run dev
```
