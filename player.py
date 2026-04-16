#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サビプレイヤー
  - フォルダ内のMP3からランダムに1曲選び、ランダムな20秒を再生
  - 20秒経過したら自動で次の曲へ
"""

import tkinter as tk
from tkinter import ttk
import pygame
import os
import random

try:
    from mutagen.mp3 import MP3
    def get_duration(path):
        try:
            return MP3(path).info.length
        except Exception:
            return 240.0
except ImportError:
    def get_duration(path):
        return 240.0

MUSIC_DIR = os.path.dirname(os.path.abspath(__file__))

# ── カラー ────────────────────────────────────────────────────────────────────
BG       = '#12121f'
PANEL    = '#1c1c30'
DEEP     = '#0d0d1a'
ACCENT   = '#ff4c6a'
TEXT     = '#e8e8f0'
SUBTEXT  = '#7070a0'
GREEN    = '#40c060'
YELLOW   = '#f0c040'

CLIP_SECS   = 20   # 1クリップの再生時間(秒)


class RandomPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("サビプレイヤー")
        self.root.geometry("600x420")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.songs = []
        self.current_song = None
        self.current_start = 0.0
        self.song_duration = 0.0
        self.is_playing = False
        self.clip_secs = CLIP_SECS
        self._after_id = None

        self.load_songs()
        self.build_ui()

    # ── 曲リスト ──────────────────────────────────────────────────────────────

    def load_songs(self):
        exts = {'.mp3', '.wav', '.wma', '.flac', '.ogg', '.m4a', '.aac'}
        self.songs = sorted(
            [f for f in os.listdir(MUSIC_DIR)
             if os.path.splitext(f.lower())[1] in exts
             and os.path.isfile(os.path.join(MUSIC_DIR, f))]
        )

    # ── UI 構築 ───────────────────────────────────────────────────────────────

    def build_ui(self):
        # ─ タイトル
        tk.Label(self.root, text="サビプレイヤー", bg=BG, fg=ACCENT,
                 font=('Yu Gothic UI', 18, 'bold')).pack(pady=(20, 4))

        tk.Label(self.root, text=f"ランダムに {CLIP_SECS} 秒再生",
                 bg=BG, fg=SUBTEXT, font=('Yu Gothic UI', 10)).pack()

        # ─ 曲名
        song_frame = tk.Frame(self.root, bg=PANEL, pady=10)
        song_frame.pack(fill=tk.X, padx=20, pady=14)

        self.song_var = tk.StringVar(value="▶ を押してスタート")
        tk.Label(song_frame, textvariable=self.song_var, bg=PANEL, fg=TEXT,
                 font=('Yu Gothic UI', 11, 'bold'),
                 wraplength=540, justify='center').pack(padx=10)

        self.pos_var = tk.StringVar(value="")
        tk.Label(song_frame, textvariable=self.pos_var, bg=PANEL, fg=SUBTEXT,
                 font=('Yu Gothic UI', 9)).pack()

        # ─ プログレスバー (15秒分)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Clip.Horizontal.TProgressbar',
                         troughcolor=DEEP, background=ACCENT,
                         darkcolor=ACCENT, lightcolor=ACCENT,
                         bordercolor=DEEP, thickness=12)

        bar_frame = tk.Frame(self.root, bg=BG)
        bar_frame.pack(fill=tk.X, padx=20, pady=(0, 8))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            bar_frame, variable=self.progress_var,
            maximum=self.clip_secs, mode='determinate',
            style='Clip.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X)

        self.remain_var = tk.StringVar(value="")
        tk.Label(bar_frame, textvariable=self.remain_var, bg=BG, fg=SUBTEXT,
                 font=('Courier New', 9)).pack(anchor='e')

        # ─ ボタン群
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=10)

        def btn(parent, text, cmd, color=PANEL, fg=TEXT, size=12, w=8):
            return tk.Button(parent, text=text, command=cmd,
                             bg=color, fg=fg, activebackground=ACCENT,
                             activeforeground='white', bd=0, cursor='hand2',
                             font=('Yu Gothic UI', size, 'bold'),
                             width=w, pady=8)

        self.play_btn = btn(btn_frame, "▶  再生", self.toggle_play,
                            color=ACCENT, fg='white', size=13, w=12)
        self.play_btn.pack(side=tk.LEFT, padx=8)

        btn(btn_frame, "⏭  次の曲", self.next_random,
            color=PANEL, fg=TEXT, size=11, w=10).pack(side=tk.LEFT, padx=8)


        # ─ 秒数スライダー
        sec_frame = tk.Frame(self.root, bg=BG)
        sec_frame.pack(pady=(6, 0))

        tk.Label(sec_frame, text="再生秒数:", bg=BG, fg=SUBTEXT,
                 font=('Yu Gothic UI', 9)).pack(side=tk.LEFT)

        self.sec_var = tk.IntVar(value=CLIP_SECS)
        self.sec_label = tk.Label(sec_frame, text=f"{CLIP_SECS}秒", bg=BG, fg=YELLOW,
                                   font=('Yu Gothic UI', 9, 'bold'), width=4)
        self.sec_label.pack(side=tk.RIGHT, padx=(4, 0))

        style.configure('Sec.Horizontal.TScale',
                         background=BG, troughcolor=DEEP, sliderthickness=12)
        sec_slider = ttk.Scale(sec_frame, from_=5, to=60, orient=tk.HORIZONTAL,
                                variable=self.sec_var, length=200,
                                style='Sec.Horizontal.TScale',
                                command=self._on_sec_change)
        sec_slider.pack(side=tk.LEFT, padx=6)

        # ─ ステータス
        self.status_var = tk.StringVar(value=f"{len(self.songs)} 曲を認識")
        tk.Label(self.root, textvariable=self.status_var, bg=BG, fg=SUBTEXT,
                 font=('Yu Gothic UI', 8)).pack(side=tk.BOTTOM, pady=6)

    # ── イベント ───────────────────────────────────────────────────────────────

    def _on_sec_change(self, val):
        v = int(float(val))
        self.clip_secs = v
        self.progress_bar.config(maximum=v)
        self.sec_label.config(text=f"{v}秒")

    def toggle_play(self):
        if self.is_playing:
            self._pause()
        else:
            if self.current_song and pygame.mixer.music.get_pos() >= 0:
                self._resume()
            else:
                self.next_random()

    def _pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False
        self.play_btn.config(text="▶  再生")
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _resume(self):
        pygame.mixer.music.unpause()
        self.is_playing = True
        self.play_btn.config(text="⏸  一時停止")
        self._tick_start = _now_ms()
        self._tick_elapsed_base = self._elapsed
        self._schedule_tick()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_song = None
        self.play_btn.config(text="▶  再生")
        self.progress_var.set(0)
        self.remain_var.set("")
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.song_var.set("▶ を押してスタート")
        self.pos_var.set("")
        self.status_var.set(f"{len(self.songs)} 曲を認識")

    # ── ランダム再生 ──────────────────────────────────────────────────────────

    def next_random(self):
        if not self.songs:
            self.status_var.set("MP3 ファイルが見つかりません")
            return

        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None

        pygame.mixer.music.stop()

        song = random.choice(self.songs)
        path = os.path.join(MUSIC_DIR, song)
        duration = get_duration(path)

        # ランダム開始位置: 曲の 20%〜75% あたり (イントロ・アウトロを避ける)
        lo = 0
        hi = max(0, duration - self.clip_secs)
        start = random.uniform(lo, hi)

        try:
            pygame.mixer.music.load(path)
        except pygame.error:
            self.songs.remove(song)
            self.status_var.set(f"スキップ（非対応形式）: {song}")
            self.next_random()
            return
        pygame.mixer.music.play(start=start)

        self.current_song = song
        self.current_start = start
        self.song_duration = duration
        self.is_playing = True
        self._elapsed = 0.0
        self._tick_start = _now_ms()
        self._tick_elapsed_base = 0.0

        # 表示名を短縮
        display = song
        if len(display) > 55:
            display = display[:52] + "..."
        self.song_var.set(display)
        self.pos_var.set(f"{_fmt(start)} 〜 {_fmt(start + self.clip_secs)}"
                         f"  /  全 {_fmt(duration)}")
        self.play_btn.config(text="⏸  一時停止")
        self.status_var.set(f"再生中 ♪  ({len(self.songs)} 曲中からランダム)")

        self._schedule_tick()

    # ── チック処理 ────────────────────────────────────────────────────────────

    def _schedule_tick(self):
        self._after_id = self.root.after(100, self._tick)

    def _tick(self):
        if not self.is_playing:
            return

        now = _now_ms()
        self._elapsed = self._tick_elapsed_base + (now - self._tick_start) / 1000.0

        # プログレス更新
        e = min(self._elapsed, self.clip_secs)
        self.progress_var.set(e)
        remain = max(0.0, self.clip_secs - self._elapsed)
        self.remain_var.set(f"{remain:.1f}秒")

        # クリップ終了 → 次へ
        if self._elapsed >= self.clip_secs:
            self.next_random()
            return

        # 曲が止まっていたら次へ
        if not pygame.mixer.music.get_busy():
            self.next_random()
            return

        self._schedule_tick()


def _now_ms():
    import time
    return time.monotonic() * 1000


def _fmt(sec):
    m = int(sec) // 60
    s = int(sec) % 60
    return f"{m}:{s:02d}"


def main():
    root = tk.Tk()
    app = RandomPlayer(root)  # noqa: F841

    def on_close():
        pygame.mixer.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == '__main__':
    main()
