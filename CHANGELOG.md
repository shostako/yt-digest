# 変更履歴

このリポジトリの主な変更を新しい順に書く。日付は日本時間。

## 2026-10-22

### セキュリティ
- 画面側の Next.js を 14.2.0 から 15.5.28 に、React を 18 から 19 に上げた（#6）。
  - 画像最適化の口（`/_next/image`）から任意のコードを実行できる脆弱性（GHSA-2xp9-vwfh-vxw4、critical）を直した。SSRF、DoS、キャッシュ汚染（high）も直った。
  - postcss は `overrides` で 8.5 系に固定した。Next 15.5 が固定している 8.4.31 にはビルド時の high が残るため。
  - `npm audit` は 4 件（critical 1・high 3）から 0 件になった。

### 修正
- 解説の生成が失敗していたのを直した（#8）。
  - Gemini のモデルを `gemini-2.5-flash` から `gemini-3.8-flash` に替えた。2.5 Flash は新しい利用者に提供されなくなり、404 を返していた。
  - SDK を、提供が終わった `google-generativeai` から `google-genai` に移した。
  - 応答の本文が空のとき、分かりやすいエラーを返すようにした。
  - Gemini 3 系は思考のトークンも出力の上限に数えるので、`max_output_tokens` を 8192 から 16384 にした。
- 古い動画でサムネイルが灰色の仮の絵になるのを直した。高画質のサムネイル（maxresdefault）が無い動画では hqdefault を使う。
- 解説の中の太字（`**…**`）が、かぎ括弧などの約物の隣で太字にならず、`**` がそのまま見えていたのを直した。Markdown の表示に `remark-cjk-friendly` を足した。

### 運用
- 本番（Render の yt-digest-api）の `GEMINI_API_KEY` を、yt-digest 専用の新しいプロジェクトのキーに替えた。前のキーは無効になっていた。
