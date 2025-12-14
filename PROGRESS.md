# プロジェクト進捗状況

## 現在の状態
- **最終更新**: 2025-12-14
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
- [x] Obsidian保存をURI scheme方式に変更
- [x] コードレビュー改善（Issue #1）
  - デッドコード削除（digest.py: 198行→81行）
  - CORS設定を環境変数化（FRONTEND_URL）
  - next/fontでGoogle Fonts読み込みに移行
- [x] Render Blueprints移行（2025-12-14）
  - render.yaml: plan: free明示、FRONTEND_URL追加
  - PYTHON_VERSION: 3.11 → 3.11.0（パッチバージョン必須）
- [x] 解説文途切れ問題修正（2025-12-14）
  - max_output_tokens: 4096 → 8192
- [ ] ~~音声読み上げ機能（2025-12-14）~~ → 断念（Web Speech APIがChrome環境で動作せず）

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

### Obsidian保存方式
- **採用**: Obsidian URI scheme（`obsidian://new`）
- **理由**: サーバーサイド（Render）からローカルファイルシステムへのアクセスは不可能
- **旧方式の問題**: WSLパス（`/mnt/c/...`）変換はローカル開発環境でのみ有効
- **メリット**: Obsidianが起動して即座にノートが開かれる、以前より使いやすい

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
