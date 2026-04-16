# サビプレイヤー

フォルダ内の MP3 からランダムに1曲選び、ランダムな20秒を再生するプレイヤー。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

## 機能

- フォルダ内のMP3などをランダムに選曲
- 曲の中からランダムな位置の20秒を再生
- 20秒経過したら自動で次の曲へ
- 再生秒数を5〜60秒でカスタマイズ可能
- 一時停止 / 次の曲

## セットアップ

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