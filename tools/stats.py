# -*- coding: utf-8 -*-
"""汉志经纬 · 计数产物（凡数字出自脚本 → docs/stats.json）
   前端 README / ANALYSIS / 论文只读本产物。运行：python tools/stats.py"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "stats.json")


def load_js(path):
    raw = open(path, encoding="utf-8").read()
    return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])


def main():
    sd = load_js(os.path.join(ROOT, "data", "site_data.js"))
    xr = load_js(os.path.join(ROOT, "data", "xref_yh.js"))
    fetch = json.load(open(os.path.join(ROOT, "data", "fetch_report.json"), encoding="utf-8"))
    states = [s for b in sd["bu"] for s in b["states"]]

    # 语料字数（去空白，自分片实测）
    chars = 0
    for f in os.listdir(os.path.join(ROOT, "data", "text")):
        if not f.endswith(".js"):
            continue
        t = open(os.path.join(ROOT, "data", "text", f), encoding="utf-8").read()
        d = json.loads(t[t.rfind("=") + 1:].rstrip().rstrip(";"))
        chars += sum(len(re.sub(r"\s", "", v)) for v in d.values())

    n_x = sum(len(s["xian"]) for s in states)
    top_hu = sorted(states, key=lambda s: -(s.get("hu") or 0))[:10]
    top_xian = sorted(states, key=lambda s: -len(s["xian"]))[:10]
    mang_top = sorted(states, key=lambda s: -(s.get("badges", {}).get("mang") or 0))[:5]
    out = {
        "bu": len(sd["bu"]),
        "states": len(states),
        "states_listed_ok": sum(1 for s in states if s.get("ok")),
        "counties_parsed": n_x,
        "counties_stated_sum": sum(s.get("nx") or 0 for s in states),
        "xianyi_expected": 1314 + 32 + 241,
        "coords": sum(1 for s in states if s.get("c")),
        "conf1": sum(1 for s in states if s.get("conf") == 1),
        "conf2": sum(1 for s in states if s.get("conf") == 2),
        "seats": sum(1 for s in states if s.get("seat")),
        "seat_exceptions": sum(1 for s in states if s.get("seat_note")),
        "hu_sum": sum(s.get("hu") or 0 for s in states),
        "kou_sum": sum(s.get("kou") or 0 for s in states),
        "hu_empire": sd["meta"]["totals"]["hu"],
        "kou_empire": sd["meta"]["totals"]["kou"],
        "badges": {k: sum((s.get("badges") or {}).get(k, 0) for s in states)
                   for k in ["tie", "yan", "gong", "ju", "mu", "shui", "ci", "mang"]},
        "regions": len(sd["regions"]),
        "region_chars": sum(r.get("chars") or 0 for r in sd["regions"]),
        "corpus_chars": chars,
        "fetch_chars": fetch.get("total_chars"),
        "yt_max": max(s.get("yt") or 0 for s in states),
        "yt_median": sorted(s.get("yt") or 0 for s in states)[len(states) // 2],
        "top_hu": [{"n": s["n"], "hu": s["hu"], "kou": s["kou"]} for s in top_hu],
        "top_xian": [{"n": s["n"], "xian": len(s["xian"])} for s in top_xian],
        "mang_top": [{"n": s["n"], "mang": s["badges"]["mang"]} for s in mang_top],
        "per_bu": {b["name"]: {"states": len(b["states"]),
                               "xian": sum(len(s["xian"]) for s in b["states"]),
                               "hu": sum(s.get("hu") or 0 for s in b["states"])}
                   for b in sd["bu"]},
        "xref": xr["meta"],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in
                      ["states", "states_listed_ok", "counties_parsed", "coords",
                       "conf1", "conf2", "hu_sum", "kou_empire", "corpus_chars",
                       "badges", "regions"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
