"""固定场景，用来复现题面里的锚点。"""

import json

from . import core


def _line(obj):
    print(json.dumps(obj, ensure_ascii=False))


def _field(db, key, name):
    entry = core.lookup(db, key, core.Counter())
    if entry is None:
        return ""
    return entry.fields.get(name, "")


def run(name):
    if name == "macro":
        text = '@string{jn = "Journal of Testing"}\n@article{k, journal = jn}\n'
        db = core.parse(text, core.Counter())
        _line({"journal": _field(db, "k", "journal")})
        return 0
    if name == "crossref":
        text = ("@proceedings{p, year = {2020}}\n"
                "@inproceedings{k, crossref = {p}, title = {T}}\n")
        db = core.parse(text, core.Counter())
        _line({"year": _field(db, "k", "year")})
        return 0
    if name == "dup":
        text = "@article{k, title = {first}}\n@article{k, title = {second}}\n"
        db = core.parse(text, core.Counter())
        _line({"title": _field(db, "k", "title")})
        return 0
    if name == "fieldcase":
        text = "@article{k, Title = {Hello}}\n"
        db = core.parse(text, core.Counter())
        _line({"title": _field(db, "k", "title")})
        return 0
    if name == "work":
        parts = []
        for i in range(800):
            parts.append("@article{k%04d, title = {T%d}}\n" % (i, i))
        text = "".join(parts)
        db = core.parse(text, core.Counter())
        counter = core.Counter()
        for i in range(800):
            core.lookup(db, "k%04d" % i, counter)
        _line({"entries": 800, "scanned": counter.scanned})
        return 0
    raise SystemExit("未知场景：" + name)
