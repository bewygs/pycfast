"""Build a docstring review packet for PyCFAST components.

The packet puts side by side, for every constructor parameter of a component:

* the CFAST keyword(s) it is written to (read from the ``NamelistRecord`` calls
  in the class source, so it never drifts from the serializer),
* the matching row of the keyword appendix (type, units, default),
* the matching entry of the User's Guide input chapter (label, default, text),
* the current numpydoc entry of the docstring,

followed by deterministic flags (missing entries, unit/default mismatches, GUI
wording) and the guide prose of the component's chapter. The reference is the
LaTeX vendored in ``docs/cfast-reference`` (see ``docs/update_cfast_ref.sh``).

Usage (from the repository root)::

    uv run python .claude/skills/cfast-docstrings/scripts/review_packet.py
    uv run python .claude/skills/cfast-docstrings/scripts/review_packet.py Compartment

Without argument a one-line summary per component is printed.
"""

from __future__ import annotations

import argparse
import ast
import inspect
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import pycfast  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[4]
REF_DIR = ROOT / "docs" / "cfast-reference"
GUIDE = REF_DIR / "Input_File_Chapter.tex"
APPENDIX = REF_DIR / "Appendix_CFAST_Keywords.tex"

# Guide scope of each component, as "Chapter > Section > Subsection" prefixes
COMPONENT_SCOPE: dict[str, list[str]] = {
    "SimulationEnvironment": ["Simulation Environment"],
    "Material": ["Thermal Properties"],
    "Compartment": ["Compartments"],
    "WallVent": ["Vents > Natural Ventilation > Wall Vents"],
    "CeilingFloorVent": ["Vents > Natural Ventilation > Ceiling/Floor Vents"],
    "MechanicalVent": ["Vents > Mechanical Ventilation"],
    "FireDefinition": ["Fires"],
    "Fire": ["Fires"],
    "Device": ["Measurement and Fire Protection Devices"],
    "Visualization": ["Visualization"],
}

# Guide chapters documenting each namelist, searched when a keyword has no
# entry in the component scope (e.g. vent opening options documented once)
NAMELIST_SCOPE: dict[str, list[str]] = {
    "HEAD": ["Simulation Environment"],
    "TIME": ["Simulation Environment"],
    "INIT": ["Simulation Environment"],
    "MISC": ["Simulation Environment"],
    "MATL": ["Thermal Properties"],
    "COMP": ["Compartments"],
    "VENT": ["Vents"],
    "FIRE": ["Fires"],
    "CHEM": ["Fires"],
    "TABL": ["Fires"],
    "DEVC": ["Measurement and Fire Protection Devices"],
    "ISOF": ["Visualization"],
    "SLCF": ["Visualization"],
}

# Appendix tables documenting each namelist
APPENDIX_TABLES: dict[str, list[str]] = {
    "CHEM": ["FIRE"],
    "FIRE": ["FIRE2"],
    "TABL": ["FIRE3"],
}

# Classes whose serializer writes some of the component's parameters
DELEGATES: dict[str, list[str]] = {"Fire": ["FireDefinition"]}

ATTRIBUTION = re.compile(r"Adapted from the `?CFAST User's Guide")
GUI_WORDS = re.compile(r"\b(tab|page|CEdit|button|click(ing)?)\b", re.IGNORECASE)
VERSION_WORDS = re.compile(r"\b(version\s+\d|CFAST\s+\d)", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# LaTeX
# --------------------------------------------------------------------------- #

_UNIT_REPL = [
    (r"\\degreeCelsius", "°C"),
    (r"\\degc", "°C"),
    (r"\\tothe\{([^}]*)\}", r"^(\1)"),
    (r"\^\{?2\}?", "²"),
    (r"\^\{?3\}?", "³"),
    (r"\.", "·"),
]


def _unit(text: str) -> str:
    for pat, rep in _UNIT_REPL:
        text = re.sub(pat, rep, text)
    return text


def _strip_braced(text: str, macro: str, keep: bool) -> str:
    r"""Remove ``\macro{...}`` (balanced braces), keeping the argument if asked."""
    out, i, token = [], 0, "\\" + macro + "{"
    while True:
        j = text.find(token, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:j])
        k, depth = j + len(token), 1
        while k < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            k += 1
        if keep:
            out.append(text[j + len(token) : k - 1])
        i = k


def clean_latex(text: str) -> str:
    """Convert a LaTeX fragment of the guide to plain text with RST literals."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", "", text, flags=re.DOTALL)
    text = re.sub(
        r"\\unit\{([^{}]*(\{[^{}]*\}[^{}]*)*)\}", lambda m: _unit(m.group(1)), text
    )
    text = re.sub(r"\\ct\{([^}]*)\}", lambda m: f"``{m.group(1)}``", text)
    text = re.sub(r"\{\\(ct|tt) ([^}]*)\}", lambda m: f"``{m.group(2)}``", text)
    text = re.sub(r"\{\\(it|em|bf) ([^}]*)\}", r"\2", text)
    for macro in ("cite", "label", "includegraphics", "Needspace"):
        text = _strip_braced(text, macro, keep=False)
    for macro in ("textbf", "textit", "emph", "underline", "texttt", "mathrm", "rm"):
        text = _strip_braced(text, macro, keep=True)
    text = re.sub(
        r"(Sec|Section|Chapter|Table|Fig)\.?~?\\ref\{([^}]*)\}", r"[\2]", text
    )
    text = re.sub(r"\\ref\{([^}]*)\}", r"[\1]", text)
    text = re.sub(r"\\footnote\{([^}]*)\}", r" (\1)", text)
    text = re.sub(r"_\{\\sss ([^}]*)\}", r"_\1", text)
    text = re.sub(r"\^?\\circ\s*", "°", text)
    text = _strip_braced(text, "hbox", keep=True)
    text = re.sub(r"\\sqrt\{([^{}]*)\}", r"(\1)^(1/2)", text)
    text = text.replace("\\mid", "|")
    text = text.replace("\\cdot", "·").replace("\\times", "×")
    text = text.replace("\\degreeCelsius", "°C").replace("\\%", "%")
    text = text.replace("\\_", "_").replace("---", "—").replace("``", '"')
    text = re.sub(r"(?<!`)''", '"', text)
    text = text.replace("~", " ").replace("$", "").replace("\\\\", "")
    # restore RST literals mangled by the quote replacement above
    text = re.sub(r'"([A-Z0-9_()=:,./\' ]+)"', r"``\1``", text)
    text = re.sub(r"\\(newpage|noindent|centering|item|hline)\b", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


@dataclass
class GuideItem:
    r"""One ``\item`` of a description list of the guide."""

    path: str
    label: str
    meta: str
    text: str
    keywords: list[str]


@dataclass
class GuideSection:
    """Prose paragraphs and items under one guide heading."""

    path: str
    prose: list[str] = field(default_factory=list)
    items: list[GuideItem] = field(default_factory=list)


def _meta_keywords(meta: str) -> list[str]:
    """Keywords listed after ``namelist:``; ``NML/KEY`` references keep the group."""
    if "namelist:" not in meta:
        return []
    names = re.findall(
        r"\\(?:ct|texttt)\{([A-Z][A-Z0-9_\\/]*)", meta.split("namelist:", 1)[1]
    )
    return [n.replace("\\", "") for n in names]


def _split_meta(body: str) -> tuple[str, str]:
    """Split ``(default: ...; namelist: ...) text`` into meta and text."""
    body = body.lstrip()
    if not body.startswith("("):
        return "", body
    depth = 0
    for i, ch in enumerate(body):
        depth += {"(": 1, ")": -1}.get(ch, 0)
        if depth == 0:
            return body[1:i], body[i + 1 :].lstrip(" :")
    return "", body


def parse_guide(path: Path = GUIDE) -> list[GuideSection]:
    r"""Parse the input chapter into sections of prose and ``\item`` entries."""
    raw = re.sub(r"(?<!\\)%.*", "", path.read_text())
    raw = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", "", raw, flags=re.DOTALL)
    heading = re.compile(
        r"\\(chapter|section|subsection)\*?\{((?:[^{}]|\{[^{}]*\})*)\}"
    )
    level = {"chapter": 0, "section": 1, "subsection": 2}
    stack: list[str] = []
    sections: list[GuideSection] = []
    pos = 0
    matches = list(heading.finditer(raw)) + [None]
    for m in matches:
        chunk = raw[pos : m.start() if m else len(raw)]
        if stack:
            sections.append(_parse_section(" > ".join(stack), chunk))
        if m is None:
            break
        lvl = level[m.group(1)]
        stack = stack[:lvl] + [clean_latex(m.group(2))]
        pos = m.end()
    return sections


def _parse_section(path: str, chunk: str) -> GuideSection:
    section = GuideSection(path)
    pieces = re.split(
        r"\\begin\{description\}(.*?)\\end\{description\}", chunk, flags=re.DOTALL
    )
    for i, piece in enumerate(pieces):
        if i % 2 == 0:
            for para in re.split(r"\n\s*\n", piece):
                para = clean_latex(" ".join(para.split()))
                if para:
                    section.prose.append(para)
            continue
        for entry in re.split(r"\\item(?=\[)", piece)[1:]:
            label_m = re.match(r"\[((?:[^\[\]]|\[[^\]]*\])*)\]", entry)
            if not label_m:
                continue
            meta, text = _split_meta(entry[label_m.end() :])
            keywords = _meta_keywords(meta)
            if not meta:  # unbalanced parenthesis in the guide
                head = re.match(
                    r"\s*:?\s*\((.*?namelist:(?:\s*\\ct\{[^}]*\},?)+)", text
                )
                if head:
                    meta, text = head.group(1), text[head.end() :]
                    keywords = _meta_keywords(meta)
            section.items.append(
                GuideItem(
                    path=path,
                    label=clean_latex(label_m.group(1)).strip(" :"),
                    meta=clean_latex(meta),
                    text=clean_latex(" ".join(text.split())),
                    keywords=keywords,
                )
            )
    return section


@dataclass
class AppendixRow:
    """One keyword row of an appendix table."""

    keyword: str
    type: str
    units: str
    default: str


def parse_appendix(path: Path = APPENDIX) -> dict[str, dict[str, AppendixRow]]:
    """Return ``{table_label: {KEYWORD: row}}`` from the keyword appendix."""
    raw = path.read_text()
    tables: dict[str, dict[str, AppendixRow]] = {}
    parts = re.split(r"\\label\{tbl:([A-Za-z0-9_]+)\}", raw)
    for label, body in zip(parts[1::2], parts[2::2], strict=True):
        end = body.find("\\end{xltabular}")
        if end < 0:
            continue
        rows: dict[str, AppendixRow] = {}
        for line in body[:end].splitlines():
            cells = [c.strip() for c in line.split("\\\\")[0].split("&")]
            m = re.match(r"\\ct\{([A-Z0-9_]+)\}", cells[0]) if len(cells) == 5 else None
            if m:
                rows[m.group(1)] = AppendixRow(
                    m.group(1),
                    clean_latex(cells[1]),
                    _unit(clean_latex(cells[3])),
                    clean_latex(cells[4]),
                )
        tables[label] = rows
    return tables


# --------------------------------------------------------------------------- #
# PyCFAST side
# --------------------------------------------------------------------------- #


def _self_attrs(
    node: ast.AST, assigns: dict[str, list[ast.AST]], seen: set[str]
) -> set[str]:
    """Collect ``self.<attr>`` reachable from an expression through local names."""
    attrs: set[str] = set()
    for sub in ast.walk(node):
        if (
            isinstance(sub, ast.Attribute)
            and isinstance(sub.value, ast.Name)
            and sub.value.id == "self"
        ):
            attrs.add(sub.attr)
        elif isinstance(sub, ast.Name) and sub.id in assigns and sub.id not in seen:
            seen.add(sub.id)
            for value in assigns[sub.id]:
                attrs |= _self_attrs(value, assigns, seen)
    return attrs


def _record_namelist(node: ast.AST, records: dict[str, str]) -> str | None:
    """Find the namelist group of the record an ``add_*`` call is made on."""
    while True:
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "NamelistRecord":
                arg = node.args[0] if node.args else None
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    return arg.value
                return None
            if isinstance(node.func, ast.Attribute):
                node = node.func.value
                continue
        if isinstance(node, ast.Name):
            return records.get(node.id)
        return None


def serialized_fields(cls: type) -> dict[tuple[str, str], set[str]]:
    """Map ``(NAMELIST, KEYWORD)`` to the attributes written by the class methods."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(cls)))
    out: dict[tuple[str, str], set[str]] = {}
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef):
            continue
        assigns: dict[str, list[ast.AST]] = {}
        records: dict[str, str] = {}
        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigns.setdefault(target.id, []).append(node.value)
                        nml = _record_namelist(node.value, records)
                        if nml:
                            records[target.id] = nml
        parents = {
            child: node
            for node in ast.walk(func)
            for child in ast.iter_child_nodes(node)
        }
        for node in ast.walk(func):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr.startswith("add_")
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                continue
            nml = _record_namelist(node.func.value, records)
            if nml is None:
                continue
            key = (nml, node.args[0].value)
            attrs = set()
            for arg in node.args[1:]:
                attrs |= _self_attrs(arg, assigns, set())
            # a constant value (e.g. SHAFT = True) is driven by the enclosing condition
            parent = parents.get(node)
            while not attrs and parent is not None and parent is not func:
                if isinstance(parent, ast.If):
                    attrs = _self_attrs(parent.test, assigns, set())
                parent = parents.get(parent)
            out.setdefault(key, set()).update(attrs)
    return out


@dataclass
class DocParam:
    """One entry of the docstring Parameters section."""

    name: str
    type: str
    text: str


def parse_docstring(doc: str) -> tuple[str, dict[str, str], dict[str, DocParam]]:
    """Split a numpydoc docstring into summary, sections and parameter entries."""
    lines = inspect.cleandoc(doc).splitlines()
    sections: dict[str, list[str]] = {"": []}
    current = ""
    i = 0
    while i < len(lines):
        if (
            i + 1 < len(lines)
            and lines[i].strip()
            and set(lines[i + 1].strip()) == {"-"}
        ):
            current = lines[i].strip()
            sections[current] = []
            i += 2
            continue
        sections[current].append(lines[i])
        i += 1
    params: dict[str, DocParam] = {}
    name = None
    for line in sections.get("Parameters", []):
        m = re.match(r"^(\w+)\s*:\s*(.*)$", line)
        if m and not line.startswith(" "):
            name = m.group(1)
            params[name] = DocParam(name, m.group(2), "")
        elif name and line.strip():
            params[name].text += " " + line.strip()
    for p in params.values():
        p.text = p.text.strip()
    joined = {k: "\n".join(v).strip() for k, v in sections.items()}
    return joined.get("", ""), joined, params


# --------------------------------------------------------------------------- #
# Comparison
# --------------------------------------------------------------------------- #

_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?")


def _numbers(value: object) -> list[float]:
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, (tuple, list)):
        return [n for v in value for n in _numbers(v)]
    return [float(n) for n in _NUM.findall(str(value))]


def _norm_units(units: str) -> set[str]:
    """Return the normalized alternatives of a unit string such as ``°C or %/m``."""
    out = set()
    for unit in re.split(r"\bor\b|[,|]", units.lower()):
        unit = (
            unit.replace(" ", "")
            .replace("°c", "k")
            .replace("·", "")
            .replace("%rh", "%")
        )
        unit = (
            unit.replace("^2", "²")
            .replace("^3", "³")
            .replace("m2", "m²")
            .replace("m3", "m³")
        )
        if unit:
            out.add(unit)
    return out


def _doc_default(text: str) -> str | None:
    m = re.search(r"default value:\s*(.+?)(?:\.\s|\.$|$)", text, re.IGNORECASE)
    return m.group(1) if m else None


def _doc_units(text: str) -> str | None:
    m = re.search(r"default units:\s*([^,.;]+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _guide_default(meta: str) -> str | None:
    meta = re.split(r"[;,]?\s*namelist:", meta)[0]
    m = re.search(r"default value:\s*([^;]+)", meta, re.IGNORECASE)
    m = m or re.search(r"default(?!\s+units):?\s+([^;]+)", meta, re.IGNORECASE)
    return m.group(1).strip().rstrip(",") if m else None


def _guide_units(meta: str) -> str | None:
    m = re.search(r"default units:\s*([^,;]+)", meta, re.IGNORECASE)
    return m.group(1).strip() if m else None


@dataclass
class ParamReport:
    """Everything known about one constructor parameter."""

    name: str
    default: object
    keys: list[tuple[str, str]]
    appendix: list[AppendixRow]
    items: list[GuideItem]
    doc: DocParam | None
    flags: list[str]


def _norm_label(label: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", label.upper()).strip("_")


def _in_scope(path: str, scopes: list[str]) -> bool:
    return any(path == s or path.startswith(s + " > ") for s in scopes)


def build_report(
    cls: type,
    sections: list[GuideSection],
    appendix: dict[str, dict[str, AppendixRow]],
) -> dict:
    """Compare a component with the guide and the appendix."""
    name = cls.__name__
    scope = COMPONENT_SCOPE.get(name, [])
    fields = serialized_fields(cls)
    for other in DELEGATES.get(name, []):
        fields.update(serialized_fields(getattr(pycfast, other)))
    namelists = sorted({nml for nml, _ in fields})
    scoped_items = [it for s in sections if _in_scope(s.path, scope) for it in s.items]

    def guide_items(nml: str, key: str) -> list[GuideItem]:
        hits = [it for it in scoped_items if key in it.keywords]
        hits = hits or [
            it
            for it in scoped_items
            if not it.keywords and _norm_label(it.label) == key
        ]
        if not hits:
            wider = NAMELIST_SCOPE.get(nml, [])
            hits = [
                it
                for s in sections
                if _in_scope(s.path, wider) and not _in_scope(s.path, scope)
                for it in s.items
                if key in it.keywords
            ]
        # explicit NML/KEY references from other chapters (e.g. COMP/GRID in Visualization)
        hits += [
            it for s in sections for it in s.items if f"{nml}/{key}" in it.keywords
        ]
        return hits

    def appendix_row(nml: str, key: str) -> AppendixRow | None:
        for table in APPENDIX_TABLES.get(nml, [nml]):
            if key in appendix.get(table, {}):
                return appendix[table][key]
        return None

    summary, doc_sections, doc_params = parse_docstring(cls.__doc__ or "")
    signature = inspect.signature(cls)
    params = [p for p in signature.parameters.values() if p.name != "self"]
    used_items: set[int] = set()
    reports: list[ParamReport] = []
    for p in params:
        keys = sorted(k for k, attrs in fields.items() if p.name in attrs)
        rows = [r for k in keys if (r := appendix_row(*k))]
        items: list[GuideItem] = []
        for k in keys:
            for it in guide_items(*k):
                if it not in items:
                    items.append(it)
        used_items |= {id(it) for it in items}
        doc = doc_params.get(p.name)
        default = None if p.default is inspect.Parameter.empty else p.default
        flags = []
        if doc is None:
            flags.append("missing from the docstring Parameters section")
        if not keys:
            flags.append("not written to any CFAST keyword (pycfast-only parameter?)")
        elif not items:
            flags.append(
                "no entry in the User's Guide input chapter (check the appendix and prose)"
            )
        if doc is not None:
            if gui := GUI_WORDS.search(doc.text):
                flags.append(f"GUI wording: {gui.group(0)!r}")
            if version := VERSION_WORDS.search(doc.text):
                flags.append(f"version-specific wording: {version.group(0)!r}")
            ref_units = [
                u
                for u in [
                    *(r.units for r in rows),
                    *(_guide_units(it.meta) for it in items),
                ]
                if u
            ]
            doc_units = _doc_units(doc.text)
            ref_norm = (
                set().union(*(_norm_units(u) for u in ref_units))
                if ref_units
                else set()
            )
            if ref_units and doc_units and not _norm_units(doc_units) & ref_norm:
                flags.append(
                    f"units differ: docstring {doc_units!r}, reference {sorted(set(ref_units))}"
                )
            if ref_units and not doc_units and doc.text:
                flags.append(f"units not stated, reference {sorted(set(ref_units))}")
            doc_default = _doc_default(doc.text)
            effective = default
            if default is None:
                refs = [
                    d
                    for d in [
                        *(_guide_default(it.meta) for it in items),
                        *(r.default for r in rows),
                    ]
                    if d
                ]
                effective = refs[0] if refs else None
            if doc_default and _numbers(doc_default) and _numbers(effective):
                if not set(_numbers(effective)) <= set(_numbers(doc_default)):
                    flags.append(
                        f"default differs: docstring {doc_default!r}, effective {effective!r}"
                    )
        reports.append(ParamReport(p.name, default, keys, rows, items, doc, flags))

    extra_doc = sorted(set(doc_params) - {p.name for p in params})
    # Components documented in the same chapter (Fire / FireDefinition) share keywords
    components = _components()
    group = [c for c in components if COMPONENT_SCOPE[c.__name__] == scope]
    written = set(fields).union(*(serialized_fields(c) for c in group))
    written_all = set().union(*(serialized_fields(c) for c in components))
    # TABL column labels (HRR, AREA, CO_YIELD...) are keywords as well
    labels = {label for c in group for label in getattr(c, "LABELS", ())}
    written_keys = {k for _, k in written} | labels
    not_exposed: list[tuple[str, GuideItem | AppendixRow]] = []
    seen: set[str] = set()
    for it in scoped_items:
        for key in it.keywords:
            if "/" in key:  # explicit NML/KEY reference to another namelist
                if tuple(key.split("/", 1)) in written_all:
                    continue
            elif key in written_keys:
                continue
            if key not in seen:
                seen.add(key)
                not_exposed.append((key, it))
    others = set().union(
        *(serialized_fields(c) for c in components if c not in group and c is not cls)
    )
    for nml in namelists:
        if any(n == nml for n, _ in others):
            continue  # shared namelist (VENT): only keywords documented in scope are listed
        for table in APPENDIX_TABLES.get(nml, [nml]):
            for key, row in appendix.get(table, {}).items():
                if key not in written_keys and key not in seen:
                    seen.add(key)
                    not_exposed.append((key, row))
    unmatched = [
        it for it in scoped_items if id(it) not in used_items and it.keywords == []
    ]
    class_flags = []
    if not ATTRIBUTION.search(doc_sections.get("Notes", "")):
        class_flags.append(
            "attribution line 'Adapted from the CFAST User's Guide' missing from Notes"
        )
    for sec in ("", "Notes"):
        hit = GUI_WORDS.search(doc_sections.get(sec, ""))
        if hit:
            class_flags.append(
                f"GUI wording in {'summary' if not sec else sec}: {hit.group(0)!r}"
            )
        hit = VERSION_WORDS.search(doc_sections.get(sec, ""))
        if hit:
            class_flags.append(
                f"version-specific wording in {'summary' if not sec else sec}: {hit.group(0)!r}"
            )
    return {
        "name": name,
        "scope": scope,
        "namelists": namelists,
        "params": reports,
        "extra_doc": extra_doc,
        "not_exposed": not_exposed,
        "unmatched": unmatched,
        "class_flags": class_flags,
        # in-scope sections, plus those of guide entries matched from other chapters
        "sections": [
            s
            for s in sections
            if _in_scope(s.path, scope) or any(id(it) in used_items for it in s.items)
        ],
    }


def _components() -> list[type]:
    return [getattr(pycfast, n) for n in COMPONENT_SCOPE if hasattr(pycfast, n)]


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #


def _fmt_keys(keys: list[tuple[str, str]]) -> str:
    return ", ".join(f"{n}.{k}" for n, k in keys) or "—"


def print_packet(report: dict) -> None:
    """Print the review packet of one component as Markdown."""
    ref = (REF_DIR / ".cfast_version").read_text().strip()
    print(f"# Review packet: {report['name']}\n")
    print(f"Reference: docs/cfast-reference @ firemodels/cfast {ref[:10]}")
    print(f"Guide scope: {', '.join(report['scope']) or '—'}")
    print(f"Namelists written: {', '.join(report['namelists']) or '—'}\n")
    if report["class_flags"]:
        print("## Class-level flags\n")
        for f in report["class_flags"]:
            print(f"- {f}")
        print()
    print("## Parameters\n")
    for p in report["params"]:
        print(f"### `{p.name}` -> {_fmt_keys(p.keys)}\n")
        print(f"- signature default: {p.default!r}")
        for r in p.appendix:
            print(
                f"- appendix {r.keyword}: type {r.type or '—'} | units {r.units or '—'} | default {r.default or '—'}"
            )
        for it in p.items:
            meta = f" ({it.meta})" if it.meta else ""
            print(f"- guide [{it.path}] **{it.label}**{meta}: {it.text}")
        if p.doc is not None:
            print(f"- docstring ({p.doc.type}): {p.doc.text or '—'}")
        for f in p.flags:
            print(f"- FLAG: {f}")
        print()
    if report["extra_doc"]:
        print("## Documented but not in the signature\n")
        for n in report["extra_doc"]:
            print(f"- `{n}`")
        print()
    if report["not_exposed"]:
        print("## CFAST keywords in scope that the component does not write\n")
        for key, src in report["not_exposed"]:
            if isinstance(src, GuideItem):
                meta = f" ({src.meta})" if src.meta else ""
                print(f"- {key}: guide [{src.path}] **{src.label}**{meta}: {src.text}")
            else:
                print(
                    f"- {key}: appendix type {src.type or '—'} | units {src.units or '—'} | default {src.default or '—'}"
                )
        print()
    if report["unmatched"]:
        print("## Guide entries without keyword not matched to a parameter\n")
        for it in report["unmatched"]:
            meta = f" ({it.meta})" if it.meta else ""
            print(f"- [{it.path}] **{it.label}**{meta}: {it.text}")
        print()
    print("## Guide prose in scope\n")
    for s in report["sections"]:
        if s.prose:
            print(f"### {s.path}\n")
            for para in s.prose:
                print(para + "\n")


def main(argv: list[str] | None = None) -> int:
    """Print the summary or the review packets asked on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "components", nargs="*", help="component class names (default: summary of all)"
    )
    args = parser.parse_args(argv)
    sections = parse_guide()
    appendix = parse_appendix()
    if not args.components:
        print(f"{'component':<24}{'params':>7}{'flags':>7}{'not written':>13}")
        for cls in _components():
            r = build_report(cls, sections, appendix)
            n_flags = sum(len(p.flags) for p in r["params"]) + len(r["class_flags"])
            print(
                f"{cls.__name__:<24}{len(r['params']):>7}{n_flags:>7}{len(r['not_exposed']):>13}"
            )
        return 0
    for name in args.components:
        if name not in COMPONENT_SCOPE:
            print(
                f"Unknown component {name!r}, choose from {', '.join(COMPONENT_SCOPE)}",
                file=sys.stderr,
            )
            return 1
        print_packet(build_report(getattr(pycfast, name), sections, appendix))
    return 0


if __name__ == "__main__":
    sys.exit(main())
