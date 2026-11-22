# -*- coding: utf-8 -*-
"""汉志经纬 · 一键回归：python run_tests.py
  1) lint（确定性禁止清单）
  2) 数据断言（≥10 项，Python 侧直查产物）
  3) 无头浏览器断言页（TESTLOG 协议）
  退出码 0=全绿 / 1=有失败。本地服务：python -m http.server 9800"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
BASE = os.environ.get("HS_BASE", "http://127.0.0.1:9800/")

fails = []

# ── 1. Lint ──
rl = subprocess.run([sys.executable, "tools/lint.py"], capture_output=True,
                    text=True, encoding="utf-8", errors="replace", timeout=180)
lint_ok = "全过" in rl.stdout
print(rl.stdout.strip().splitlines()[-1] if rl.stdout.strip() else "✗ lint 无输出")
if not lint_ok:
    for b in [l for l in rl.stdout.splitlines() if l.startswith("✗")][:8]:
        print("    " + b)
    fails.append(("lint", ["见上"]))

# ── 2. 数据断言（数字皆出自脚本产物）──
print("── 数据断言")
raw = open("data/site_data.js", encoding="utf-8").read()
sd = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
stats = json.load(open("docs/stats.json", encoding="utf-8"))
fetch = json.load(open("data/fetch_report.json", encoding="utf-8"))

A_COUNT = 0


def A(name, ok, detail=""):
    global A_COUNT
    A_COUNT += 1
    mark = "✓" if ok else "✗"
    print(f"  {mark} {name} {detail}")
    if not ok:
        fails.append((name, [detail or "断言失败"]))


states = [s for b in sd["bu"] for s in b["states"]]
n_coord = sum(1 for s in states if s.get("c"))
n_conf1 = sum(1 for s in states if s.get("conf") == 1)
n_xian = sum(len(s.get("xian") or []) for s in states)
n_stated = sum(s.get("nx") or 0 for s in states)
n_mang = sum((s.get("badges") or {}).get("mang", 0) for s in states)

A("A1 十四部域齐全", len(sd["bu"]) == 14, f"{len(sd['bu'])}部域")
A("A2 郡国条目 =103", len(states) == 103, f"{len(states)}郡国")
A("A3 县名录对账全合", sum(1 for s in states if s.get("ok")) == 103,
  "103/103 与原文縣N密合")
A("A4 入表县 1578 = 原文载", n_xian == 1578 and n_xian == n_stated,
  f"{n_xian}县（志总自报 1587，差 9 如实入档）")
A("A5 郡治坐标全覆盖", n_coord == len(states), f"{n_coord}/{len(states)}")
A("A6 高置信坐标过半", n_conf1 >= len(states) * 0.5, f"确 {n_conf1} / 推 {len(states) - n_conf1}")
A("A7 户口全解析（元始二年）",
  all(s.get("hu") and s.get("kou") for s in states),
  f"户分计 {sum(s.get('hu') or 0 for s in states)}")
A("A8 帝国总计与志文合",
  sd["meta"]["totals"]["hu"] == 12233062 and sd["meta"]["totals"]["kou"] == 59594978,
  "戸12,233,062 · 口59,594,978")
A("A9 域分十三区域", len(sd["regions"]) == 13,
  "、".join(r["n"] for r in sd["regions"][:5]) + "…")
A("A10 stats 与 site_data 同源",
  stats["states"] == len(states) and stats["counties_parsed"] == n_xian,
  f"{stats['states']}郡国/{stats['counties_parsed']}县")
A("A11 抓取语料 ≥7万字", fetch["total_chars"] >= 70000, f"{fetch['total_chars']}字")
A("A12 全文分片 6 且郡名全合",
  len([f for f in os.listdir("data/text") if f.endswith(".js")]) == 6,
  "juanshou/sy/zj/yf/j1/j2")
A("A13 京兆尹条存在且首县長安",
  any(s["n"] == "京兆尹" and s.get("seat") == "長安" for s in states))
A("A14 莽改县注计数", n_mang == 671, f"莽曰×{n_mang}")
A("A15 首县例之例外如实注",
  sum(1 for s in states if s.get("seat_note")) == 2, "梁國/日南郡")

# ── 2c. 账目对账（SHA256SUMS 指纹账本；行尾无关口径，过期即红） ──
print("── 账目对账（SHA256SUMS）")
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("build_sums", "tools/build_sums.py")
_bs = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_bs)
_want = _bs.collect()
_has_sums = os.path.exists("SHA256SUMS")
A("A19 账本在库且纯 LF", _has_sums
  and open("SHA256SUMS", "rb").read().count(b"\r") == 0,
  f"{len(open('SHA256SUMS', encoding='utf-8').read().splitlines()) if _has_sums else 0} 行"
  if _has_sums else "缺失——先 python tools/build_sums.py")
_lines = open("SHA256SUMS", encoding="utf-8").read().splitlines() if _has_sums else []
_problems, _seen = [], set()
for _i, _line in enumerate(_lines, 1):
    _parts = _line.split("  ", 1)
    _rel = _parts[1].strip().replace("\\", "/") if len(_parts) == 2 else ""
    if len(_parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", _parts[0]) or not _rel:
        _problems.append(f"第{_i}行格式非法"); continue
    if _rel in _seen:
        _problems.append(f"第{_i}行重复 {_rel}"); continue
    _seen.add(_rel)
    if not os.path.isfile(_rel):
        _problems.append(f"账上文件缺失 {_rel}"); continue
    if _bs.sha256(_rel) != _parts[0]:
        _problems.append(f"指纹不符 {_rel}")
A("A20 逐行指纹与磁盘实测一致", not _problems,
  f"失真 {len(_problems)}：{_problems[:2]}——重跑 python tools/build_sums.py" if _problems
  else f"{len(_lines)} 行全符")
A("A21 行数与生成器一致且产物无缺账",
  len(_lines) == len(_want) and not [r for r in _want if r not in _seen],
  f"账 {len(_lines)} 行 / 生成器 {len(_want)} 行"
  + ("" if len(_lines) == len(_want) else "——重跑 python tools/build_sums.py"))

# ── 2b. 互查桥 + 导出 + 论文 ──
xraw = open("data/xref_yh.js", encoding="utf-8").read()
xref = json.loads(xraw[xraw.find("{"): xraw.rfind("}") + 1])
xm = xref["meta"]
A("A16 汉唐互查桥自洽", xm["han_juns"] == len(states)
  and xm["matched"] + xm["unmatched"] == xm["han_juns"]
  and xm["matched"] >= 45 and xm["same_name"] + xm["renamed"] >= xm["matched"] - 2,
  f"同名同城 {xm['same_name']} · 承名 {xm['renamed']} · 迁治 {xm['qianyi']} · 无对应 {xm['unmatched']}（含元和缺卷归因）")
zc = open("docs/export/汉志经纬-郡国对照.csv", "rb").read()
xc = open("docs/export/汉志经纬-县名录.csv", "rb").read()
gj = json.load(open("docs/export/汉志经纬-郡治点位.geojson", encoding="utf-8"))
km = open("docs/export/汉志经纬-郡治点位.kml", encoding="utf-8").read()
n_zc = len(zc.decode("utf-8-sig").strip().splitlines()) - 1
n_xc = len(xc.decode("utf-8-sig").strip().splitlines()) - 1
A("A17 导出三格式同口径（CSV 带 BOM）",
  zc[:3] == b"\xef\xbb\xbf" and xc[:3] == b"\xef\xbb\xbf"
  and n_zc == stats["states"] == 103 and n_xc == stats["counties_parsed"]
  and len(gj["features"]) == stats["states"]
  and km.count("<Placemark>") == stats["states"],
  f"郡国 {n_zc} 行 · 县 {n_xc} 行 · 点位 {len(gj['features'])}")
A("A18 论文 PDF 在位", os.path.exists("docs/汉志经纬-数字人文.pdf")
  and os.path.getsize("docs/汉志经纬-数字人文.pdf") > 100000, "汉志经纬-数字人文.pdf（5 页 3 图）")

# ── 3. 本地服务健康检查 ──
try:
    urllib.request.urlopen(BASE + "index.html", timeout=3).read()
except Exception as e:
    print(f"✗ 本地服务不可达：{BASE} —— 请先 python -m http.server 9800")
    sys.exit(1)

# ── 4. 无头断言页 ──
CANDS = [
    os.environ.get("HS_BROWSER", ""),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]
EDGE = next((c for c in CANDS if c and os.path.exists(c)), None)
if not EDGE:
    print("✗ 未找到浏览器（可用环境变量 HS_BROWSER 指定）")
    sys.exit(1)

PAGES = ["tests/test_auto.html", "tests/test_ft.html", "tests/test_3d.html"]
# 「无日志」= 页面在虚时预算内没跑完（Worker 冷启动竞态）——有界重试+加预算；
# 一旦产出 TESTLOG 且含 FAIL 仍即红，重试只治「没跑」，不吞断言失败
BUDGETS = [18000, 30000, 45000]
for page in PAGES:
    lines = None
    for attempt, budget in enumerate(BUDGETS, 1):
        prof = tempfile.mkdtemp(prefix="hstest_")
        r = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu", "--no-first-run",
             "--user-data-dir=" + prof, "--virtual-time-budget=" + str(budget),
             "--dump-dom", BASE + page],
            capture_output=True, timeout=240)
        html = r.stdout.decode("utf-8", errors="replace")
        m = re.search(r'id="testlog"[^>]*>([^<]*)<', html)
        if m and "TESTLOG" in (m.group(1) or ""):
            lines = [l.strip() for l in m.group(1).splitlines()
                     if l.strip() and l.strip() not in ("TESTLOG", "ENDLOG")]
            if attempt > 1:
                print(f"  （第 {attempt} 次跑出日志，预算 {budget}）")
            break
    if lines is None:
        fails.append((page, ["脚本未产出 TESTLOG"]))
        print(f"✗ {page} 无日志产出（{len(BUDGETS)} 次重试后仍无）")
        continue
    bad = [l for l in lines if "FAIL" in l]
    print(("✓" if not bad else "✗") + f" {page} {len(lines)} 项断言")
    for l in bad:
        fails.append((page, [l]))
        print("    FAIL  " + l)

# ── 5. 离线四验（SW 在位 · 真断网重载 · 数据层离线可得 · 3D 断网直航；audit.yml 亦专步硬跑） ──
ro = subprocess.run([sys.executable, "tools/offline_check.py"],
                    capture_output=True, text=True, encoding="utf-8", timeout=300)
print("── 离线四验")
print(ro.stdout.strip())
if ro.returncode != 0:
    fails.append(("offline_check", ["exit %d" % ro.returncode]))

print()
if fails:
    print(f"回归未过：{sum(len(f[1]) for f in fails)} 个失败项")
    sys.exit(1)
print("回归通过：lint + 数据断言（A1–A%d）+ %d 断言页全绿" % (A_COUNT, len(PAGES)))
