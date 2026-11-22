# -*- coding: utf-8 -*-
"""汉志经纬 · 计量分析页生成器：docs/stats.json → docs/ANALYSIS.md
   数字全部出自脚本产物（stats.json 由 tools/stats.py 产），改动分析须重跑本脚本。
   运行：python tools/build_analysis.py"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))


def fm(n):
    return f"{n:,}"


def bars(pairs, unit=""):
    mx = max(v for _, v in pairs) or 1
    out = ["| 名 | 数 | 分布 |", "|---|---|---|"]
    for k, v in pairs:
        w = int(round(v / mx * 26))
        out.append(f"| {k} | `{unit}{fm(v)}` | {'█' * w}{' ' if w else ''}|")
    return "\n".join(out)


MD = f"""# 汉志经纬 · 计量分析

> 《漢書·地理志》（上下两卷，文渊阁四库本）数字人文计量——凡数字出自脚本
> （`tools/stats.py` → `docs/stats.json`；汉唐对照出自 `tools/build_xref_yh.py`）。
> 本页由 `tools/build_analysis.py` 生成，改分析须重跑。

## 一、覆盖

| 维度 | 数 |
|---|---|
| 郡国条目 | **{S['states']}**（上卷 52 · 下卷 51；志总自报 103，合） |
| 县邑道国入表 | **{fm(S['counties_parsed'])}**（与各郡「縣N」分计全合；志总自报 1587，差 9 系传世文本分计与总数之歧，如实入档） |
| 名录对账全合郡国 | {S['states_listed_ok']}/103 |
| 郡治坐标（src:derived） | {S['coords']}/103（置信确 {S['conf1']} / 推 {S['conf2']}） |
| 首县（郡治例） | {S['seats']}，例外 2（梁國治睢阳、日南郡治西卷，通说并注） |
| 语料字数（去空白） | **{fm(S['corpus_chars'])}**（志文正文+顔師古注+四库提要） |
| 域分风俗区域 | {S['regions']} 区（{fm(S['region_chars'])} 字） |

## 二、元始二年户口（公元 2 年）

- 帝国总计（志末自报）：**戸 {fm(S['hu_empire'])} · 口 {fm(S['kou_empire'])}**
- 郡国分计合计：戸 {fm(S['hu_sum'])} · 口 {fm(S['kou_sum'])}
- 分计与总计之差：戸 {fm(S['hu_sum'] - S['hu_empire'])}（分计多）· 口 {fm(S['kou_sum'] - S['kou_empire'])}（分计少）
  ——传世志文户口分计与总计数不合，旧籍实情，两存之。

### 户数前十郡国

| 郡国 | 户 |
|---|---|
{bars([(d['n'], d['hu']) for d in S['top_hu']])}

### 属县最多十郡国

| 郡国 | 县数 |
|---|---|
{bars([(d['n'], d['xian']) for d in S['top_xian']])}

## 三、名物注记（郡县注中实证）

| 注记 | 志文计数 |
|---|---|
| 莽曰（王莽改地名） | **{S['badges']['mang']}** |
| 祠（山川祠庙） | {S['badges']['ci']} |
| 鹽官 | {S['badges']['yan']} |
| 铁官（鐵/鐡二形并计） | {S['badges']['tie']} |
| 工官 | {S['badges']['gong']} |
| 橘官 | {S['badges']['ju']} |
| 木官 | {S['badges']['mu']} |

莽改县注最多的郡国：{ "、".join(f"{d['n']}×{d['mang']}" for d in S['mang_top']) }。

## 四、部域分组（西汉末监察部域整编示意）

| 部域 | 郡国 | 县 | 户（分计） |
|---|---|---|---|
{chr(10).join(f"| {k} | {v['states']} | {v['xian']} | {fm(v['hu'])} |" for k, v in S['per_bu'].items())}

## 五、条目文量（3D 文柱据）

- 郡国条目文量（正文+注）：中位 {S['yt_median']} 字 · 最大 {S['yt_max']} 字（琅邪郡，五十一县）
- 文柱阈值 500 字（`js/map3d.js` YT_MIN），不满阈值不立柱——志文简省之实，不以矮柱充数

## 六、汉唐对照（× 元和经纬，P2 桥）

- 汉 {S['xref']['han_juns']} 郡国 ↔ 唐 {S['xref']['tang_states']} 州府（元和八年 813）：
  同名同城 {S['xref']['same_name']} · 承名 {S['xref']['renamed']}（同城承名+承名整编）·
  同名迁治 {S['xref']['qianyi']} · **无对应 {S['xref']['unmatched']}**（含元和志缺卷归因：淮南整道佚之寿/庐/扬、卷十九/二十之幽州、卷二十三之荆/金州、卷二十五/二十六之宣州）
- 唐侧无汉郡对应（新置/羁縻等）：{S['xref']['tang_new']}

## 七、口径声明

- 语料为志文正文+双行夹注（顔師古注等），括号原样保留；四库馆臣「考證」剥离未计
- 底本避讳改字从原书（玄→元，志作「元菟」；弘作𢎞），站内正名归一（玄菟/雁門/真定/河間/城陽）
- kanripo 生僻字实体（&KR####;）站内显示为 □，原文档保留实体
- 坐标为今地整编（非考古定位）；部域分组非考证边界
"""


def main():
    path = os.path.join(ROOT, "docs", "ANALYSIS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(MD)
    print("docs/ANALYSIS.md 重写（%d 字）" % len(MD))


if __name__ == "__main__":
    main()
