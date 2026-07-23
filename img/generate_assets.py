#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README 用 SVG 素材ジェネレータ
------------------------------------------------------------------
使い方:
    python3 generate_assets.py            # ./assets へ出力
    python3 generate_assets.py -o ./img   # 出力先を指定

下の CONFIG だけ書き換えれば文字列・色・数値を変更できます。
"""

import argparse
import math
import os
import random
from html import escape

# ==================================================================
# CONFIG — ここだけ編集すれば OK
# ==================================================================

CONFIG = {
    # ---------------- 配色 ----------------
    "colors": {
        "bg":       "#070B14",   # 背景（濃い方）
        "bg_light": "#0C1220",   # 背景（薄い方 / グラデ上端）
        "accent":   "#5EEAD4",   # メインアクセント（ティール）
        "accent2":  "#7C9CFF",   # サブアクセント（ペリウィンクル）
        "text":     "#C8D4E6",   # 本文テキスト
        "dim":      "#5A6B87",   # 補助テキスト
    },

    # 等幅フォントのスタック（先頭から順に使われます）
    "font_mono": '"SFMono-Regular",Consolas,"Roboto Mono","DejaVu Sans Mono",monospace',

    # 星の配置などをランダム生成する際のシード（変えると星並びが変わる）
    "seed": 4242,

    # ---------------- hero.svg ----------------
    "hero": {
        "width": 1200,
        "height": 340,
        "eyebrow":  "PROFILE",   # タイトル上の小さい行
        "title":    "NAGA-T",                       # 大見出し
        "tagline":  "NLP  ·  GENERATIVE AI  ·  WEB APPLICATION",
        "footnote": "UNIVERSITY OF THE RYUKYUS — OKINAWA, JP",
        "show_cursor": True,        # タイトル横の点滅カーソル
        "show_orbit": True,         # 右側の軌道リング
        "show_spectrum": True,      # 下端のスペクトラムバー
        "star_count": 90,
        "title_font_size": 62,
        "title_letter_spacing": 9,
    },

    # ---------------- pipeline.svg ----------------
    "pipeline": {
        "width": 1000,
        "height": 250,
        "header": "RESEARCH MODULE // AUTOMATED QUALITY EVALUATION",
        "stage1_label": "01 / INPUT",
        "stage1_title": "応対テキスト",
        "stage1_note":  "OPERATOR RESPONSE STREAM",
        "stage2_label": "02 / ANALYSIS",
        "node_line1":   "NLP",      # 中央ノード 1行目
        "node_line2":   "LLM",      # 中央ノード 2行目
        "stage3_label": "03 / EVALUATION",
        # 評価軸: (ラベル, 0.0〜1.0 の値)
        "metrics": [
            ("ACCURACY", 0.86),
            ("EMPATHY",  0.72),
            ("CLARITY",  0.91),
            ("CLOSING",  0.64),
        ],
        "stage3_note": "CONSISTENT · LOW-COST · AUTOMATED",
        "status_label": "STATUS: IN PROGRESS",
        "status_value": 0.63,       # 進捗バー 0.0〜1.0
    },

    # ---------------- divider.svg ----------------
    "divider": {
        "width": 1000,
        "height": 16,
        "tick_positions": [120, 300, 500, 700, 880],  # 目盛りの x 座標
        "packet_duration": 5.5,                        # 走る光の周期（秒）
    },
}

# ==================================================================
# 以下は生成ロジック（通常は編集不要）
# ==================================================================


def build_hero(cfg):
    c, h = cfg["colors"], cfg["hero"]
    W, H = h["width"], h["height"]
    mono = cfg["font_mono"]

    stars = "\n    ".join(
        f'<circle cx="{round(random.uniform(0, W), 1)}" cy="{round(random.uniform(0, H), 1)}" '
        f'r="{random.choice([0.5, 0.7, 0.9, 1.1])}" fill="#fff" '
        f'opacity="{round(random.uniform(.12, .55), 2)}" '
        f'style="animation:tw {round(random.uniform(3, 8), 1)}s ease-in-out '
        f'{round(random.uniform(0, 6), 1)}s infinite"/>'
        for _ in range(h["star_count"])
    )

    spectrum = ""
    if h["show_spectrum"]:
        bars = []
        for i in range(64):
            x = 40 + i * 18
            bh = random.uniform(4, 26)
            bars.append(
                f'<rect x="{x}" y="{round(300 - bh, 1)}" width="6" height="{round(bh, 1)}" '
                f'fill="{c["accent"]}" opacity="0.5" '
                f'style="transform-origin:{x + 3}px 300px;'
                f'animation:eq {round(random.uniform(1.6, 2.8), 2)}s ease-in-out '
                f'{round(i * 0.045, 3)}s infinite"/>'
            )
        spectrum = "\n    ".join(bars)

    ticks = "\n    ".join(
        f'<rect x="46" y="{92 + i * 13}" width="{random.choice([10, 16, 22, 28])}" height="2" '
        f'fill="{c["accent2"]}" opacity="{round(random.uniform(.2, .7), 2)}"/>'
        for i in range(9)
    )

    orbit = ""
    if h["show_orbit"]:
        orbit = f'''<g opacity="0.85" fill="none">
    <circle cx="1058" cy="168" r="70" stroke="{c["accent"]}" stroke-opacity="0.18" stroke-width="1"/>
    <g class="r1">
      <circle cx="1058" cy="168" r="70" stroke="{c["accent"]}" stroke-opacity="0.7" stroke-width="1.6" stroke-dasharray="30 180"/>
      <circle cx="1128" cy="168" r="3.5" fill="{c["accent"]}" filter="url(#glow)"/>
    </g>
    <g class="r2">
      <circle cx="1058" cy="168" r="46" stroke="{c["accent2"]}" stroke-opacity="0.6" stroke-width="1.4" stroke-dasharray="14 60"/>
      <circle cx="1012" cy="168" r="2.8" fill="{c["accent2"]}"/>
    </g>
    <circle cx="1058" cy="168" r="16" fill="{c["accent"]}" fill-opacity="0.10" stroke="{c["accent"]}" stroke-opacity="0.4"/>
    <circle cx="1058" cy="168" r="3" fill="{c["accent"]}"/>
  </g>'''

    # タイトル幅に応じてカーソル位置を推定（等幅前提のざっくり計算）
    fs = h["title_font_size"]
    ls = h["title_letter_spacing"]
    cursor_x = 90 + len(h["title"]) * (fs * 0.60 + ls)
    cursor = ""
    if h["show_cursor"]:
        cursor = (f'<text class="cur" x="{round(cursor_x)}" y="182" font-size="{fs}" '
                  f'font-weight="bold" fill="{c["accent"]}">_</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(h["title"])}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">
      <stop offset="0%" stop-color="{c["bg_light"]}"/>
      <stop offset="100%" stop-color="{c["bg"]}"/>
    </linearGradient>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{c["accent"]}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{c["accent"]}" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="{c["accent"]}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{c["accent"]}" stop-opacity="0"/>
      <stop offset="20%" stop-color="{c["accent"]}" stop-opacity="0.9"/>
      <stop offset="80%" stop-color="{c["accent2"]}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{c["accent2"]}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0 H0 V40" fill="none" stroke="{c["accent"]}" stroke-opacity="0.06" stroke-width="1"/>
    </pattern>
    <radialGradient id="vig" cx="50%" cy="45%" r="72%">
      <stop offset="55%" stop-color="#000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0.65"/>
    </radialGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.4"/>
    </filter>
    <style>
      @keyframes tw    {{ 0%,100% {{opacity:.1}} 50% {{opacity:.75}} }}
      @keyframes eq    {{ 0%,100% {{transform:scaleY(.35)}} 50% {{transform:scaleY(1.5)}} }}
      @keyframes sweep {{ 0% {{transform:translateY(-60px)}} 100% {{transform:translateY(400px)}} }}
      @keyframes rev   {{ 0% {{transform:rotate(0deg)}} 100% {{transform:rotate(360deg)}} }}
      @keyframes rev2  {{ 0% {{transform:rotate(360deg)}} 100% {{transform:rotate(0deg)}} }}
      @keyframes draw  {{ 0% {{transform:scaleX(0)}} 100% {{transform:scaleX(1)}} }}
      @keyframes fade  {{ 0% {{opacity:0;transform:translateY(6px)}} 100% {{opacity:1;transform:translateY(0)}} }}
      @keyframes blink {{ 0%,49% {{opacity:1}} 50%,100% {{opacity:0}} }}
      .scan {{ animation: sweep 7s linear infinite; }}
      .r1   {{ animation: rev 26s linear infinite; transform-origin:1058px 168px; }}
      .r2   {{ animation: rev2 17s linear infinite; transform-origin:1058px 168px; }}
      .rule {{ animation: draw 1.6s cubic-bezier(.2,.8,.2,1) both; transform-origin:0 0; }}
      .f1   {{ animation: fade .9s ease-out .15s both; }}
      .f2   {{ animation: fade .9s ease-out .45s both; }}
      .f3   {{ animation: fade .9s ease-out .75s both; }}
      .cur  {{ animation: blink 1.1s step-end infinite; }}
      text  {{ font-family: {mono}; }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <g>
    {stars}
  </g>
  <rect class="scan" x="0" y="0" width="{W}" height="60" fill="url(#scan)"/>

  <g stroke="{c["accent"]}" stroke-opacity="0.45" stroke-width="1.5" fill="none">
    <path d="M24 46 H70 M24 46 V92"/>
    <path d="M{W - 24} 46 H{W - 70} M{W - 24} 46 V92"/>
    <path d="M24 {H - 46} H70 M24 {H - 46} V{H - 92}"/>
    <path d="M{W - 24} {H - 46} H{W - 70} M{W - 24} {H - 46} V{H - 92}"/>
  </g>
  {ticks}

  {orbit}

  <text class="f1" x="92" y="118" font-size="13" letter-spacing="5" fill="{c["dim"]}">{escape(h["eyebrow"])}</text>
  <text class="f2" x="90" y="182" font-size="{fs}" font-weight="bold" letter-spacing="{ls}" fill="{c["text"]}">{escape(h["title"])}</text>
  <text class="f2" x="90" y="182" font-size="{fs}" font-weight="bold" letter-spacing="{ls}" fill="{c["accent"]}" opacity="0.35" filter="url(#glow)">{escape(h["title"])}</text>
  {cursor}

  <rect class="rule" x="92" y="206" width="640" height="2" fill="url(#rule)"/>

  <text class="f3" x="92" y="240" font-size="16" letter-spacing="2.5" fill="{c["accent"]}">{escape(h["tagline"])}</text>
  <text class="f3" x="92" y="266" font-size="13" letter-spacing="2" fill="{c["dim"]}">{escape(h["footnote"])}</text>

  {spectrum}

  <rect width="{W}" height="{H}" fill="url(#vig)"/>
</svg>
'''


def build_pipeline(cfg):
    c, p = cfg["colors"], cfg["pipeline"]
    W, H = p["width"], p["height"]
    mono = cfg["font_mono"]

    wave = []
    for i in range(46):
        x = 62 + i * 7
        bh = abs(math.sin(i * 0.7)) * 26 + random.uniform(4, 16)
        wave.append(
            f'<rect x="{x}" y="{round(125 - bh / 2, 1)}" width="3" height="{round(bh, 1)}" rx="1.5" '
            f'fill="{c["accent"]}" opacity="0.75" '
            f'style="transform-origin:{x + 1.5}px 125px;'
            f'animation:eq {round(random.uniform(1.1, 2.2), 2)}s ease-in-out '
            f'{round(i * 0.035, 3)}s infinite"/>'
        )
    wave = "\n  ".join(wave)

    metrics = []
    for i, (label, val) in enumerate(p["metrics"]):
        y = 78 + i * 26
        val = max(0.0, min(1.0, float(val)))
        metrics.append(
            f'<text x="700" y="{y + 4}" font-size="10" letter-spacing="1.5" fill="{c["dim"]}">{escape(label)}</text>'
            f'<rect x="782" y="{y - 6}" width="150" height="8" rx="4" fill="{c["accent2"]}" fill-opacity="0.12"/>'
            f'<rect x="782" y="{y - 6}" width="{round(150 * val)}" height="8" rx="4" fill="{c["accent"]}" '
            f'style="transform-origin:782px {y}px;'
            f'animation:grow 2.2s cubic-bezier(.2,.9,.3,1) {round(i * 0.18 + 0.4, 2)}s both"/>'
        )
    metrics = "\n  ".join(metrics)

    status_w = round(120 * max(0.0, min(1.0, float(p["status_value"]))))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Research pipeline">
  <defs>
    <linearGradient id="pbg" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0%" stop-color="{c["bg_light"]}"/><stop offset="100%" stop-color="{c["bg"]}"/>
    </linearGradient>
    <pattern id="pgrid" width="25" height="25" patternUnits="userSpaceOnUse">
      <path d="M25 0 H0 V25" fill="none" stroke="{c["accent"]}" stroke-opacity="0.05"/>
    </pattern>
    <filter id="pglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
    <style>
      @keyframes eq    {{ 0%,100% {{transform:scaleY(.3)}} 50% {{transform:scaleY(1.35)}} }}
      @keyframes grow  {{ 0% {{transform:scaleX(0)}} 100% {{transform:scaleX(1)}} }}
      @keyframes flow  {{ 0% {{stroke-dashoffset:44}} 100% {{stroke-dashoffset:0}} }}
      @keyframes pulse {{ 0%,100% {{opacity:.35}} 50% {{opacity:.9}} }}
      @keyframes spin  {{ 0% {{transform:rotate(0)}} 100% {{transform:rotate(360deg)}} }}
      .flow {{ stroke-dasharray:6 16; animation: flow 1.3s linear infinite; }}
      .halo {{ animation: pulse 2.6s ease-in-out infinite; }}
      .spin {{ animation: spin 12s linear infinite; transform-origin:500px 125px; }}
      text  {{ font-family: {mono}; }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" rx="10" fill="url(#pbg)"/>
  <rect width="{W}" height="{H}" rx="10" fill="url(#pgrid)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{c["accent"]}" stroke-opacity="0.22"/>

  <text x="24" y="30" font-size="11" letter-spacing="3" fill="{c["dim"]}">{escape(p["header"])}</text>
  <line x1="24" y1="42" x2="{W - 24}" y2="42" stroke="{c["accent"]}" stroke-opacity="0.15"/>

  <text x="62" y="72" font-size="11" letter-spacing="2" fill="{c["accent"]}">{escape(p["stage1_label"])}</text>
  <text x="62" y="90" font-size="10" letter-spacing="1" fill="{c["dim"]}">{escape(p["stage1_title"])}</text>
  {wave}
  <rect x="56" y="98" width="336" height="54" rx="6" fill="none" stroke="{c["accent"]}" stroke-opacity="0.18"/>
  <text x="62" y="176" font-size="9" letter-spacing="1" fill="{c["dim"]}">{escape(p["stage1_note"])}</text>

  <line class="flow" x1="398" y1="125" x2="452" y2="125" stroke="{c["accent"]}" stroke-width="2"/>

  <g class="halo"><circle cx="500" cy="125" r="52" fill="{c["accent"]}" fill-opacity="0.07" filter="url(#pglow)"/></g>
  <g class="spin" fill="none">
    <circle cx="500" cy="125" r="46" stroke="{c["accent2"]}" stroke-opacity="0.45" stroke-dasharray="10 26"/>
  </g>
  <circle cx="500" cy="125" r="34" fill="{c["bg"]}" stroke="{c["accent"]}" stroke-opacity="0.65" stroke-width="1.5"/>
  <text x="500" y="120" text-anchor="middle" font-size="12" font-weight="bold" letter-spacing="1" fill="{c["accent"]}">{escape(p["node_line1"])}</text>
  <text x="500" y="136" text-anchor="middle" font-size="12" font-weight="bold" letter-spacing="1" fill="{c["accent"]}">{escape(p["node_line2"])}</text>
  <text x="500" y="196" text-anchor="middle" font-size="11" letter-spacing="2" fill="{c["dim"]}">{escape(p["stage2_label"])}</text>

  <line class="flow" x1="548" y1="125" x2="602" y2="125" stroke="{c["accent"]}" stroke-width="2"/>

  <text x="700" y="52" font-size="11" letter-spacing="2" fill="{c["accent"]}">{escape(p["stage3_label"])}</text>
  {metrics}
  <line x1="700" y1="196" x2="932" y2="196" stroke="{c["accent"]}" stroke-opacity="0.15"/>
  <text x="700" y="216" font-size="10" letter-spacing="1.5" fill="{c["dim"]}">{escape(p["stage3_note"])}</text>

  <text x="24" y="236" font-size="9" letter-spacing="2" fill="{c["dim"]}">{escape(p["status_label"])}</text>
  <rect x="180" y="229" width="120" height="5" rx="2.5" fill="{c["accent2"]}" fill-opacity="0.15"/>
  <rect x="180" y="229" width="{status_w}" height="5" rx="2.5" fill="{c["accent"]}"
        style="transform-origin:180px 231px;animation:grow 2s ease-out .6s both"/>
</svg>
'''


def build_divider(cfg):
    c, d = cfg["colors"], cfg["divider"]
    W, H = d["width"], d["height"]
    mid = H / 2

    ticks = "".join(
        f'<rect x="{x}" y="{mid - (6 if i == len(d["tick_positions"]) // 2 else 4)}" width="1" '
        f'height="{12 if i == len(d["tick_positions"]) // 2 else 8}"/>'
        for i, x in enumerate(d["tick_positions"])
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="">
  <defs>
    <linearGradient id="dl" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{c["accent"]}" stop-opacity="0"/>
      <stop offset="12%" stop-color="{c["accent"]}" stop-opacity=".55"/>
      <stop offset="88%" stop-color="{c["accent2"]}" stop-opacity=".55"/>
      <stop offset="100%" stop-color="{c["accent2"]}" stop-opacity="0"/>
    </linearGradient>
    <style>
      @keyframes run {{ 0% {{transform:translateX(60px);opacity:0}} 10% {{opacity:1}}
                        90% {{opacity:1}} 100% {{transform:translateX({W - 60}px);opacity:0}} }}
      .pkt {{ animation: run {d["packet_duration"]}s cubic-bezier(.4,0,.6,1) infinite; }}
    </style>
  </defs>
  <rect x="0" y="{mid - 0.7}" width="{W}" height="1.4" fill="url(#dl)"/>
  <g fill="{c["accent"]}" opacity="0.35">{ticks}</g>
  <g class="pkt">
    <rect x="-22" y="{mid - 1.3}" width="26" height="2.6" rx="1.3" fill="{c["accent"]}" opacity="0.5"/>
    <circle cx="4" cy="{mid - 0.3}" r="2.6" fill="{c["accent"]}"/>
  </g>
</svg>
'''


def main():
    ap = argparse.ArgumentParser(description="README 用 SVG 素材を生成します")
    ap.add_argument("-o", "--out", default="./assets", help="出力先ディレクトリ (default: ./assets)")
    args = ap.parse_args()

    random.seed(CONFIG["seed"])
    os.makedirs(args.out, exist_ok=True)

    files = {
        "hero.svg":     build_hero(CONFIG),
        "pipeline.svg": build_pipeline(CONFIG),
        "divider.svg":  build_divider(CONFIG),
    }
    for name, body in files.items():
        path = os.path.join(args.out, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"  generated  {path}  ({len(body.encode('utf-8')):,} bytes)")


if __name__ == "__main__":
    main()
