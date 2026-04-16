# サビプレイヤー

フォルダ内の MP3 からランダムに1曲選び、ランダムな15秒を再生するプレイヤー。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

## 機能

- フォルダ内の MP3 をランダムに選曲
- 曲の中からランダムな位置の15秒を再生（イントロ・アウトロを避けた範囲）
- 15秒経過したら自動で次の曲へ
- 再生秒数を5〜60秒でカスタマイズ可能
- 一時停止 / 次の曲 / 停止

## セットアップ

### 必要なもの

- Python 3.9 以上
- pygame-ce または pygame (2.0 以上)
- mutagen

### インストール

```bash
pip install pygame-ce mutagen
```

### 使い方

1. MP3 ファイルを `player.py` と同じフォルダに入れる
2. 実行する

```bash
python player.py
```