# 🍶 日本酒マップ (Sake Map)

日本全国の日本酒を都道府県別に探索できる Django Web アプリケーションです。  
[さけのわ API](https://muro.sakenowa.com/sakenowa-data/) のデータを活用し、銘柄検索・フレーバーチャート表示・飲酒ログ・お気に入り管理などの機能を提供します。

---

## 主な機能

| 機能 | 説明 |
|------|------|
| **都道府県マップ** | Geolonia の日本地図 SVG で全国を表示。飲酒割合に応じて色が変化 |
| **都道府県詳細** | 各県の蔵元・銘柄を一覧表示 |
| **日本酒一覧・検索** | 銘柄名・蔵元名でキーワード検索 |
| **日本酒詳細** | フレーバーチャート（華やか・芳醇・重厚・穏やか・ドライ・軽快）を表示 |
| **マイログ** | 飲んだ日本酒を記録（飲んだ日・評価・メモ）。地図上で飲酒進捗を可視化 |
| **お気に入り** | 「いいね」した日本酒をカードグリッドで一覧表示 |
| **ログイン / ログアウト** | ユーザー認証（現在はadminのみ） |

---

## 技術スタック

- **Python** 3.13+
- **Django** 5.2+
- **SQLite** (デフォルト)
- **さけのわ API** — 都道府県・蔵元・銘柄・フレーバーチャートデータ
- **Geolonia japanese-prefectures** — 日本地図 SVG

---

## セットアップ

### 1. リポジトリのクローンと仮想環境

```bash
git clone <repository-url>
cd sake_map
python -m venv .venv
source .venv/bin/activate
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env` ファイルを作成：

```ini
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
```

### 4. データベースのマイグレーション

```bash
python manage.py migrate
```

### 5. さけのわ API からデータ取得

```bash
python manage.py fetch_sakenowa
```

これにより以下のデータが登録されます：

- 48 都道府県（エリア）
- 約 1,700 蔵元
- 約 3,100 銘柄
- 約 1,300 フレーバーチャート

### 6. 管理ユーザーの作成

```bash
python manage.py createsuperuser
```

### 7. 開発サーバーの起動

```bash
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/prefecture/ にアクセスしてください。

---

## URL 一覧

| URL | ページ |
|-----|--------|
| `/prefecture/` | 都道府県マップ（トップ） |
| `/prefecture/<id>/` | 都道府県詳細 |
| `/sake/` | 日本酒一覧・検索 |
| `/sake/<id>/` | 日本酒詳細 + ログ登録 |
| `/mylog/` | マイログ一覧 + 飲酒マップ |
| `/mylog/<id>/` | ログ詳細 + 編集 |
| `/favorites/` | お気に入り一覧 |
| `/login/` | ログイン |
| `/logout/` | ログアウト |
| `/admin/` | Django 管理画面 |

---

## プロジェクト構成

```
sake_map/
├── manage.py
├── requirements.txt
├── .env                  
├── .gitignore
├── README.md
├── sake_map/              # プロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── sake_app/              # メインアプリ
    ├── models.py          # Prefecture, Brewery, Sake, SakeLog
    ├── views.py           # 各ページのビュー
    ├── urls.py            # URLルーティング
    ├── forms.py           # SakeLogForm
    ├── admin.py           # 管理画面登録
    ├── management/
    │   └── commands/
    │       └── fetch_sakenowa.py   # APIデータ取得コマンド
    ├── static/
    │   └── sake_app/
    │       └── map-full.svg        # 日本地図SVG
    └── templates/
        └── sake_app/
            ├── base.html       
            ├── japan_map.html       
            ├── login.html   
            ├── prefecture_list.html
            ├── prefecture_detail.html
            ├── sake_list.html
            ├── sake_detail.html
            ├── sakelog_list.html
            ├── sakelog_detail.html
            └── favorite_list.html
```

---

## データモデル

```
Prefecture (都道府県)
  └── Brewery (蔵元)
        └── Sake (日本酒)  ← フレーバーチャート f1〜f6
              └── SakeLog (ユーザーログ)  ← 飲んだ/いいね/評価/メモ
```

---

## さけのわ API について

本アプリは [さけのわデータ](https://muro.sakenowa.com/sakenowa-data/) を利用しています。  
データの利用にあたっては、さけのわの利用規約に従ってください。

---

## ライセンス

地図 SVG: [Geolonia japanese-prefectures](https://github.com/geolonia/japanese-prefectures)
