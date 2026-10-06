# bib-parse

解析 BibTeX 数据库：`@string` 宏、字段大小写归一、`crossref` 继承、键去重，以及按键查找。只用 Python 标准库。

```
python3 -m unittest discover -s tests
python3 -m bibparse --sample=macro
python3 -m bibparse --sample=crossref
python3 -m bibparse --sample=dup
python3 -m bibparse --sample=fieldcase
python3 -m bibparse --sample=work
```

## 口径

- **宏**：`@string{name = value}` 登记宏；字段值若正好是宏名，取宏的值；否则按字面值。
- **字段名**：字段名大小写不敏感，一律按小写存取。
- **继承**：带 `crossref` 的条目，把被引用条目里缺失的字段补进来（`crossref` 本身不继承）。
- **去重**：同一个键只保留第一次出现的条目，后出现的同名键忽略。
- **查找**：按键查找走索引，不重新解析整份文本。

## 不变量

- 每个键在库里只有一条条目，且是首次出现的那条。
- 条目字段名都是小写；宏展开后字段值不再是裸宏名。
- `scanned` 不随条目数乘查找次数放大：八百条条目查八百次的 `scanned` 不超过 6000。

## 输出契约

场景打印一行 JSON，键随场景而定。`--sample=work` 打印 `{"entries": N, "scanned": N}`。
