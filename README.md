# サビプレイヤー

フォルダ内の MP3 を全曲シャッフルして一周し、各曲のランダムな位置を指定秒数だけ再生するプレイヤー。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

### 機能

- 全曲を一周シャッフル再生（一周後は自動で次のシャッフルへ）
- 1曲あたりの再生秒数をスライダーで調整（5〜60秒、5秒刻み）
- 設定は自動保存・次回起動時に復元

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
