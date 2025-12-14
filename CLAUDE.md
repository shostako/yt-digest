# yt-digest

## 概要
YouTube動画の字幕を取得し、Gemini APIで詳細な解説を生成するWebアプリ

## 技術スタック
- **フロントエンド**: Next.js (App Router)
- **バックエンド**: Python FastAPI
- **字幕取得**: youtube-transcript-api
- **LLM**: Google Gemini API
- **デプロイ**: Render（フロント・API両方）

## 作業ログの習慣
**重要：セッション終了前に必ず作業ログを記録すること**
- ログ保存先：`logs/yyyy-MM.md`
- その日の作業内容、技術的発見、教訓を記録

## セッション開始時の必須アクション
**重要：新しいセッションでこのプロジェクトに入った際は、以下を最初に実行すること**

1. **PROGRESS.md を読む**: `PROGRESS.md` を開き、現在の状態と未完了タスクを把握
2. **GitHub Issues 確認**: `gh issue list` でオープンなIssueを確認（GitHub連携していない場合はスキップ）
3. **次のアクション確認**: 「次セッションへの引き継ぎ」セクションを確認し、継続すべきタスクを認識
4. **ユーザーへの報告**: 認識した未完了タスク・Issueをユーザーに報告し、優先度を確認

**目的**: セッション間の引き継ぎを確実にし、前回の作業を途切れなく継続するため

**GitHub連携の判定**: `.git/config`に`[remote "origin"]`があればGitHub連携済み

## PROGRESS.md手動更新時の注意
- **時刻更新時は必ず`date '+%Y-%m-%d %H:%M'`で現在時刻を確認してから記入**
- 推測や概算で時刻を入れない

## 参照
- 開発哲学: `/home/shostako/ClaudeCode/knowledge/project-setup.md`
