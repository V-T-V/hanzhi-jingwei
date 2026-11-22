# -*- coding: utf-8 -*-
"""《汉志经纬》论文排印：docs/ANALYSIS.md → docs/汉志经纬-数字人文.pdf
   题页摘要数字运行时取自 docs/stats.json 与 data/xref_yh.js（凡数字出自脚本）；
   正文由 ANALYSIS.md（tools/build_analysis.py 生成）逐节解析——md 重产而 PDF 未重排，
   lint 哨兵即红。运行：python tools/build_paper_pdf.py"""
import io
import json
import os
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "汉志经纬-数字人文.pdf")
MD = os.path.join(ROOT, "docs", "ANALYSIS.md")

# 插图缺失时自动重建（管线可重入：docs/stats.json → build_paper_figs.py，学系列先例）
FIGS_DIR = os.path.join(ROOT, "docs", "figs")
NEED_FIGS = ["fig1_bu.png", "fig2_hukou.png", "fig3_badges.png"]
if not all(os.path.isfile(os.path.join(FIGS_DIR, f)) for f in NEED_FIGS):
    subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "build_paper_figs.py")],
                   check=True)

pdfmetrics.registerFont(TTFont("KaiTi", r"C:\Windows\Fonts\STKAITI.TTF"))
pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))

# ━━ 配色（站色系：玄墨 · 朱砂 · 麻纸）━━
ACCENT = colors.HexColor("#37414e")
CINNABAR = colors.HexColor("#842b16")
TEXT_PRIMARY = colors.HexColor("#2b2620")
TEXT_MUTED = colors.HexColor("#897d66")
BG_SURFACE = colors.HexColor("#e7e0cc")
BG_PAGE = colors.HexColor("#efe8d4")

W, H = A4
M = 20 * mm
AW = W - 2 * M

S = {
    "title": ParagraphStyle("t", fontName="KaiTi", fontSize=23, leading=33, alignment=TA_CENTER,
                            textColor=TEXT_PRIMARY, wordWrap="CJK"),
    "sub": ParagraphStyle("s", fontName="KaiTi", fontSize=12.5, leading=19, alignment=TA_CENTER,
                          textColor=TEXT_MUTED, wordWrap="CJK"),
    "h1": ParagraphStyle("h1", fontName="KaiTi", fontSize=15.5, leading=23, textColor=ACCENT,
                         spaceBefore=14, spaceAfter=6, wordWrap="CJK"),
    "body": ParagraphStyle("b", fontName="YaHei", fontSize=10.5, leading=17.5, alignment=TA_JUSTIFY,
                           textColor=TEXT_PRIMARY, spaceAfter=5, wordWrap="CJK", firstLineIndent=21),
    "body0": ParagraphStyle("b0", fontName="YaHei", fontSize=10.5, leading=17.5, alignment=TA_JUSTIFY,
                            textColor=TEXT_PRIMARY, spaceAfter=4, wordWrap="CJK"),
    "abs": ParagraphStyle("a", fontName="YaHei", fontSize=9.8, leading=16.5, alignment=TA_JUSTIFY,
                          textColor=TEXT_PRIMARY, wordWrap="CJK", firstLineIndent=19.6),
    "cap": ParagraphStyle("c", fontName="KaiTi", fontSize=9.5, leading=14, alignment=TA_CENTER,
                          textColor=TEXT_MUTED, spaceBefore=2, spaceAfter=8, wordWrap="CJK"),
    "th": ParagraphStyle("th", fontName="YaHei", fontSize=9.5, leading=13.5, alignment=TA_CENTER,
                         textColor=colors.white, wordWrap="CJK"),
    "td": ParagraphStyle("td", fontName="YaHei", fontSize=9.5, leading=13.5, alignment=TA_CENTER,
                         textColor=TEXT_PRIMARY, wordWrap="CJK"),
    "tdl": ParagraphStyle("tdl", fontName="YaHei", fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY,
                          textColor=TEXT_PRIMARY, wordWrap="CJK"),
}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def P(t, st="body"):
    return Paragraph(esc(t), S[st])


def tbl(headers, rows):
    n = len(headers)
    data = [[Paragraph(esc(h), S["th"]) for h in headers]]
    for r in rows:
        r = list(r) + [""] * (n - len(r))          # 列数宽容（分布列可空）
        data.append([Paragraph(esc(c), S["tdl"] if i == 0 else S["td"]) for i, c in enumerate(r)])
    t = Table(data, colWidths=[AW / n] * n, hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_SURFACE]),
        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#c7bfa8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def footer(cv, doc):
    cv.saveState()
    cv.setFont("KaiTi", 8.5)
    cv.setFillColor(TEXT_MUTED)
    cv.drawCentredString(W / 2, 12 * mm, f"— {doc.page} —")
    cv.setFont("KaiTi", 7.5)
    cv.drawString(M, 12 * mm, "汉志经纬 · 数字人文")
    cv.drawRightString(W - M, 12 * mm, "漢書·地理志（東漢 · 班固）")
    cv.restoreState()


def fig(fname, h_mm, caption):
    img = Image(os.path.join(FIGS_DIR, fname), width=AW, height=h_mm * mm, hAlign="CENTER")
    return KeepTogether([Spacer(1, 2 * mm), img, Paragraph(esc(caption), S["cap"])])


# 节 → 插图（fname, h_mm, 图注）。挂在各节首表之后——图文对应，数字均出自 docs/stats.json
FIGS_AFTER = {
    "一、覆盖": [
        ("fig1_bu.png", 96.0, "图 1　十四部域郡国数与县数——司隶 7 郡国领县 132 为诸部之冠"
                              "（docs/stats.json: per_bu）"),
    ],
    "二、元始二年户口（公元 2 年）": [
        ("fig2_hukou.png", 88.0, "图 2　元始二年户数前十郡国——汝南 461,587 户居首；灰柱为口数量级对照"
                                 "（docs/stats.json: top_hu）"),
    ],
    "三、名物注记（郡县注中实证）": [
        ("fig3_badges.png", 84.0, "图 3　名物注记频次——莽曰 671 · 祠 48 · 鹽官 23 · 铁官 33（鐵/鐡二形并计）"
                                  "（docs/stats.json: badges）"),
    ],
}


def parse_md(md):
    """ANALYSIS.md（build_analysis.py 产物）→ flowables：## 节 → h1；表格 → tbl；- 条 → body0；> 引 → cap
    节内首表后按 FIGS_AFTER 挂插图（图注自 stats.json 键名，凡数字出自脚本）。"""
    out, lines, i = [], md.splitlines(), 0
    section, figs_done = "", set()
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("## "):
            section = ln[3:].strip()
            out.append(P(ln[3:], "h1"))
            i += 1
            continue
        if ln.startswith("# "):
            i += 1
            continue
        if ln.startswith("> "):
            out.append(P(ln[2:].lstrip(), "cap"))
            i += 1
            continue
        if ln.startswith("|"):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-— ") for c in row):
                    block.append(row)
                i += 1
            if block:
                out.append(tbl(block[0], block[1:]))
                out.append(Spacer(1, 2 * mm))
                if section in FIGS_AFTER and section not in figs_done:
                    for fname, h_mm, cap in FIGS_AFTER[section]:
                        out.append(fig(fname, h_mm, cap))
                    figs_done.add(section)
            continue
        if ln.lstrip().startswith("- "):
            out.append(P("· " + ln.lstrip()[2:], "body0"))
            i += 1
            continue
        out.append(P(ln.strip(), "body0"))
        i += 1
    return out


def main():
    stats = json.load(open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))
    xraw = open(os.path.join(ROOT, "data", "xref_yh.js"), encoding="utf-8").read()
    xm = json.loads(xraw[xraw.find("{"): xraw.rfind("}") + 1])["meta"]
    md = open(MD, encoding="utf-8").read()

    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=M, rightMargin=M,
                          topMargin=18 * mm, bottomMargin=20 * mm,
                          title="汉志经纬：《漢書·地理志》数字人文整编", author="汉志经纬项目组",
                          subject="数字人文·汉代政区地理·漢書地理志", creator="汉志经纬")
    frame = Frame(M, 20 * mm, AW, H - 38 * mm, id="f")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=footer)])

    E = [Spacer(1, 10 * mm),
         Paragraph("《漢書·地理志》的数字人文整编", S["title"]),
         Spacer(1, 3 * mm),
         Paragraph("——一百三郡国、元始二年户口与域分风俗的机器可读整编", S["sub"]),
         Spacer(1, 8 * mm),
         Paragraph("汉志经纬项目组", S["sub"]),
         Paragraph("2026 年 11 月 · 全部数字由脚本可复核（tools/stats.py · build_xref_yh.py）", S["sub"]),
         Spacer(1, 5 * mm),
         HRFlowable(width="34%", thickness=.7, color=ACCENT, hAlign="CENTER"),
         Spacer(1, 5 * mm)]

    abstract = (
        "<b>摘　要</b>　本文报告東漢班固《漢書·地理志》（志第八，上下两卷，所记户口为元始二年——"
        "公元 2 年之籍）的数字人文整编。自 kanripo 文淵閣四庫本《前漢書》卷二十八抓取全志，"
        "语料（去空白）%(chars)s 字（志文正文+顔師古注+四库提要，四库馆臣考證两节剥离），解析得"
        "郡国条目 %(states)d、入表县 %(counties)s——逐郡县名录与原书「縣N」对账 %(ok)d/103 全合"
        "（志总自报 1587，差 9 系传世文本分计与总数之歧，如实入档）。郡治今地坐标全覆盖"
        "（置信确 %(c1)d / 推 %(c2)d，src:derived，非考古定位；首县例 2 例外通说并注）。"
        "在此底线上作四项计量：元始二年户口（郡分计 戸 %(hus)s / 口 %(kous)s，志末总计 "
        "戸 %(hu_e)s / 口 %(kou_e)s，分计与总计不合两存并注差数）、名物注记（莽曰 %(mang)d——"
        "新莽易地名之实录、祠 %(ci)d、鹽官 %(yan)d、铁官 %(tie)d（鐵/鐡二形并计）、工官 %(gong)d）、"
        "域分风俗十三区域（%(yf_chars)s 字）、条目文量（中位 %(med)d / 最大 %(ymax)d 字，3D 文柱据）。"
        "又与姊妹站元和经纬（唐元和八年 813《元和郡县图志》）作汉唐郡治↔州治对照：汉 %(han)d 郡国"
        "得唐对应 %(matched)d（同名同城 %(same)d · 承名 %(renamed)d · 迁治 %(qy)d），无对应 "
        "%(unmatched)d 如实分档（含元和志淮南整道佚、卷十九/二十幽州等缺卷归因）。全部数字可由"
        "仓库脚本复现。" % {
            "chars": format(stats["corpus_chars"], ","), "states": stats["states"],
            "counties": format(stats["counties_parsed"], ","), "ok": stats["states_listed_ok"],
            "c1": stats["conf1"], "c2": stats["conf2"],
            "hus": format(stats["hu_sum"], ","), "kous": format(stats["kou_sum"], ","),
            "hu_e": format(stats["hu_empire"], ","), "kou_e": format(stats["kou_empire"], ","),
            "mang": stats["badges"]["mang"], "ci": stats["badges"]["ci"],
            "yan": stats["badges"]["yan"], "tie": stats["badges"]["tie"],
            "gong": stats["badges"]["gong"], "yf_chars": format(stats["region_chars"], ","),
            "med": stats["yt_median"], "ymax": stats["yt_max"],
            "han": xm["han_juns"], "matched": xm["matched"], "same": xm["same_name"],
            "renamed": xm["renamed"], "qy": xm["qianyi"], "unmatched": xm["unmatched"]})
    kw = ("<b>关键词</b>　漢書地理志；西汉政区地理；元始二年户口；数字人文；域分风俗；汉唐对照")
    abs_tbl = Table([[Paragraph(abstract, S["abs"])], [Paragraph(kw, S["abs"])]], colWidths=[AW])
    abs_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_PAGE),
        ("LINEBELOW", (0, 0), (-1, 0), .4, colors.HexColor("#d3cbb5")),
        ("BOX", (0, 0), (-1, -1), .6, colors.HexColor("#c7bfa8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    E += [abs_tbl, Spacer(1, 6 * mm)]

    E += [P("引言", "h1"),
          P("《漢書·地理志》是我国正史地理志之祖，以元始二年簿籍为底账，首尾完具地录下西汉末"
            "一百三郡国、一千五百余县邑道国的名数、户口与山川祠官，末缀「域分风俗」十三区域，"
            "为两汉政区地理之基。本整编将四库本全志解析为「部域—郡国—县」机器可读数据，"
            "坐标依汉代政区地理整编为今地（首县例为郡治，属县但存名录，不作定位臆测），"
            "并坚持两条纪律：凡数字必出自脚本；歧则如实计歧。以下各节计量均由"
            " tools/build_analysis.py 产出的 ANALYSIS.md 逐节排印，交互验证见于配套站点汉志经纬"
            "（舆图 · 循郡而读 · 全书检索 · 域分风俗 · 汉唐对照）。")]
    E += parse_md(md)
    E += [Spacer(1, 4 * mm), HRFlowable(width="100%", thickness=.5, color=BG_SURFACE),
          Paragraph("本文一切数字可由仓库脚本复现；交互验证：站点「舆图」「循郡而读」「漢唐對照」诸页签。", S["cap"])]

    doc.build(E)
    print("OK →", OUT, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
