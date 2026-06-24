# jsonforge

![Tests](https://github.com/NzJulien/jsonforge/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Infer JSON Schemas, validate JSON documents, and diff JSON data — with zero runtime dependencies.**

`jsonforge` is a small toolkit for working with JSON structurally. Point it at
real-world JSON and it will figure out a schema for you, tell you whether new
data still conforms, and show you exactly what changed between two versions
of a document.

## Why

Most projects that consume JSON (APIs, config files, data exports) eventually
need to answer three questions:

1. **What shape is this data, really?** → `infer`
2. **Does this document still match that shape?** → `validate`
3. **What changed between two versions of it?** → `diff`

`jsonforge` answers all three with a single, dependency-free package.

## Install

```bash
git clone https://github.com/NzJulien/jsonforge.git
cd jsonforge
pip install -e .
```

## CLI Usage

### Infer a schema from sample data

```bash
jsonforge infer examples/users.json -t "User Schema" -o schema.json
```

Given multiple sample files (or a JSON array of records), `jsonforge` merges
them: fields missing from some samples are correctly left out of `required`,
and fields whose type varies across samples become a type union.

```bash
jsonforge infer samples/*.json -o schema.json
```

### Validate data against a schema

```bash
jsonforge validate data.json schema.json
```

```
INVALID: 1 error(s) found
  $.age: expected type 'integer', got str
```

Exit code is `0` when valid, `1` when invalid — safe to use in CI.

### Diff two JSON documents

```bash
jsonforge diff examples/users.json examples/users_v2.json
```

```
~ $[0].age: 36 -> 37
+ $[0].tags[2] = 'pioneer'
~ $[1].active: True -> False
+ $[2] = {'id': 3, 'name': 'Margaret Hamilton', ...}

4 change(s) found.
```

## Library Usage

```python
from jsonforge import infer_schema, validate, diff

samples = [
    {"name": "Ada", "age": 36},
    {"name": "Grace", "age": 85, "nickname": "Amazing Grace"},
]

schema = infer_schema(samples, title="Person")
# "name" and "age" become required; "nickname" stays optional

result = validate({"name": "Ada", "age": "old"}, schema)
if not result:
    for error in result.errors:
        print(error)
    # $.age: expected type 'integer', got str

changes = diff({"age": 36}, {"age": 37})
for change in changes:
    print(change)
    # ~ $.age: 36 -> 37
```

## What's supported

**Inference** — primitive types, nested objects, arrays, optional field
detection across samples, type unions (e.g. a field that's sometimes a
string and sometimes an integer).

**Validation** — `type`, `properties`, `required`, `items`, `enum`,
`minimum` / `maximum`, `minLength` / `maxLength`, `pattern`, `anyOf`,
`additionalProperties`.

**Diff** — added / removed / changed detection across nested objects and
arrays, with JSONPath-style addressing (`$.user.tags[1]`). Integers and
floats with equal value are not treated as a type change.

## Project layout

```
jsonforge/
├── jsonforge/
│   ├── inferencer.py   # sample data -> JSON Schema
│   ├── validator.py    # JSON Schema validation (no external deps)
│   ├── differ.py       # structural diff between two JSON documents
│   ├── cli.py           # argparse-based command line interface
│   └── utils.py        # JSON IO + terminal color helpers
├── tests/               # pytest suite (25 tests)
├── examples/            # sample data used in the README and CI
└── .github/workflows/   # CI: runs the test suite on Python 3.9–3.12
```

## Running the tests

```bash
pip install -e ".[dev]"
pytest -v
```

## License

MIT — see [LICENSE](LICENSE).

---

Made by [NzJulien](https://github.com/NzJulien)
