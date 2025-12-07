# プロジェクト進捗状況

## 現在の状態
- **最終更新**: 2025-12-07
- **アクティブタスク**: ローカル動作確認

## 完了済み
- [x] プロジェクト作成
- [x] 技術スタック決定（Next.js + FastAPI + Gemini）
- [x] 仕様書作成（.tmp/requirements.md）
- [x] バックエンド実装（FastAPI + youtube-transcript-api + Gemini）
- [x] フロントエンド実装（Next.js + ReactMarkdown）

## 未完了・保留
- [ ] ローカル動作確認
- [ ] 結合テスト
- [ ] Renderデプロイ

## 次セッションへの引き継ぎ
- **次のアクション**:
  1. Gemini API Key取得・設定
  2. バックエンド起動テスト
  3. フロントエンド起動テスト
  4. 結合テスト

## 起動方法

### バックエンド
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .envにGEMINI_API_KEYを設定
uvicorn app.main:app --reload
```

### フロントエンド
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```
