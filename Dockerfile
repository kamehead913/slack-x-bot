# ベースイメージ（Python 3.10）
FROM python:3.10-slim

# 作業ディレクトリ作成
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt requirements.txt

# 依存パッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# ポート設定（Cloud Runは8080固定）
ENV PORT=8080

# Flaskを起動
CMD ["python", "main.py"]
