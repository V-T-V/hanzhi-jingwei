# -*- coding: utf-8 -*-
"""汉志经纬 · 古今对照导出（P2）：103 郡国 + 1,578 县名录 → CSV（带 BOM）/ KML / GeoJSON
   字段与前端「⤓ 导出」按钮同口径（js/panels.js exportRows）——两处数字互证。
   坐标为整编今地（src:derived，非考古定位），置信分确/推，导出中逐行注明。
   运行：python tools/export_data.py → docs/export/"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "export")
os.makedirs(OUT, exist_ok=True)

raw = open(os.path.join(ROOT, "data", "site_data.js"), encoding="utf-8").read()
hz = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])

BOM = "\ufeff"


def main():
    # ── 郡国表（103 行）──
    jun_rows = [["部域", "郡国", "卷", "戸（元始二年）", "口", "縣数（原文载）", "入表县数",
                 "首县", "治所今地（依据）", "纬度", "经度", "src", "置信", "坐标注记"]]
    feats, pins = [], []
    for b in hz["bu"]:
        for u in b["states"]:
            conf = "推" if u.get("conf") == 2 else "确"
            note = "整编今地坐标（非考古定位）"
            if u.get("seat_note"):
                note += "；" + u["seat_note"]
            jun_rows.append([
                b["name"], u["n"], u.get("juan") or "",
                u.get("hu") or "", u.get("kou") or "",
                u.get("nx") or "", len(u.get("xian") or []),
                u.get("seat") or "", u.get("now") or "",
                (u.get("c") or ["", ""])[0], (u.get("c") or ["", ""])[1],
                u.get("src") or "derived", conf, note,
            ])
            if u.get("c"):
                feats.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [u["c"][1], u["c"][0]]},
                    "properties": {"名": u["n"], "部域": b["name"], "卷": u.get("juan") or "",
                                   "戸": u.get("hu") or 0, "口": u.get("kou") or 0,
                                   "縣": u.get("nx") or 0, "首县": u.get("seat") or "",
                                   "今地": u.get("now") or "", "src": u.get("src") or "derived",
                                   "置信": conf, "坐标注记": note},
                })
                pins.append(
                    "<Placemark><name>%s</name><description>%s · 卷%s · 戸%s 口%s 縣%s 今%s"
                    "（src:derived 置信%s）</description>"
                    "<Point><coordinates>%s,%s,0</coordinates></Point></Placemark>"
                    % (u["n"], b["name"], u.get("juan") or "", u.get("hu") or "",
                       u.get("kou") or "", u.get("nx") or "",
                       (u.get("now") or ""), conf, u["c"][1], u["c"][0]))

    # ── 县表（1,578 行：首县与郡同治，余县但存名录） ──
    xian_rows = [["部域", "郡国", "县", "首县/属县", "附注"]]
    for b in hz["bu"]:
        for u in b["states"]:
            for i, x in enumerate(u.get("xian") or []):
                xian_rows.append([
                    b["name"], u["n"], x,
                    "首县" if i == 0 else "属县",
                    ("与郡治同治（%s）" % (u.get("now") or "").split("（")[0]) if i == 0
                    else "名录存真，治所未定位",
                ])

    # ── 落盘 ──
    def w(name, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("  ✓", name)

    w("汉志经纬-郡国对照.csv", BOM + "\n".join(",".join(str(c) for c in r) for r in jun_rows) + "\n")
    w("汉志经纬-县名录.csv", BOM + "\n".join(",".join(str(c) for c in r) for r in xian_rows) + "\n")
    w("汉志经纬-郡治点位.kml",
      '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
      "<name>汉志经纬·郡治点位（整编今地坐标）</name>" + "".join(pins) + "</Document></kml>\n")
    w("汉志经纬-郡治点位.geojson", json.dumps({"type": "FeatureCollection", "features": feats},
                                              ensure_ascii=False, indent=1) + "\n")
    print("导出完成：郡国 %d 行（表头外 %d 数据行）· 县 %d 行（表头外 %d）· KML/GeoJSON 点位 %d"
          % (len(jun_rows), len(jun_rows) - 1, len(xian_rows), len(xian_rows) - 1, len(feats)))


if __name__ == "__main__":
    main()
