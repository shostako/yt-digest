# yt-digest 要件定義

## 概要
YouTube動画のURLを入力すると、字幕を取得してGemini APIで詳細な解説を生成するWebアプリ

## 機能要件

### MVP（最小構成）
1. **URL入力**
   - YouTubeのURL（通常形式・短縮形式両対応）を入力
   - 動画IDを抽出

2. **字幕取得**
   - youtube-transcript-apiで字幕テキストを取得
   - 日本語字幕優先、なければ英語、なければ自動生成
   - 字幕がない場合はエラーメッセージ表示

3. **解説生成**
   - Gemini APIに字幕テキストを送信
   - 詳細な解説を生成（要約ではなく解説）
   - 出力形式：Markdown

4. **結果表示**
   - 動画タイトル表示
   - 解説をMarkdownレンダリング
   - コピー機能

### 将来拡張（v2以降）
- 履歴保存
- 解説のカスタマイズ（詳細度、観点）
- チャプター別解説
- エクスポート機能（PDF、Notion）

## 非機能要件
- レスポンス時間：30秒以内（長い動画でも）
- エラーハンドリング：ユーザーフレンドリーなメッセージ
- レスポンシブデザイン

## API設計

### POST /api/digest
**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=xxxxx"
}
```

**Response:**
```json
{
  "video_id": "xxxxx",
  "title": "動画タイトル",
  "digest": "## 解説\n\n...",
  "transcript_language": "ja"
}
```

**Error Response:**
```json
{
  "error": "NO_TRANSCRIPT",
  "message": "この動画には字幕がありません"
}
```

## 技術詳細

### 字幕取得フロー
1. URLから動画ID抽出（正規表現）
2. youtube-transcript-apiで字幕リスト取得
3. 優先順位：日本語手動 > 英語手動 > 日本語自動 > 英語自動
4. 字幕テキストを結合

### Geminiプロンプト設計
```
以下はYouTube動画の字幕テキストです。
この動画の内容について詳細に解説してください。

【解説に含めるべき要素】
- 動画の主題と目的
- 主要なポイント（箇条書き）
- 重要な概念の説明
- 結論・まとめ

【字幕テキスト】
{transcript}
```
