# -*- coding: utf-8 -*-
"""汉志经纬 · 全文分片管线
  data_raw/kr/KR2a0007_0{0,8}.txt → data/text/*.js（懒加载）
  juanshou.js  四库提要（000 卷首）
  sy.js        志序（禹贡·职方——昔在黃帝起）
  j1.js/j2.js  郡国各条（上下卷；逐县一行重构，注在括号内，字字皆志文）
  zj.js        郡国总计段（凡郡國一百三…漢極盛矣）
  yf.js        域分风俗十三区（秦地…粵地）
运行：python tools/build_text.py（在 build_data.py 之后）
"""
import importlib.util
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "text")


def load_mod():
    spec = importlib.util.spec_from_file_location(
        "bd", os.path.join(ROOT, "tools", "build_data.py"))
    bd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bd)
    return bd


def paged_clean(seg):
    """页界为段的清洗：pb 标签占位 → 去行尾/换行 → 页界还原为 \n（页面=底本真实结构单元）"""
    s = re.sub(r"<pb:[^>]*>", "\x01", seg)
    s = s.replace("¶", "").replace("\n", "")
    s = s.replace("\x01", "\n")
    s = re.sub(r"\n+", "\n", s).strip("\n")
    return s


def strip_spaces(s):
    return s.replace("\u3000", "")


def entry_text(ent):
    """郡国条可读重构：字字皆志文，仅重排行（郡名行/户口行/县行）"""
    lines = [ent["disp"] + ("（%s）" % ent["_hn"] if ent["_hn"] else "")]
    if ent["_hv"]:
        lines.append(strip_spaces(ent["_hv"]) + "。" + strip_spaces(ent["_xv"]) + "：")
    for cn, note in ent["_c"]:
        nm = re.sub(r"&KR\d{4};", "□", cn)
        note = re.sub(r"/", "", note)
        lines.append(nm + ("（%s）" % note if note else ""))
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    bd = load_mod()
    states, diag, xvxu, zongji, yf, up, xia, entries = bd.parse()

    def w(key, obj):
        with open(os.path.join(OUT, key + ".js"), "w", encoding="utf-8") as f:
            f.write("/* 汉志经纬 · 全文分片（build_text.py 生成 · 懒加载） */\n")
            f.write("window.HZTEXT=window.HZTEXT||{};HZTEXT[%s]=" % json.dumps(key))
            f.write(json.dumps(obj, ensure_ascii=False) + ";\n")

    # 提要（000 卷首：等謹案起）
    t000 = open(os.path.join(ROOT, "data_raw", "kr", "KR2a0007_000.txt"),
                encoding="utf-8").read()
    tc = paged_clean(t000)
    j = tc.find("(臣/)等謹案")
    if j < 0:
        j = tc.find("等謹案")
    tiyao = strip_spaces(tc[j:].replace("/", "")).strip("\n")
    w("juanshou", {"四庫提要": tiyao})

    # 志序 / 总计 / 域分（页面分段；域分按区）
    sy = strip_spaces(paged_clean(xvxu_source(bd)).replace("/", ""))
    w("sy", {"志序": sy})
    zj = strip_spaces(paged_clean(zongji_source(bd)).replace("/", ""))
    w("zj", {"郡國總計": zj})

    yf_p = paged_clean(yf_source(bd))
    i_fs = yf_p.find("凡民函五常之性")
    regions = {}
    REGS = bd.REGIONS
    if i_fs < 0:
        raise SystemExit("域分起点未找到（凡民函五常之性）")
    intro_end = yf_p.find("秦地", i_fs)
    regions["風俗序"] = strip_spaces(
        yf_p[i_fs:intro_end].replace("/", "")).strip("\n")
    for i, r in enumerate(REGS):
        p = yf_p.find(r, intro_end)
        e = yf_p.find(REGS[i + 1], p + 1) if i + 1 < len(REGS) else len(yf_p)
        if p < 0:
            regions[bd.REGION_DISP.get(r, r)] = ""
            continue
        seg = strip_spaces(yf_p[p:e].replace("/", "")).strip("\n")
        body = seg[len(r):].lstrip("，").lstrip("\n")
        regions[bd.REGION_DISP.get(r, r)] = r + "，" + body
    w("yf", regions)

    # 郡国条（上下卷分片）
    j1, j2 = {}, {}
    for ent in entries:
        doc = entry_text(ent)
        (j1 if ent["juan"] == "上" else j2)[ent["disp"]] = doc
    w("j1", j1)
    w("j2", j2)

    n_chars = len(tiyao) + len(sy) + len(zj) + \
        sum(len(v) for v in regions.values()) + \
        sum(len(v) for v in list(j1.values()) + list(j2.values()))
    n_chars_ns = len(re.sub(r"\s", "", tiyao + sy + zj +
                            "".join(regions.values()) +
                            "".join(list(j1.values()) + list(j2.values()))))
    print("分片 6 · 篇 %d（含提要1·志序1·总计1·域分13·郡国103）· %d 字（去空白 %d）"
          % (2 + len(regions) + len(j1) + len(j2), n_chars, n_chars_ns))


def xvxu_source(bd):
    """志序原文（重新自 raw 提取，保留页界）"""
    t = open(os.path.join(bd.ROOT, "data_raw", "kr", "KR2a0007_028.txt"),
             encoding="utf-8").read()
    up = t[:t.find("卷二十八上考證")]
    up = re.sub(r"昔在黃帝", "昔在黃帝", up)
    return up[up.find("昔在黃帝"):]


def zongji_source(bd):
    t = open(os.path.join(bd.ROOT, "data_raw", "kr", "KR2a0007_028.txt"),
             encoding="utf-8").read()
    xia = t[t.find("前漢書卷二十八下"):t.find("卷二十八下考證")]
    i_zj = xia.find("本秦京師為内史")
    i_fs = xia.find("凡民函五常之性")
    return xia[i_zj:i_fs]


def yf_source(bd):
    t = open(os.path.join(bd.ROOT, "data_raw", "kr", "KR2a0007_028.txt"),
             encoding="utf-8").read()
    xia = t[t.find("前漢書卷二十八下"):t.find("卷二十八下考證")]
    xia = re.sub(r"[\u3000\s]*前漢書卷二十八下#\+PROPERTY.*$", "", xia)
    return xia[xia.find("凡民"):][:60000] if xia.find("凡民") >= 0 else xia


if __name__ == "__main__":
    main()
