# -*- coding: utf-8 -*-
"""汉志经纬 × 元和经纬 · 汉唐互查桥（P2）
   读 D:\\W_A_W\\YHJZ\\data\\site_data.js（**YHJZ 只读，绝不写入**），
   汉郡治（元始二年·公元2年 103 郡国）↔ 唐州治（元和八年·813 227 州府）匹配：
     一档 同名同城：名键相合（去 尹/翊/風/郡/國 与 府/州/军/监 尾）且治所 ≤35 km；
     二档 同城承名：治所同城（≤35 km）而今名相合、名异（汉郡→唐州同城异名）；
     三档 同名迁治：名键相合而治所 35–150 km（承名而治徙，注记）；
     人工整编别名（书证明确者注明）；匹配不上如实分档（唐废/改置/边外）。
   产 data/xref_yh.js（前端「汉唐对照」页签）；深链 ../YHJZ/#dao=<id>&zhou=<名>。
   运行：python tools/build_xref_yh.py"""
import io
import json
import math
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YHJZ = os.path.join(os.path.dirname(ROOT), "YHJZ", "data", "site_data.js")

# 繁→简（仅覆盖两站名表所需字）
T2S = {
    "漢": "汉", "馮": "冯", "翊": "翊", "風": "风", "農": "农", "東": "东",
    "黨": "党", "陳": "陈", "潁": "颍", "陽": "阳", "廬": "庐", "濟": "济",
    "陰": "阴", "鉅": "巨", "齊": "齐", "萊": "莱", "琅": "琅", "臨": "临",
    "會": "会", "廣": "广", "漢": "汉", "犍": "犍", "為": "为", "嶲": "嶲",
    "牂": "牂", "隴": "陇", "張": "张", "雲": "云", "鴈": "雁", "漁": "渔",
    "遼": "辽", "菟": "菟", "樂": "乐", "鬱": "郁", "蒼": "苍", "眞": "真",
    "閒": "间", "甾": "甾", "膠": "胶", "壽": "寿", "魯": "鲁", "廢": "废",
    "趙": "赵", "廣": "广", "國": "国", "長": "长", "鹽": "盐", "鐵": "铁",
    "戶": "户", "戸": "户",
}


def norm(s):
    return "".join(T2S.get(ch, ch) for ch in (s or ""))


def base_key(name):
    """名键：剥 左/右 前缀（三辅）与 尹/翊/風/郡/國/府/州/军/监 尾"""
    n = norm(name)
    while n and n[0] in "左右":
        n = n[1:]
    while n and n[-1] in "尹翊風风郡國国府州军监":
        n = n[:-1]
    return n


def dist_km(a, b):
    if not a or not b:
        return None
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def now_align(a, b):
    """治所今名对齐（含县级今名，≥2 字互含）"""
    a, b = norm(a or ""), norm(b or "")
    if len(a) < 2 or len(b) < 2:
        return False
    return a in b or b in a


def load_js(path):
    raw = open(path, encoding="utf-8").read()
    return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])


# 人工整编别名（书证明确；键=汉郡 display 名（繁体），值=(唐州名, 注)）
ALIAS = {
    "汝南郡": ("蔡州", "承名整编：唐蔡州治汝阳县（今汝南），即汉汝南郡故地；平舆故治与汝阳相距约 25 km"),
    "河東郡": ("河中府", "承名整编：唐河中府治河东县（蒲州），汉河东郡名存于唐县；郡治安邑与蒲州治相距约 100 km，治徙并注"),
    "趙國": ("磁州", "唐磁州治滏阳（今磁县），领邯郸县——赵国故治为唐磁州属县"),
    "南陽郡": ("邓州", "唐邓州领南阳县，即汉宛故治；州治穰县与宛相距约 49 km"),
    "巴郡": ("渝州", "渝州治巴县，即汉江州故地；桥计距 45 km 系两侧今地取点之差"),
}

# 无对应专因（元和志缺卷所致者，注明卷次——据 YHJZ 缺卷记）
WHY_OVERRIDE = {
    "九江郡": "唐寿州（同城）在元和志淮南道整道佚卷，桥无所出",
    "廬江郡": "唐庐州（同域）在元和志淮南道整道佚卷，桥无所出",
    "六安國": "唐舒州（同域）在元和志淮南道整道佚卷，桥无所出",
    "廣陵國": "唐扬州（同城）在元和志淮南道整道佚卷，桥无所出",
    "南郡": "唐荆州（同城江陵）条在元和志卷二十三佚，桥无所出",
    "漢中郡": "唐金州（同今地）条在元和志卷二十三佚，桥无所出",
    "廣陽國": "唐幽州（同城蓟城）条在元和志河北道缺卷（卷十九/二十），桥无所出",
    "涿郡": "唐幽州（近畿）条在元和志河北道缺卷（卷十九/二十），桥无所出",
    "丹陽郡": "唐宣州（同城宛陵）条在元和志江南道缺卷（卷二十五/二十六），桥无所出",
}

# 承名词族（汉郡名→唐州名键的谱系承递，如 犍为→嘉州? 不入——只收书证坚确者）
NAME_KIN = {
    "京兆": ["京兆"],
    "南郡": ["荆州"],          # 唐荆州治安陆? 非——YHJZ 若无荆州则不命中
}


def main():
    hz = load_js(os.path.join(ROOT, "data", "site_data.js"))
    yh = load_js(YHJZ)  # 只读

    han = []
    for b in hz["bu"]:
        for s in b["states"]:
            han.append({"n": s["n"], "bu": b["name"], "bu_id": b["id"],
                        "now": (s.get("now") or "").split("（")[0], "c": s.get("c")})
    tang = []
    for d in yh["daos"]:
        for s in d["states"]:
            tang.append({"n": s["n"], "dao": d["name"], "id": d["id"],
                         "now": (s.get("now") or "").split("（")[0].replace("陕西", "").replace("山西", "")
                                 .replace("河南", "").replace("河北", "").replace("山东", "")
                                 .replace("江苏", "").replace("浙江", "").replace("安徽", "")
                                 .replace("湖北", "").replace("湖南", "").replace("江西", "")
                                 .replace("四川", "").replace("重庆", "").replace("贵州", "")
                                 .replace("云南", "").replace("广西", "").replace("广东", "")
                                 .replace("甘肃", "").replace("青海", "").replace("宁夏", "")
                                 .replace("内蒙古", "").replace("陕西", ""),
                         "c": s.get("c")})
    for t in tang:
        t["key"] = base_key(t["n"])
        t["used"] = False

    rows = []
    # ── 档序：同名同城 → 人工别名 → 同城承名 → 同名迁治（≤100 km，注记）──
    for h in han:
        hk = base_key(h["n"])
        row = {"n": h["n"], "bu": h["bu"], "now": h["now"], "m": None}
        # 一档：同名同城（名键相合 + ≤35 km）
        keys = [hk] + NAME_KIN.get(hk, [])
        cands = [t for t in tang if t["key"] in keys and not t["used"]]
        best, best_d = None, None
        for t in cands:
            dkm = dist_km(h["c"], t["c"])
            if dkm is not None and dkm <= 35:
                if best is None or dkm < best_d:
                    best, best_d = t, dkm
        if best:
            best["used"] = True
            row["m"] = {"n": best["n"], "dao": best["dao"], "id": best["id"],
                        "now": best["now"], "kind": "同名同城"}
            row["m"]["tongcheng"] = True
            row["m"]["qianyi"] = False
            rows.append(row)
            continue
        # 二档：人工整编别名（书证明确）
        if h["n"] in ALIAS:
            tn, note = ALIAS[h["n"]]
            t = next((x for x in tang if not x["used"] and x["n"] == tn), None)
            if t:
                t["used"] = True
                row["m"] = {"n": t["n"], "dao": t["dao"], "id": t["id"],
                            "now": t["now"], "kind": "承名同地"}
                row["m"]["tongcheng"] = False
                row["m"]["qianyi"] = False
                row["m"]["note"] = note
                rows.append(row)
                continue
        # 三档：同城承名（治所 ≤35 km，今名相合优先）
        near = []
        for t in tang:
            if t["used"]:
                continue
            dkm = dist_km(h["c"], t["c"])
            if dkm is not None and dkm <= 35:
                near.append((0 if now_align(h["now"], t["now"]) else 1, dkm, t))
        if near:
            near.sort(key=lambda x: (x[0], x[1]))
            _, dkm, t = near[0]
            t["used"] = True
            row["m"] = {"n": t["n"], "dao": t["dao"], "id": t["id"],
                        "now": t["now"], "kind": "同城承名"}
            row["m"]["tongcheng"] = True
            row["m"]["qianyi"] = False
            row["m"]["note"] = "治所同今地（相距 %d km）而名承" % round(dkm)
            rows.append(row)
            continue
        # 四档：同名迁治（名键相合 + 35–100 km，注记；同名异地 >100 km 不入）
        best, best_d = None, None
        for t in cands:
            dkm = dist_km(h["c"], t["c"])
            if dkm is not None and 35 < dkm <= 100:
                if best is None or dkm < best_d:
                    best, best_d = t, dkm
        if best:
            best["used"] = True
            row["m"] = {"n": best["n"], "dao": best["dao"], "id": best["id"],
                        "now": best["now"], "kind": "同名迁治"}
            row["m"]["tongcheng"] = False
            row["m"]["qianyi"] = True
            row["m"]["note"] = "承名而治所相距 %d km——八百年间治徙" % round(best_d)
        rows.append(row)

    # ── 无对应归因 ──
    for h, row in zip(han, rows):
        if row["m"]:
            continue
        if h["n"] in WHY_OVERRIDE:
            row["why"] = WHY_OVERRIDE[h["n"]]
            continue
        n = norm(h["n"])
        if any(k in n for k in ("玄菟", "乐浪", "交趾", "九真", "日南", "合浦", "郁林", "苍梧")):
            row["why"] = "边郡（汉境之外/后废），唐志无同城州治"
        elif h["n"] in ("朔方郡", "五原郡", "云中郡", "定襄郡", "西河郡", "上郡", "北地郡"):
            row["why"] = "北边郡（汉后屡废屡徙），唐州治不同城"
        else:
            row["why"] = "唐志未见同城州治（郡废/改置/治徙，如实计）"

    # ── 样例（汉志原文句 × 元和原文句）──
    prefer = ["京兆尹", "河南郡", "太原郡", "弘農郡", "南陽郡", "九江郡",
              "蜀郡", "安定郡", "武威郡", "南海郡"]
    hz_text_hint = {}
    for b in hz["bu"]:
        for s in b["states"]:
            hz_text_hint[s["n"]] = (s.get("hukou_v") or "") + "○縣" + str(s.get("nx") or "")
    yh_yan = {}
    for d in yh["daos"]:
        for s in d["states"]:
            yh_yan[s["n"]] = (s.get("yan") or "").strip()
    samples = []
    for name in prefer:
        row = next((r for r in rows if r["n"] == name and r["m"]), None)
        if not row:
            continue
        hq = hz_text_hint.get(name, "")
        tq = yh_yan.get(row["m"]["n"], "")
        samples.append({
            "hn": name, "hq": (hq[:56] + "……") if len(hq) > 56 else hq,
            "tn": row["m"]["n"], "tq": (tq[:56] + "……") if len(tq) > 56 else tq,
            "tid": row["m"]["id"], "kind": row["m"]["kind"],
            "tongcheng": bool(row["m"].get("tongcheng")),
            "qianyi": bool(row["m"].get("qianyi")),
        })
        if len(samples) >= 8:
            break

    # ── 计数（凡计数出自脚本）──
    matched = [r for r in rows if r["m"]]
    by_bu = []
    for b in hz["bu"]:
        rs = [r for r in rows if r["bu"] == b["name"]]
        by_bu.append({
            "bu": b["name"], "id": b["id"],
            "total": len(rs), "matched": sum(1 for r in rs if r["m"]),
            "qianyi": sum(1 for r in rs if r["m"] and r["m"].get("qianyi")),
        })
    meta = {
        "han_juns": len(rows),
        "tang_states": len(tang),
        "matched": len(matched),
        "same_name": sum(1 for r in matched if r["m"]["kind"] == "同名同城"),
        "renamed": sum(1 for r in matched if r["m"]["kind"] in ("同城承名", "承名同地")),
        "tongcheng": sum(1 for r in matched if r["m"].get("tongcheng")),
        "qianyi": sum(1 for r in matched if r["m"].get("qianyi")),
        "unmatched": sum(1 for r in rows if not r["m"]),
        "tang_new": sum(1 for t in tang if not t["used"]),
        "source": "YHJZ/data/site_data.js（只读 · 元和郡县图志 识典古籍四库本）",
    }
    out = {"meta": meta, "byBu": by_bu, "rows": rows, "samples": samples}
    with open(os.path.join(ROOT, "data", "xref_yh.js"), "w", encoding="utf-8") as f:
        f.write("/* 汉志经纬 · 元和互查桥（build_xref_yh.py 生成，勿手改；YHJZ 只读） */\n")
        f.write("var HZXREF = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("汉唐对照桥：汉 %d 郡国 ↔ 唐 %d 州府：同名同城 %d · 承名 %d｜迁治 %d · 无对应 %d｜唐侧无汉对应 %d"
          % (meta["han_juns"], meta["tang_states"], meta["same_name"], meta["renamed"],
             meta["qianyi"], meta["unmatched"], meta["tang_new"]))
    print("样例：", "、".join(s["hn"] + "↔" + s["tn"] for s in samples))


if __name__ == "__main__":
    main()
