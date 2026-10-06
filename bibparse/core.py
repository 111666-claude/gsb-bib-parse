"""BibTeX 解析、宏展开、crossref 继承与按键查找。"""


class Counter:
    """记录解析过的字符数。"""

    def __init__(self):
        self.scanned = 0


class Entry:
    def __init__(self, key, kind, fields):
        self.key = key
        self.kind = kind
        self.fields = fields


class Db:
    def __init__(self):
        self.text = ""
        self.strings = {}
        self.entries = []
        self.by_key = {}


def _clean(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == "{" and raw[-1] == "}":
        return raw[1:-1]
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        return raw[1:-1]
    return raw


def split_fields(body):
    out = []
    depth = 0
    quote = False
    start = 0
    for i, ch in enumerate(body):
        if ch == '"':
            quote = not quote
        elif ch == "{" and not quote:
            depth += 1
        elif ch == "}" and not quote:
            depth -= 1
        elif ch == "," and depth == 0 and not quote:
            out.append(body[start:i])
            start = i + 1
    out.append(body[start:])
    return out


def _add_entry(db, kind, body):
    key, _, rest = body.partition(",")
    key = key.strip()
    if key in db.by_key:
        return
    entry = Entry(key, kind, {})
    for field in split_fields(rest):
        name, _, value = field.partition("=")
        name = name.strip().lower()
        if name:
            entry.fields[name] = _clean(value.strip())
    db.entries.append(entry)
    db.by_key[entry.key] = entry


def parse(text, counter):
    db = Db()
    db.text = text
    i = 0
    n = len(text)
    while i < n:
        at = text.find("@", i)
        if at < 0:
            break
        j = at + 1
        while j < n and (text[j].isalnum() or text[j] == "_"):
            j += 1
        kind = text[at + 1:j].lower()
        while j < n and text[j].isspace():
            j += 1
        if j >= n or text[j] != "{":
            i = j
            continue
        counter.scanned += 1
        depth = 1
        k = j + 1
        while k < n and depth > 0:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        body = text[j + 1:k - 1]
        if kind == "string":
            name, _, value = body.partition("=")
            db.strings[name.strip().lower()] = _clean(value.strip())
        else:
            _add_entry(db, kind, body)
        i = k
    _expand_strings(db)
    _apply_crossrefs(db)
    return db


def lookup(db, key, counter):
    counter.scanned += 1
    return db.by_key.get(key)


def _expand_strings(db):
    for entry in db.entries:
        for name, value in entry.fields.items():
            if value in db.strings:
                entry.fields[name] = db.strings[value]


def _apply_crossrefs(db):
    for entry in db.entries:
        ref_key = entry.fields.get("crossref")
        if not ref_key or ref_key not in db.by_key:
            continue
        parent = db.by_key[ref_key]
        for name, value in parent.fields.items():
            if name == "crossref":
                continue
            entry.fields.setdefault(name, value)
