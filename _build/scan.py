#!/usr/bin/env python3
# 자산 창고 전체 폴더 트리 스캔 (재개 가능). 시간 예산 초과 시 캐시 저장 후 PARTIAL 출력.
# 사용: python3 scan.py "<창고 절대경로>" [budget_sec]
import os, json, sys, time, pickle

ROOT = sys.argv[1]
BUDGET = float(sys.argv[2]) if len(sys.argv) > 2 else 35.0
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(OUT_DIR, "scan_cache.pkl")
EXCLUDE_FILES = {"desktop.ini"}
t0 = time.time()

cache = {}
if os.path.exists(CACHE):
    with open(CACHE, "rb") as fp:
        cache = pickle.load(fp)

class TimeUp(Exception):
    pass

def build(path, rel):
    if rel in cache:
        n = cache[rel]
        return n, n["tf"], n["td"]
    if time.time() - t0 > BUDGET:
        raise TimeUp()
    name = os.path.basename(path.rstrip("/")) or path
    node = {"n": name, "f": 0, "c": []}
    try:
        entries = sorted(os.scandir(path), key=lambda e: e.name)
    except OSError:
        entries = []
    tf, td = 0, 0
    for e in entries:
        if e.name.startswith("."):
            continue
        try:
            if e.is_dir(follow_symlinks=False):
                child, ctf, ctd = build(e.path, rel + "/" + e.name)
                node["c"].append(child); tf += ctf; td += ctd + 1
            elif e.is_file(follow_symlinks=False):
                if e.name in EXCLUDE_FILES:
                    continue
                node["f"] += 1; tf += 1
        except OSError:
            continue
    node["tf"] = tf; node["td"] = td
    if not node["c"]:
        del node["c"]
    cache[rel] = node
    return node, tf, td

try:
    tree, tf, td = build(ROOT, "")
    tree["n"] = "4. 콘텐츠 자산 창고"
    kst = time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 9 * 3600))
    with open(os.path.join(OUT_DIR, "tree.json"), "w", encoding="utf-8") as fp:
        json.dump({"generated": kst, "tree": tree}, fp, ensure_ascii=False, separators=(",", ":"))
    if os.path.exists(CACHE):
        os.remove(CACHE)
    print(f"DONE dirs={td} files={tf} generated={kst} t={time.time()-t0:.0f}s")
except TimeUp:
    with open(CACHE, "wb") as fp:
        pickle.dump(cache, fp)
    print(f"PARTIAL cached={len(cache)} t={time.time()-t0:.0f}s -- run again")
