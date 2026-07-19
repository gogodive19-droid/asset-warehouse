#!/usr/bin/env python3
# tree.json + template.html -> index.html
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
data = open(os.path.join(D, "tree.json"), encoding="utf-8").read().replace("</", "<\\/")
tpl = open(os.path.join(D, "template.html"), encoding="utf-8").read()
open(os.path.join(D, "index.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", data))
print("index.html", round(os.path.getsize(os.path.join(D, "index.html"))/1e6, 2), "MB")
