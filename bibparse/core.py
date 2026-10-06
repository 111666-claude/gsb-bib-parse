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


def _is_quoted(raw):
    raw = raw.strip()
    return len(raw) >= 2 and (
        (raw[0] == "{" and raw[-1] == "}")
        or (raw[0] == '"' and raw[-1] == '"')
    )


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
    bare = set()
    for field in split_fields(rest):
        name, _, value = field.partition("=")
        name = name.strip().lower()
        if not name:
            continue
        raw = value.strip()
        if not _is_quoted(raw):
            bare.add(name)
        entry.fields[name] = _clean(raw)
    entry.bare = bare
    db.entries.append(entry)
    db.by_key[entry.key] = entry


def _inherit_crossref(db):
    for entry in db.entries:
        target_key = entry.fields.get("crossref")
        if not target_key:
            continue
        target = db.by_key.get(target_key.strip())
        if target is None:
            continue
        for name, value in target.fields.items():
            if name == "crossref" or name in entry.fields:
                continue
            entry.fields[name] = value


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
            db.strings[name.strip()] = _clean(value.strip())
        else:
            _add_entry(db, kind, body)
        i = k
    for entry in db.entries:
        for name in getattr(entry, "bare", ()):
            raw = entry.fields[name]
            if raw in db.strings:
                entry.fields[name] = db.strings[raw]
    _inherit_crossref(db)
    return db


def lookup(db, key, counter):
    counter.scanned += 1
    return db.by_key.get(key)
