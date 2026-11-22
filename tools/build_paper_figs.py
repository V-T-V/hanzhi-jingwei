# -*- coding: utf-8 -*-
"""汉志经纬 · 论文插图生成：python tools/build_paper_figs.py

数据源（口径纪律）：docs/stats.json（tools/stats.py 产物）——凡数字出自脚本。
输出：docs/figs/fig1_bu.png · fig2_hukou.png · fig3_badges.png
     （200dpi 麻纸玄墨，学 YHJZ/HHH docs/build_paper_figs.py）
build_paper_pdf.py 于插图缺失时自动调用本脚本（管线可重入）。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "figs")
os.makedirs(OUT, exist_ok=True)

STATS = json.load(open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))

# ── 麻纸玄墨版式（沿站点 CSS 与 PDF 配色） ──
SILK, INK, MUTED = "#efe6cf", "#2b2620", "#897d66"
XUAN, CINNABAR, GOLD, GRIDC = "#37414e", "#842b16", "#a3762b", "#ded4ba"
plt.rcParams.update({
    "font.family": "Microsoft YaHei", "axes.unicode_minus": False,
    "figure.facecolor": SILK, "axes.facecolor": SILK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "text.color": INK,
})
KAI = FontProperties(fname=r"C:\Windows\Fonts\simkai.ttf", size=14)


def frame(ax, axis="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, axis=axis, color=GRIDC, lw=.7, alpha=.8)
    ax.set_axisbelow(True)


# ══ 图 1　十四部域郡国数与县数 ══
per = STATS["per_bu"]                                       # stats.json:per_bu
bus = list(per.keys())
fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=200)
frame(ax)
xs = range(len(bus))
states = [per[b]["states"] for b in bus]
xian = [per[b]["xian"] for b in bus]
ax.bar([x - .19 for x in xs], states, width=.38, color=XUAN, label="郡国数", edgecolor=SILK, lw=.5)
ax.bar([x + .19 for x in xs], xian, width=.38, color=MUTED, label="县数（入表）", edgecolor=SILK, lw=.5)
for x, v in zip(xs, states):
    ax.text(x - .19, v + .8, str(v), ha="center", fontsize=8, color=INK)
for x, v in zip(xs, xian):
    ax.text(x + .19, v + 2.5, str(v), ha="center", fontsize=8, color=INK)
ax.set_xticks(list(xs))
ax.set_xticklabels(bus, fontsize=8.5, rotation=18)
ax.set_ylabel("条目数", fontsize=9.5)
ax.set_ylim(0, max(xian) * 1.18)
ax.legend(fontsize=9, frameon=False, loc="upper right")
ax.set_title("十四部域郡国数与县数（郡国 103 · 县 1,578）", fontproperties=KAI, pad=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1_bu.png"))
plt.close(fig)

# ══ 图 2　元始二年户数前十郡国（与志末总计对读） ══
top = STATS["top_hu"]                                      # stats.json:top_hu
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
frame(ax, axis="x")
names = [d["n"] for d in top][::-1]
hus = [d["hu"] for d in top][::-1]
kous = [d["kou"] for d in top][::-1]
ax.barh(names, kous, color=GRIDC, height=.62, label="口数（右轴对照，不作柱读）", edgecolor=SILK, lw=.5)
ax.barh(names, hus, color=XUAN, height=.62, label="户数", edgecolor=SILK, lw=.5)
for i, v in enumerate(hus):
    ax.text(v + 6000, i, format(v, ","), va="center", fontsize=8.5, color=INK)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9)
ax.set_xlabel("户数（元始二年）", fontsize=9.5)
ax.set_xlim(0, max(kous) * 1.02)
secax = ax.secondary_xaxis("top", functions=(lambda x: x, lambda x: x))
secax.set_xlabel("（上轴同尺：口数灰柱为量级对照——汝南一郡口 259.6 万）", fontsize=8.5, color=MUTED)
secax.tick_params(labelsize=8, colors=MUTED)
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
ax.set_title("元始二年户数前十郡国——帝国总计戸 12,233,062", fontproperties=KAI, pad=26)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2_hukou.png"))
plt.close(fig)

# ══ 图 3　名物注记频次（莽改 · 祠 · 盐铁诸官） ══
bd = STATS["badges"]                                       # stats.json:badges
LAB = [("mang", "莽曰（王莽改地名）"), ("ci", "祠（山川祠庙）"), ("yan", "鹽官"),
       ("tie", "铁官（鐵/鐡并计）"), ("gong", "工官"), ("ju", "橘官"), ("mu", "木官")]
items = [(lab, bd[k]) for k, lab in LAB if bd.get(k)]
fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
frame(ax, axis="x")
names = [k for k, _ in items][::-1]
vals = [v for _, v in items][::-1]
cols = [CINNABAR if n.startswith("莽曰") else (GOLD if "官" in n else XUAN) for n in names]
ax.barh(names, vals, color=cols, height=.62, edgecolor=SILK, lw=.5)
for i, v in enumerate(vals):
    ax.text(v + 8, i, str(v), va="center", fontsize=9, color=INK)
ax.set_xlabel("志文计数（郡县注中实证）", fontsize=9.5)
ax.set_xlim(0, max(vals) * 1.14)
ax.legend(handles=[Patch(fc=CINNABAR, label="莽改（新莽易地名）"),
                   Patch(fc=GOLD, label="诸官（盐铁工橘木）"),
                   Patch(fc=XUAN, label="祠庙")],
          loc="lower right", fontsize=8.5, frameon=False)
ax.set_title("名物注记频次——莽曰 671 · 祠 48 · 鹽官 23 · 铁官 33", fontproperties=KAI, pad=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3_badges.png"))
plt.close(fig)

print("OK →", OUT, sorted(os.listdir(OUT)))
