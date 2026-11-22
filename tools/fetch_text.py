# -*- coding: utf-8 -*-
"""汉志经纬 · 文本抓取（kanripo/KR2a0007《前漢書》文淵閣四庫本）

数据源: https://github.com/kanripo/KR2a0007 （raw.githubusercontent.com 直取）
  KR2a0007_000.txt —— 四庫提要（卷首文献，站内「关于」引据）
  KR2a0007_028.txt —— 卷二十八上/下 = 《漢書·地理志》全志（本站正书）
选源说明: 任务书示 KR2b0007/KR2a0003 有「地理志」命中——实测两仓卷目为
         《資治通鑑》与《史記索隱》，皆非汉书；GitHub 检索定正本 KR2a0007
         《前漢書》104 文件，地理志上下同在 _028.txt（mandoku 格式）。
特性: 断点续抓（已存且 >10KB 跳过）· 限速 >=0.6s · UA 自报 · 3 次退避重试
输出: data_raw/kr/ 下原始 txt（不进 git）；data/fetch_report.json 抓取盘点
用法: python tools/fetch_text.py [--force]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

FILES = {
    "000": "四庫提要",
    "028": "漢書地理志上下",
}
BASE = "https://raw.githubusercontent.com/kanripo/KR2a0007/master/KR2a0007_%s.txt"
UA = ("HSDZ-DH-site-builder/0.1 (digital humanities research; static site for "
      "Hanshu Dilizhi; polite crawl, >=0.6s/page)")
MIN_SIZE = {"000": 2000, "028": 50000}    # 卷28 全志 ~7.5万字符（≈183KB UTF-8）

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data_raw", "kr")

_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch_one(key: str, force: bool = False) -> str:
    dest = os.path.join(RAW, "KR2a0007_%s.txt" % key)
    if not force and os.path.exists(dest) and os.path.getsize(dest) > MIN_SIZE.get(key, 200):
        return "skip"
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(BASE % key, headers={"User-Agent": UA})
            with _opener.open(req, timeout=60) as r:
                data = r.read()
            text = data.decode("utf-8", errors="strict")
            if len(text) < MIN_SIZE.get(key, 200):
                raise IOError("suspiciously small (%d chars)" % len(text))
            if "mandoku" not in text[:80] and "TITLE" not in text[:400]:
                raise IOError("header missing (not mandoku?)")
            with open(dest, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            return "fetched %d chars" % len(text)
        except urllib.error.HTTPError as e:
            last_err = "HTTP %d" % e.code
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            last_err = str(e)
            time.sleep(5 * (attempt + 1))
    return "ERROR " + str(last_err)


def main():
    force = "--force" in sys.argv
    os.makedirs(RAW, exist_ok=True)
    report = {"source": "kanripo/KR2a0007（前漢書·文淵閣四庫本）via raw.githubusercontent.com",
              "files": [], "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    total_chars = 0
    errs = 0
    for key, label in FILES.items():
        res = fetch_one(key, force)
        tag = res.split()[0]
        n = 0
        if tag in ("skip", "fetched"):
            body = open(os.path.join(RAW, "KR2a0007_%s.txt" % key), encoding="utf-8").read()
            n = len(body.replace("¶", "").replace(" ", "").replace("\n", ""))
            total_chars += n
        if tag == "ERROR":
            errs += 1
        print("%s %s: %s" % (key, label, res))
        report["files"].append({"key": key, "label": label, "res": res,
                                "chars_no_space": n})
        if tag == "fetched":
            time.sleep(0.6)
    report["total_chars"] = total_chars
    with open(os.path.join(ROOT, "data", "fetch_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print("合计 %d 字（去空白）→ data/fetch_report.json" % total_chars)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
