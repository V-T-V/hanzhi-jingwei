# -*- coding: utf-8 -*-
"""汉志经纬 Lint——确定性检查（继承系列禁止清单）
   python tools/lint.py  →  0 = 全过 / 1 = 有违规"""
import glob
import io
import json
import os
import re
import subprocess
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def check(ok, msg):
    if ok:
        print(f"  ✓ {msg}")
    else:
        fails.append(msg)
        print(f"  ✗ {msg}")


print("═══ 汉志经纬 Lint · 禁止清单→确定性 ═══")

# ── 1. 版本一致性（?v= 全站同号，glob 不用手列清单）──
print("── 1. 版本一致性")
idx = open("index.html", encoding="utf-8").read()
sw = open("sw.js", encoding="utf-8").read()
m = re.search(r"\?v=(\w+)", idx)
idx_v = m.group(1) if m else "?"
m2 = re.search(r'VERSION = "v(\w+)"', sw)
sw_v = m2.group(1) if m2 else "?"
check(idx_v == sw_v, f"index ?v={idx_v} == sw VERSION v{sw_v}")
all_v = set(re.findall(r"\?v=(\w+)", idx))
check(len(all_v) <= 1, f"index.html 版本唯一（实得 {all_v}）")
for f in ["tests/*.html", "3d.html"]:
    for g in glob.glob(f):
        c = open(g, encoding="utf-8").read()
        bad = set(re.findall(r"\?v=(\w+)", c)) - {idx_v}
        check(not bad, f"{g} 版本对齐（杂散 {bad if bad else '无'}）")

# ── 2. 目录结构 ──
print("── 2. 目录结构")
check(not glob.glob("test_*.html"), "根目录无残留测试页")
for d in ["js", "css", "data", "tools", "tests", "vendor", "data/text", "docs", "icons"]:
    check(os.path.isdir(d), f"{d}/ 目录存在")
check(os.path.exists("js/ftworker.js"), "Worker 在 js/")

# ── 3. 数据完整性 ──
print("── 3. 数据完整性")
raw = open("data/site_data.js", encoding="utf-8").read()
sd = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
states = [s for b in sd["bu"] for s in b["states"]]
n_jun = len(states)
n_ok = sum(1 for s in states if s.get("ok"))
n_coord = sum(1 for s in states if s.get("c"))
n_xian = sum(len(s.get("xian") or []) for s in states)
n_stated = sum(s.get("nx") or 0 for s in states)
check(len(sd["bu"]) == 14, f"十四部域齐全（实得 {len(sd['bu'])}）")
check(n_jun == 103, f"郡国条目 =103（实得 {n_jun}）")
check(n_ok == 103, f"县名录对账全合 103（实得 {n_ok}）——不合者须修名录或如实标 raw")
check(n_xian == n_stated, f"入表县 == 原文载（{n_xian}=={n_stated}）")
check(n_coord == n_jun, f"郡治坐标全覆盖（{n_coord}/{n_jun}）")
check(all(s.get("hu") and s.get("kou") and s.get("nx") for s in states),
      "郡皆有户口县数（元始二年之籍）")
check("郡國一百三" in json.dumps(sd["meta"], ensure_ascii=False) or
      sd["meta"]["totals"]["jun"] == 103, "meta 含志总郡国数")
check(len(sd["regions"]) == 13, f"域分十三区域（实得 {len(sd['regions'])}）")
stats = json.load(open("docs/stats.json", encoding="utf-8"))
check(stats["states"] == n_jun and stats["counties_parsed"] == n_xian,
      f"stats.json 与 site_data 同源（{stats['states']}=={n_jun}，{stats['counties_parsed']}=={n_xian}）")
badges_sum = sum((s.get("badges") or {}).get("mang", 0) for s in states)
check(badges_sum == stats["badges"]["mang"], f"莽改注计数同源（{badges_sum}）")

# ── 4. 坐标域（汉境）──
print("── 4. 坐标域")
bad_coord = [s["n"] for s in states
             if s.get("c") and not (15 < s["c"][0] < 44 and 88 < s["c"][1] < 137)]
check(not bad_coord, f"坐标皆在汉域内（违 {bad_coord[:5] if bad_coord else '无'}）")

# ── 5. 全文分片 ──
print("── 5. 全文分片")
shards = glob.glob("data/text/*.js")
check(len(shards) == 6, f"全文分片 =6（实得 {len(shards)}）")
frag = open(shards[0], encoding="utf-8").read()
check("HZTEXT" in frag, "分片写入 HZTEXT 全局")
# 分片键与 site_data 郡名对齐
import json as _j
j1 = open("data/text/j1.js", encoding="utf-8").read()
j2 = open("data/text/j2.js", encoding="utf-8").read()
d1 = _j.loads(j1[j1.rfind("=") + 1:].rstrip().rstrip(";"))
d2 = _j.loads(j2[j2.rfind("=") + 1:].rstrip().rstrip(";"))
names_shard = set(d1) | set(d2)
names_data = {s["n"] for s in states}
check(names_shard == names_data, f"分片郡名与数据全合（差 {sorted(names_data ^ names_shard)[:4] if names_data != names_shard else '无'}）")

# ── 6. 闭包安全 ──
print("── 6. 闭包安全")
wlet = []
for f in glob.glob("js/*.js"):
    c = open(f, encoding="utf-8").read()
    wlet += [f"{f}:{mm}" for mm in re.findall(r"window\.(_\w+)\s*=[^=]", c)]
check(not wlet, f"无 window._闭包量赋值（违 {wlet[:3] if wlet else '无'}）")

# ── 7. SW 缓存清单 ──
print("── 7. SW 覆盖")
shell_files = re.findall(r'"(\./[^"]+)"', sw)
check(len(shell_files) >= 18, f"SW SHELL ≥18 文件（实得 {len(shell_files)}）")

# ── 8. JS 语法 ──
print("── 8. JS 语法")
bad_js = []
for f in sorted(glob.glob("js/*.js")):
    r2 = subprocess.run(["node", "--check", f], capture_output=True, timeout=20)
    if r2.returncode:
        bad_js.append(f)
check(not bad_js, f"js/*.js 语法（坏 {bad_js}）")

# ── 9. 危险 API 禁用 ──
print("── 9. 危险 API")
DANGEROUS = [
    (r'map\.fire\("click"', "map.fire 委托分发不可靠"),
    (r'innerHTML\.indexOf\("mode=', "innerHTML.indexOf 验证（& 序列化）"),
    (r'git mv -q', "git mv -q 不存在"),
]
for pat, msg in DANGEROUS:
    hits = []
    for f in glob.glob("js/*.js") + glob.glob("tests/*.html") + glob.glob("tools/*.py"):
        if "lint.py" in f:
            continue
        c = open(f, encoding="utf-8").read()
        if re.search(pat, c):
            hits.append(f)
    check(not hits, f"API 禁用：{msg}（违 {hits[:3] if hits else '无'}）")

# ── 10. Worker 无 DOM / 架构约束 ──
print("── 10. 架构约束")
w = open("js/ftworker.js", encoding="utf-8").read()
dom_refs = re.findall(r"(?:document|window)\.", w)
check(len(dom_refs) == 0, f"Worker 不引用 DOM（实得 {len(dom_refs)} 处）")

# 脚本 defer 顺序
scripts = re.findall(r'<script src="js/(\w+)\.js', idx)
expected_order = ["config", "map", "panels", "rail", "search", "reader",
                  "ft_core", "fulltext", "app", "modes"]
actual_order = [s for s in scripts if s in expected_order]
check(actual_order == expected_order[:len(actual_order)],
      f"脚本 defer 顺序符合依赖链（{actual_order}）")

# ── 11. 吞错禁用 ──
print("── 11. 吞错禁用")
PY_OT = re.compile(r"\bor\s+True\b")
SW1 = "||" + " true"
SW2 = "||" + " exit 0"
py_swallow = []
for f in sorted(glob.glob("tools/*.py")) + ["run_tests.py"]:
    if not os.path.exists(f):
        continue
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        code = line.split("#")[0]
        if PY_OT.search(code) or SW1 in code or SW2 in code:
            py_swallow.append(f"{f}:{i}")
check(not py_swallow, f"py 工具无恒真吞错兜底（违 {py_swallow[:3] if py_swallow else '无'}）")

# ── 12. subprocess 显式编码 ──
print("── 12. subprocess 编码")
bare_sub = []
for f in ["run_tests.py"] + sorted(glob.glob("tools/*.py")):
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        if "text=True" in line and "encoding" not in line:
            bare_sub.append(f"{f}:{i}")
check(not bare_sub, f"text=True 同行须显式 encoding（违 {bare_sub}）")

# ── 13. Python 工具可编译 ──
print("── 13. 工具编译")
import py_compile
import tempfile as _tf
broken_py = []
for f in sorted(glob.glob("tools/*.py")) + ["run_tests.py"]:
    try:
        py_compile.compile(f, doraise=True,
                           cfile=os.path.join(_tf.gettempdir(), "hs_lint.pyc"))
    except Exception as e:
        broken_py.append(f"{f}: {str(e)[:60]}")
check(not broken_py, f"工具脚本可编译（实得 {broken_py}）")

# ── 14. 互查桥数据完整性（YHJZ 只读产物） ──
print("── 14. 互查桥")
xref_path = "data/xref_yh.js"
check(os.path.exists(xref_path), "data/xref_yh.js 存在（python tools/build_xref_yh.py）")
if os.path.exists(xref_path):
    xraw = open(xref_path, encoding="utf-8").read()
    xref = json.loads(xraw[xraw.find("{"): xraw.rfind("}") + 1])
    xm = xref["meta"]
    n_rows = len(xref["rows"])
    check(xm["han_juns"] == n_jun and n_rows == n_jun,
          f"桥行数 == 郡国数（{n_rows}=={n_jun}）")
    n_m = sum(1 for r in xref["rows"] if r["m"])
    check(xm["matched"] == n_m and xm["matched"] + xm["unmatched"] == n_rows,
          f"桥计数自洽（得对应 {xm['matched']} + 无对应 {xm['unmatched']} == {n_rows}）")
    yh_write = [ln for ln in open("tools/build_xref_yh.py", encoding="utf-8").read().splitlines()
                if 'YHJZ' in ln and ('"w"' in ln or "'w'" in ln or '"a"' in ln or "'a'" in ln)]
    check(not yh_write, f"build_xref_yh.py 不写 YHJZ（违 {yh_write[:1] if yh_write else '无'}）")
    # 深链格式
    check("../YHJZ/#dao=" in open("js/panels.js", encoding="utf-8").read(),
          "汉唐页签深链用相对兄弟路径 ../YHJZ/")

# ── 15. 提要/语料溯源 ──
print("── 15. 语料溯源")
fetch = json.load(open("data/fetch_report.json", encoding="utf-8"))
check(fetch["files"][0]["res"] in ("skip", "fetched") and fetch["total_chars"] > 70000,
      f"抓取盘点在位（{fetch['total_chars']} 字）")
check("kanripo" in sd["meta"]["source"], "meta 记 kanripo 源")

print()
if fails:
    for f_ in fails:
        print(f"✗ {f_}")
    print(f"Lint：{len(fails)} 项违规")
    sys.exit(1)
print("Lint：全过 ✓")
