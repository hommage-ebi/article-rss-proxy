# article-rss-proxy

arXiv の論文を取得し、Gemini でフィルタリング・翻訳した上で RSS フィードとして配信するツールです。

## 特徴

- arXiv API から指定カテゴリの論文を取得
- Gemini API を使用して AI4Science 関連論文をフィルタリング
- 英語の Abstract を日本語に翻訳
- 論文の図・著者・所属情報を取得
- RSS フィードとして配信（GitHub Pages 対応）
- GitHub Actions による自動更新（毎日 11:00 JST）

## セットアップ

```bash
# 環境構築
# 方法1: conda を使用する場合
conda create -n arxiv-rss python=3.12 && conda activate arxiv-rss

# 方法2: venv を使用する場合
python -m venv .venv && source .venv/bin/activate  # Linux/macOS
# または
python -m venv .venv && .venv\Scripts\activate     # Windows

# uv のインストール (https://github.com/astral-sh/uv)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存パッケージのインストール
uv pip install -r requirements.txt

# 環境変数の設定
# .env.example をコピーして .env を作成し、GEMINI_API_KEY を設定
cp .env.example .env
# .env ファイルを編集して API キーを設定
```

## 使用方法

```bash
# RSS フィードの生成
python -m src.main
# docs/index.xml が生成されます
```

## GitHub Pages での配信

1. リポジトリの Settings > Pages で以下を設定:
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /docs

2. 設定後、RSS フィードは以下の URL で配信されます:
   `https://<user>.github.io/article-rss-proxy/index.xml`

## 自動更新

デフォルトでは GitHub Actions により毎日 11:00 JST (02:00 UTC) に自動更新されます。
必要に応じて `.github/workflows/arxiv_rss.yml` のスケジュールやフィルタ条件を調整してください。
