# Notion → GitHub 自動同期（AtCoder Snippets）

Notion の「競技プログラミング Snippets」と**配下の子ページだけ**を Markdown で定期的に GitHub に同期する。AI は実行しない。実際の公開先はこのリポジトリの `notes/`。Notion を編集すれば、毎時17分ごろ（UTC・JSTとも分は17分）に差分がコミットされる。Actions のスケジュール実行は遅延・欠落することがあるため、コンテスト前は手動実行で公開を確認する。

## 事前準備

1. GitHub で新しい **Public** リポジトリ（例：`atcoder-notion-snippets`）を作成する。このフォルダの内容を、隠しディレクトリ `.github/` も含めてリポジトリに追加する。公開前に Notion の該当ツリー全体に機密情報がないか確認する。
2. [Notion integrations](https://www.notion.so/profile/integrations) または [Notion developers](https://developers.notion.com/) で内部インテグレーションを作成し、**Read content** 権限を付与してシークレットを取得する。
3. Notion の [競技プログラミング Snippets](https://www.notion.so/3e29b4299e61816a96cad16cbd4d2ca4) を開き、`...` → **Connections**（または共有メニュー内の連携）からそのインテグレーションを接続する。子ページにもアクセスできることを確認する。
4. GitHub リポジトリの `Settings` → `Secrets and variables` → `Actions` → `New repository secret` から、名前 `NOTION_API_KEY` でインテグレーショントークンを保存する。**トークンをコードに直接書かない**。
5. `Actions` → `Sync Notion to GitHub` → `Run workflow` を実行して、`notes/` にページが生成されることを確認する。GitHub Actions のリポジトリ設定で `Workflow permissions: Read and write permissions` が必要な場合は設定する（workflow 内では `contents: write` を指定済み）。
6. 以後は約1時間ごとの自動同期。最新の手動同期が必要なら `Run workflow` を押す。更新されたコードはコンテスト開始**前に公開コミット**されたことを必ず確認する。

## コードの参照URL

コンテスト中に AI で生成したコードをコピーする場合、AtCoder の現行ルールに従って参照URLを提出コードに添付する。可能なら該当ページの GitHub **固定コミットURL** を使う：

```python
# Source: https://github.com/<USER>/<REPOSITORY>/blob/<COMMIT_SHA>/notes/.../foo.md
```

**自動同期しているだけでは条件を満たさない。** 公開リポジトリ、コンテスト開始前の公開、コピー時の出典URLが必要。コンテスト中は AI に問い合わせない。ライセンスも各自で確認する。

## 動作と注意

- 一方向同期：Notion → GitHub。GitHub の `notes/` を直接編集しても次回同期時に上書きされる。
- 対象は特定の Notion 親ページとその「子ページ」ブロック以下のみ。ほかの Notion ページは同期しない。子データベースがあれば誤公開を避けるためエラー終了する。
- Markdown は Notion の [公式 Markdown API](https://developers.notion.com/reference/retrieve-page-markdown) から取得する。コードブロックも取得した Markdown のまま保存する。独自 Notion タグやリンク、アップロードした画像の一時URLは GitHub 上で完全に再現されない場合がある。
- API エラーやページ欠落・打ち切りを検知したときは同期を失敗させ、未完成のスナップショットをコミットしない。
- **削除・改名された Notion ページは次の GitHub コミットでは消えるが、過去の Git 履歴には残る**。公開したくない内容は最初から親ページ以下に置かない。
- GitHub Actions は既定で UTC。`17 * * * *` は毎時17分（日本時間でも毎時17分）に予定されるが、厳密な実行保証はない。

## ローカルで同期する場合

Python 3.12 以上。追加依存ライブラリなし。

```bash
export NOTION_API_KEY='secret_xxx'  # ローカルの環境変数にのみ設定
python sync_notion.py
```

Root page ID は `ROOT_PAGE_ID` 環境変数で変更できる（既定は既存の「競技プログラミング Snippets」）。
