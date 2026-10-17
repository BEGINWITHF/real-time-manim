"""Static checker for the native DLL parameter bindings.

    python tools/check_bindings.py [--dump] [--json] [--only NAME] [--include-tests]

The renderer talks to `native/` through ctypes.  Two independent declarations
of the same function have to agree, and neither side ever verifies it:

    native/platform.h                      real_time_manim/window/core.py
    ----------------------------------     ----------------------------------
    void AddRect(float x, float y, ...)    self.dll.AddRect.argtypes = [...]
                                           self.dll.AddRect.restype = None

ctypes accepts both sides blindly, so the classic defects are all SILENT:

    忘绑  UNBOUND_ARGTYPES  the export never gets an `argtypes` list.  ctypes
          then assumes every argument is an `int`, which truncates every
          pointer argument on Win64 and crashes (or corrupts) at call time.
    绑反  *_SWAPPED          the types are all right but in the wrong order --
          two `float`s next to two `int`s swap `x/y` for `r/g` and the frame
          renders "successfully" with the wrong colours/positions.
    漏绑  ARG_COUNT_MISMATCH the list is one entry short/long, so every later
          argument lands on the wrong parameter.

The tool parses three things and diffs them:

    1. the C contract  -- every `__declspec(dllexport)` prototype/definition
                          under native/ (platform.h is the documented form;
                          the .c/.m definitions are cross-checked against it),
    2. the Python side -- every `<dll>.<fn>.argtypes = [...]` / `.restype = ...`
                          assignment, plus the `getattr(dll, 'Name', None)`
                          aliases (SetBackgroundColor, Vulkan_InitEx, ...),
    3. every call site -- `<dll>.<fn>(...)`, checked for argument count,
                          a missing/extra `byref`, and argument order by
                          comparing the caller's variable names with the C
                          parameter names.

Exit status: 1 when there is at least one ERROR, else 0.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NATIVE_DIR = os.path.join(REPO, "native")

SEVERITIES = ("ERROR", "WARN", "INFO")

# --------------------------------------------------------------------------
# canonical type names
# --------------------------------------------------------------------------
# Both sides are normalised to the same small vocabulary so that
# `const float*` (C) and `ctypes.POINTER(ctypes.c_float)` compare equal.

BASE_C = {
    "void": "void",
    "char": "char", "signed char": "char", "unsigned char": "u8",
    "short": "i16", "signed short": "i16", "unsigned short": "u16",
    "int": "i32", "signed": "i32", "signed int": "i32", "unsigned": "u32",
    "unsigned int": "u32",
    "long": "long", "signed long": "long", "unsigned long": "ulong",
    "long int": "long", "unsigned long int": "ulong",
    "long long": "i64", "signed long long": "i64",
    "unsigned long long": "u64",
    "float": "f32", "double": "f64", "long double": "f64",
    "bool": "bool", "_Bool": "bool",
    "size_t": "size_t", "ssize_t": "ssize_t",
    "int8_t": "i8", "uint8_t": "u8",
    "int16_t": "i16", "uint16_t": "u16",
    "int32_t": "i32", "uint32_t": "u32",
    "int64_t": "i64", "uint64_t": "u64",
    "intptr_t": "intptr_t", "uintptr_t": "uintptr_t",
}

BASE_CTYPES = {
    "None": "void",
    "c_bool": "bool",
    "c_char": "char", "c_wchar": "wchar",
    "c_byte": "i8", "c_ubyte": "u8",
    "c_short": "i16", "c_ushort": "u16",
    "c_int": "i32", "c_uint": "u32",
    "c_long": "long", "c_ulong": "ulong",
    "c_longlong": "i64", "c_ulonglong": "u64",
    "c_float": "f32", "c_double": "f64", "c_longdouble": "f64",
    "c_int8": "i8", "c_uint8": "u8",
    "c_int16": "i16", "c_uint16": "u16",
    "c_int32": "i32", "c_uint32": "u32",
    "c_int64": "i64", "c_uint64": "u64",
    "c_size_t": "size_t", "c_ssize_t": "ssize_t",
    "c_char_p": "str", "c_wchar_p": "wchar",
    "c_void_p": "void*",
    "py_object": "py_object",
    # ctypes.wintypes
    "DWORD": "u32", "WORD": "u16", "BYTE": "u8", "BOOL": "i32",
    "INT": "i32", "UINT": "u32", "LONG": "long", "ULONG": "ulong",
    "HANDLE": "void*", "HWND": "void*", "HDC": "void*",
    "LPWSTR": "wchar*", "LPCWSTR": "wchar*",
    "LPARAM": "intptr_t", "WPARAM": "uintptr_t",
}

TYPE_WORDS = set("""
void char short int long float double signed unsigned const volatile restrict
struct enum union bool _Bool size_t ssize_t wchar_t
int8_t uint8_t int16_t uint16_t int32_t uint32_t int64_t uint64_t
intptr_t uintptr_t
""".split())

STOPWORDS = {
    "return", "if", "else", "while", "for", "switch", "do", "case", "default",
    "sizeof", "typeof", "assert", "static_assert", "goto", "break", "continue",
}


def canon_c(type_str: str) -> str:
    """`const float *` -> `f32*`, `char *` -> `str`, `void` -> `void`."""
    stars = type_str.count("*") + len(re.findall(r"\[[^\]]*\]", type_str))
    t = re.sub(r"\[[^\]]*\]", " ", type_str)      # array declarators are pointers
    t = re.sub(r"\b(const|volatile|restrict|struct|enum|union|extern|static)\b",
               " ", t)
    t = t.replace("*", " ")
    t = re.sub(r"\s+", " ", t).strip().lower()
    base = BASE_C.get(t, t)
    if base == "void":
        return "void" if stars == 0 else "void*"
    if base == "char" and stars == 1:
        return "str"
    if base == "wchar" and stars == 1:
        return "wchar*"
    return base + "*" * stars


def _unwrap(expr: str, head: str) -> tuple[str, int] | None:
    """`POINTER(POINTER(c_float))` -> (`c_float`, 2) for head='POINTER'."""
    expr = expr.strip()
    n = 0
    while True:
        m = re.fullmatch(r"%s\s*\((.*)\)" % re.escape(head), expr, re.DOTALL)
        if not m:
            return (expr, n) if n else None
        n += 1
        expr = m.group(1).strip()


def canon_ctypes(expr: str) -> str:
    """`ctypes.POINTER(ctypes.c_float)` -> `f32*`, `ctypes.c_char_p` -> `str`."""
    e = re.sub(r"\s+", " ", expr.strip())
    if e.startswith("#"):
        return "?"
    while e.startswith("ctypes."):
        e = e[len("ctypes."):]
    e = e.removeprefix("wintypes.")

    stars = 0
    wrapped = _unwrap(e, "POINTER")
    if wrapped is not None:
        e, stars = wrapped
        e = e.strip()
        while e.startswith("ctypes."):
            e = e[len("ctypes."):]
    else:
        while e.endswith("*"):
            stars += 1
            e = e[:-1].rstrip()

    base = BASE_CTYPES.get(e, e)
    if base == "void":
        return "void" if stars == 0 else "void*"
    if base == "char" and stars:
        return "str"
    if base == "wchar" and stars:
        return "wchar*"
    if base == "str" and stars:          # POINTER(c_char_p) -- nonsense, keep it
        return "str*" * stars
    return base + "*" * stars


def compatible(a: str, b: str) -> bool:
    """True when the two canonical names can be passed across the boundary."""
    if a == b or a == "?" or b == "?":
        return True
    if a == "void*" and b.endswith("*"):
        return True
    if b == "void*" and a.endswith("*"):
        return True
    return False


SHOW_CTYPES = {
    "void": "None",
    "bool": "ctypes.c_bool",
    "char": "ctypes.c_char",
    "wchar": "ctypes.c_wchar",
    "i8": "ctypes.c_byte", "u8": "ctypes.c_ubyte",
    "i16": "ctypes.c_short", "u16": "ctypes.c_ushort",
    "i32": "ctypes.c_int", "u32": "ctypes.c_uint",
    "long": "ctypes.c_long", "ulong": "ctypes.c_ulong",
    "i64": "ctypes.c_longlong", "u64": "ctypes.c_ulonglong",
    "f32": "ctypes.c_float", "f64": "ctypes.c_double",
    "size_t": "ctypes.c_size_t", "ssize_t": "ctypes.c_ssize_t",
    "intptr_t": "ctypes.c_ssize_t", "uintptr_t": "ctypes.c_size_t",
    "str": "ctypes.c_char_p", "wchar*": "ctypes.c_wchar_p",
    "void*": "ctypes.c_void_p",
}


def show(t: str) -> str:
    """Canonical name -> the ctypes spelling a human would write."""
    if t in SHOW_CTYPES:
        return SHOW_CTYPES[t]
    if t.endswith("*"):
        inner = t[:-1]
        if inner == "char":
            inner = "u8"
        return "ctypes.POINTER(%s)" % show(inner)
    return t


# --------------------------------------------------------------------------
# source helpers
# --------------------------------------------------------------------------

def read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def find_close(text: str, open_idx: int) -> int:
    """Index of the bracket matching text[open_idx] (which is one of ([{ )."""
    depth = 0
    for i in range(open_idx, len(text)):
        c = text[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def split_top(text: str) -> list[str]:
    """Split on commas that sit outside any bracket."""
    parts, cur, depth = [], [], 0
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    tail = "".join(cur)
    if tail.strip() or parts:
        parts.append(tail)
    return [p.strip() for p in parts if p.strip()]


def mask_python(src: str) -> str:
    """Blank comments and docstring bodies; neuter brackets inside strings.

    The result keeps every character offset (so line numbers still work) and
    keeps ordinary string *contents* readable -- `getattr(dll, 'Name', None)`
    must stay greppable -- but `(`, `)`, `,` and `#` inside a string become
    spaces so that bracket balancing and argument splitting cannot be fooled.
    """
    out = list(src)
    i, n = 0, len(src)

    def blank(a: int, b: int, keep: str = "") -> None:
        for k in range(a, b):
            if out[k] == "\n":
                continue
            if keep and src[k] in keep:
                continue
            out[k] = " "

    while i < n:
        c = src[i]
        if c == "#":
            j = src.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif src.startswith('"""', i) or src.startswith("'''", i):
            q = src[i:i + 3]
            j = src.find(q, i + 3)
            j = n if j < 0 else j + 3
            blank(i, j)
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == c:
                    j += 1
                    break
                if src[j] == "\n":
                    break
                j += 1
            blank(i + 1, max(i + 1, j - 1), keep="")
            # keep the name characters: alias detection reads them back
            for k in range(i + 1, max(i + 1, j - 1)):
                if src[k].isalnum() or src[k] in "_.":
                    out[k] = src[k]
            i = j
        else:
            i += 1
    return "".join(out)


# --------------------------------------------------------------------------
# 1. the C contract
# --------------------------------------------------------------------------

@dataclass
class Sig:
    name: str
    ret: str
    params: list          # [{'type': 'f32', 'name': 'x', 'raw': 'float x'}, ...]
    file: str
    line: int
    kind: str             # 'proto' | 'def'

    @property
    def param_types(self) -> list[str]:
        return [p["type"] for p in self.params]

    @property
    def param_names(self) -> list[str]:
        return [p["name"] for p in self.params]

    def text(self) -> str:
        return "%s %s%s" % (self.ret, self.name,
                            "(" + ", ".join(p["raw"] for p in self.params) + ")")


@dataclass
class Export:
    name: str
    proto: Sig | None = None
    defs: list = field(default_factory=list)

    @property
    def sig(self) -> Sig:
        return self.proto or self.defs[0]

    @property
    def param_types(self) -> list[str]:
        return [p["type"] for p in self.sig.params]

    @property
    def param_names(self) -> list[str]:
        return [p["name"] for p in self.sig.params]

    @property
    def ret(self) -> str:
        return self.sig.ret


def parse_param(raw: str) -> dict | None:
    p = raw.strip()
    if not p:
        return None
    p = re.sub(r"\s*=\s*.*$", "", p, flags=re.DOTALL).strip()   # C++ default value
    if not p or p == "void":
        return None
    toks = p.split()
    name = ""
    if len(toks) > 1:
        last = toks[-1]
        stars = ""
        while last.startswith("*"):
            stars += "*"
            last = last[1:]
        if last and re.fullmatch(r"[A-Za-z_]\w*", last) \
                and last.lower() not in TYPE_WORDS:
            name = last
            p = " ".join(toks[:-1]) + stars
    return {"type": canon_c(p), "name": name, "raw": raw.strip()}


def parse_signature(prefix: str, params_txt: str) -> tuple | None:
    """`__declspec(dllexport) void AddRect` + the parameter text ->
    (name, canonical return, [param dicts])."""
    prefix = re.sub(r"__declspec\s*\(\s*dllexport\s*\)", " ", prefix.strip())
    prefix = prefix.strip()
    if not prefix or any(ch in prefix for ch in ";={}()"):
        return None
    m = re.fullmatch(r"([A-Za-z_][\w\s\*]*[\s\*])\s*([A-Za-z_]\w*)", prefix)
    if not m:
        return None
    ret, name = m.group(1).strip(), m.group(2)
    if name in STOPWORDS or ret.split()[0] in STOPWORDS:
        return None
    if "#" in ret:
        return None
    params = []
    for raw in split_top(params_txt):
        parsed = parse_param(raw)
        if parsed is not None:
            params.append(parsed)
    return name, canon_c(ret), params


def native_files(native_dir: str = NATIVE_DIR) -> list[str]:
    found = []
    for root, _dirs, files in os.walk(native_dir):
        for fn in sorted(files):
            if fn.endswith((".h", ".c", ".m", ".mm", ".cpp")):
                found.append(os.path.join(root, fn))
    return sorted(found)


DECLSPEC_RE = re.compile(r"__declspec\s*\(\s*dllexport\s*\)")


def scan_native(native_dir: str = NATIVE_DIR,
                repo: str = REPO) -> dict[str, Export]:
    """Exports come from `__declspec(dllexport)`; prototypes from .h files,
    definitions from .c/.m files, then every definition of a known export is
    cross-checked against the header even when it carries no declspec
    (platform_mac.m writes them plain)."""
    exports: dict[str, Export] = {}
    rel = lambda p: os.path.relpath(p, repo).replace("\\", "/")
    files = native_files(native_dir)

    for path in files:
        src = read(path)
        is_header = path.endswith(".h")
        for m in DECLSPEC_RE.finditer(src):
            j = src.find("(", m.end())
            if j < 0:
                continue
            parsed = parse_signature(src[m.end():j], src[j + 1:find_close(src, j)])
            if not parsed:
                continue
            close = find_close(src, j)
            k = close + 1
            while k < len(src) and src[k] in " \t\r\n":
                k += 1
            if k >= len(src):
                continue
            kind = "proto" if src[k] == ";" else "def" if src[k] == "{" else None
            if kind is None or (kind == "proto") != is_header:
                continue
            name, ret, params = parsed
            sig = Sig(name, ret, params, rel(path), line_of(src, m.start()), kind)
            exp = exports.setdefault(name, Export(name))
            if kind == "proto":
                if exp.proto is None:
                    exp.proto = sig
            else:
                exp.defs.append(sig)

    # definitions written without declspec (platform_mac.m)
    for name in list(exports):
        for path in files:
            if not path.endswith((".c", ".m", ".mm", ".cpp")):
                continue
            src = read(path)
            for m in re.finditer(r"(?<![\w.>)])" + re.escape(name) + r"\s*\(", src):
                line_start = src.rfind("\n", 0, m.start()) + 1
                prefix = src[line_start:m.start()]
                close = find_close(src, m.end() - 1)
                if close < 0:
                    continue
                k = close + 1
                while k < len(src) and src[k] in " \t\r\n":
                    k += 1
                if k >= len(src) or src[k] != "{":
                    continue
                parsed = parse_signature(prefix, src[m.end():close])
                if not parsed:
                    continue
                found_name, ret, params = parsed
                if found_name != name or not prefix.strip():
                    continue
                sig = Sig(name, ret, params, rel(path),
                          line_of(src, m.start()), "def")
                exp = exports[name]
                if not any(d.file == sig.file and d.line == sig.line
                           for d in exp.defs):
                    exp.defs.append(sig)
    return exports


# --------------------------------------------------------------------------
# 2. the Python bindings
# --------------------------------------------------------------------------

@dataclass
class Binding:
    symbol: str
    file: str
    line: int
    argtypes: list | None            # canonical names, None = never assigned
    argtypes_raw: str
    restype: str | None              # canonical name, None = never assigned
    restype_raw: str
    optional: bool                   # looked up through getattr(..., None)


@dataclass
class Call:
    symbol: str
    file: str
    line: int
    args: list[str]
    check: bool = True          # False for an aliased handle reused elsewhere
    varkinds: dict = field(default_factory=dict)  # name -> ctypes kind


BIND_RE = re.compile(r"(?:\b[\w.]*\bdll)\.(\w+)\.(argtypes|restype)\s*=")
ALIAS_RE = re.compile(r"(\w+)\s*=\s*getattr\(\s*([\w.]+?)\s*,\s*'(\w+)'\s*,"
                      r"|(\w+)\s*=\s*getattr\(\s*([\w.]+?)\s*,\s*\"(\w+)\"\s*,")
CALL_RE = re.compile(r"(?:\b[\w.]*\bdll)\.(\w+)\s*\(")
ASSIGN_RE = re.compile(r"(?<![\w.])\s*(\w+)\s*=\s*([^\n#]+)")


def infer_ctypes_vars(src: str) -> dict[str, str]:
    """Lightweight per-file inference of what a ctypes variable holds.

    Only the shapes that matter for the byref check are recognised:
    `w = ctypes.c_int(0)` is a scalar *instance* (must be passed by
    `ctypes.byref(w)`), `(ctypes.c_float * n)(...)` is an array (must not)."""
    kinds: dict[str, str] = {}
    for m in ASSIGN_RE.finditer(src):
        name, expr = m.group(1), m.group(2).strip()
        if re.match(r"^\(?ctypes\.c_\w+\s*\*", expr) \
                or "ctypes.POINTER" in expr:
            kinds[name] = "array"
        elif re.match(r"^ctypes\.c_\w+\s*\(", expr):
            kinds[name] = "scalar"
        elif "create_string_buffer" in expr or "create_unicode_buffer" in expr:
            kinds[name] = "buffer"
        elif re.match(r"^(?:ctypes\.)?(?:byref|pointer|cast)\s*\(", expr):
            kinds[name] = "byref"
    return kinds


def python_roots(include_tests: bool, repo: str = REPO,
                 roots: list[str] | None = None) -> list[str]:
    if roots is None:
        roots = ["real_time_manim", "examples", "run.py", "run_all.py"]
        if include_tests:
            roots += ["tests", "tools"]
    out = []
    for r in roots:
        p = os.path.join(repo, r)
        if os.path.isfile(p):
            out.append(p)
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                out += [os.path.join(root, f) for f in sorted(files)
                        if f.endswith(".py")]
    return out


def scan_python(paths: list[str], repo: str = REPO
                ) -> tuple[dict[str, list[Binding]], list[Call], dict[str, dict]]:
    """Return (bindings by symbol, call sites, alias definitions).

    An alias is a local handle on a CDLL function,
    `init_ex = getattr(self.dll, 'Vulkan_InitEx', None)`.  It records where the
    handle was built so that `init_ex(w, h, 1)` is only read as a native call in
    the file (and after the line) that created it -- `fn()` means something
    completely different in another module."""
    bindings: dict[str, list[Binding]] = {}
    calls: list[Call] = []
    aliases: dict[str, dict] = {}

    rel = lambda p: os.path.relpath(p, repo).replace("\\", "/")

    for path in paths:
        src = mask_python(read(path))
        for m in ALIAS_RE.finditer(src):
            alias = m.group(1) or m.group(4)
            obj = m.group(2) or m.group(5)
            symbol = m.group(3) or m.group(6)
            line = line_of(src, m.start())
            parent = None
            if not obj.endswith(".dll"):
                # a second hand-off, `setter = getattr(self,
                # "_set_background", None)`; the handle still names a native
                # function.
                parent = aliases.get(symbol) or aliases.get(obj.split(".")[-1])
                before = [(ln, sym) for ln, sym in
                          sorted(parent["at"].get(rel(path), []))
                          if ln <= line] if parent else []
                if not before:
                    continue
                symbol = before[-1][1]
            rec = aliases.setdefault(alias, {"symbols": set(), "at": {}})
            rec["symbols"].add(symbol)
            rec["at"].setdefault(rel(path), []).append((line, symbol))

    for path in paths:
        raw_src = read(path)
        src = mask_python(raw_src)

        # -- argtypes / restype ------------------------------------------------
        for m in BIND_RE.finditer(src):
            symbol, kind = m.group(1), m.group(2)
            eq = m.end() - 1
            i = eq + 1
            while i < len(src) and src[i] in " \t\r\n":
                i += 1
            if kind == "argtypes":
                if i >= len(src) or src[i] != "[":
                    continue
                close = find_close(src, i)
                if close < 0:
                    continue
                items = [canon_ctypes(x) for x in split_top(src[i + 1:close])]
                end = close
            else:
                end = src.find("\n", i)
                end = len(src) if end < 0 else end
                items = canon_ctypes(src[i:end].split("#")[0].strip())

            line = line_of(src, m.start())
            rec = next((b for b in bindings.setdefault(symbol, [])
                        if b.file == rel(path)), None)
            if rec is None:
                rec = Binding(symbol, rel(path), line, None, "", None, "",
                              False)
                bindings[symbol].append(rec)
            if kind == "argtypes":
                rec.argtypes, rec.argtypes_raw = items, src[i:end + 1].strip()
                rec.line = line
            else:
                rec.restype, rec.restype_raw = items, src[i:end].strip()

        # -- getattr(dll, 'Name', None) aliases that carry their own binding ---
        for m in ALIAS_RE.finditer(src):
            alias = m.group(1) or m.group(4)
            symbol = m.group(3) or m.group(6)
            for bm in re.finditer(r"(?<![\w.])" + re.escape(alias)
                                  + r"\.(argtypes|restype)\s*=", src):
                kind = bm.group(1)
                i = bm.end() - 1 + 1
                while i < len(src) and src[i] in " \t\r\n":
                    i += 1
                if kind == "argtypes":
                    if i >= len(src) or src[i] != "[":
                        continue
                    close = find_close(src, i)
                    if close < 0:
                        continue
                    items = [canon_ctypes(x) for x in split_top(src[i + 1:close])]
                    end = close
                else:
                    end = src.find("\n", i)
                    end = len(src) if end < 0 else end
                    items = canon_ctypes(src[i:end].split("#")[0].strip())
                line = line_of(src, bm.start())
                rec = next((b for b in bindings.setdefault(symbol, [])
                            if b.file == rel(path)), None)
                if rec is None:
                    rec = Binding(symbol, rel(path), line, None, "", None, "",
                                  True)
                    bindings[symbol].append(rec)
                rec.optional = True
                rec.line = line
                if kind == "argtypes":
                    rec.argtypes, rec.argtypes_raw = items, src[i:end + 1].strip()
                else:
                    rec.restype, rec.restype_raw = items, src[i:end].strip()

        # -- call sites --------------------------------------------------------
        varmap = infer_ctypes_vars(src)
        for m in CALL_RE.finditer(src):
            open_idx = m.end() - 1
            close = find_close(src, open_idx)
            if close < 0:
                continue
            calls.append(Call(m.group(1), rel(path), line_of(src, m.start()),
                              split_top(src[open_idx + 1:close]), varkinds=varmap))

    # alias call sites (`init_ex(w, h, 1)`, `fn()`, `self._set_background(r,g,b)`)
    for path in paths:
        src = mask_python(read(path))
        rel_path = rel(path)
        for alias, rec in aliases.items():
            defined = sorted(rec["at"].get(rel_path, []))
            if not defined:
                continue                       # that handle lives elsewhere
            ambiguous = len(rec["symbols"]) > 1
            varmap = infer_ctypes_vars(src)
            for m in re.finditer(r"(?<![\w.])(?:[\w.]*\.)?"
                                 + re.escape(alias) + r"\s*\(", src):
                open_idx = src.index("(", m.start(), m.end())
                close = find_close(src, open_idx)
                if close < 0:
                    continue
                line = line_of(src, m.start())
                seen = [(ln, sym) for ln, sym in defined if ln <= line]
                if not seen:
                    continue                   # before the handle existed
                best = seen[-1][0]
                symbols = sorted({sym for ln, sym in seen if ln == best})
                args = split_top(src[open_idx + 1:close])
                for sym in symbols:
                    calls.append(Call(sym, rel_path, line, args,
                                      check=not ambiguous, varkinds=varmap))

    return bindings, calls, aliases


# --------------------------------------------------------------------------
# 3. the checks
# --------------------------------------------------------------------------

@dataclass
class Finding:
    code: str
    severity: str
    symbol: str
    message: str
    file: str = ""
    line: int = 0
    hint: str = ""

    def location(self) -> str:
        return "%s:%d" % (self.file, self.line) if self.file else "-"

    def as_dict(self) -> dict:
        return {"code": self.code, "severity": self.severity,
                "symbol": self.symbol, "message": self.message,
                "location": self.location(), "hint": self.hint}


def suggested_argtypes(exp: Export) -> str:
    parts = [show(t) for t in exp.param_types]
    if not parts:
        return "self.dll.%s.argtypes = []" % exp.name
    body = ",\n    ".join(parts)
    return "self.dll.%s.argtypes = [\n    %s,\n]" % (exp.name, body)


def swapped_pairs(actual: list, wanted: list) -> tuple[list, list]:
    """Disjoint index pairs whose swap turns `actual` into `wanted`."""
    mism = [i for i in range(len(actual)) if actual[i] != wanted[i]]
    pairs, used = [], set()
    for i in mism:
        if i in used:
            continue
        for j in mism:
            if j <= i or j in used:
                continue
            if actual[i] == wanted[j] and actual[j] == wanted[i]:
                pairs.append((i, j))
                used.update((i, j))
                break
    return pairs, [i for i in mism if i not in used]


def fmt_args(types: list[str]) -> str:
    return "(" + ", ".join(show(t) for t in types) + ")"


def check(exports: dict[str, Export], bindings: dict[str, list[Binding]],
          calls: list[Call]) -> list[Finding]:
    out: list[Finding] = []
    called = {c.symbol for c in calls}

    # ---- C side: header prototype vs the compiled definitions --------------
    for name, exp in sorted(exports.items()):
        p = exp.proto
        for d in exp.defs:
            if p is None:
                continue                      # definitions only, nothing to diff
            if d.ret != p.ret:
                out.append(Finding(
                    "C_RETURN_MISMATCH", "ERROR", name,
                    "the prototype returns %s but %s defines it as %s"
                    % (p.ret, d.file, d.ret), p.file, p.line))
            if d.param_types != p.param_types:
                out.append(Finding(
                    "C_PARAM_MISMATCH", "ERROR", name,
                    "%s defines it as %s, the prototype says %s -- ctypes "
                    "sees the prototype only" % (d.file, d.text(),
                                                 fmt_args(p.param_types)),
                    p.file, p.line))
        if p is not None and not exp.defs:
            out.append(Finding(
                "C_NO_DEFINITION", "WARN", name,
                "declared %s but no definition was found under native/"
                % fmt_args(exp.param_types), p.file, p.line))

    # ---- Python side: does every export have a binding? --------------------
    for name, exp in sorted(exports.items()):
        recs = bindings.get(name, [])
        good = [b for b in recs if b.argtypes is not None]
        if not good:
            if exp.param_types:
                if name in called:
                    out.append(Finding(
                        "UNBOUND_ARGTYPES", "ERROR", name,
                        "exported as %s and called from python, but never "
                        "given an argtypes list -- ctypes will pass every "
                        "argument as an int (pointers truncated on Win64)"
                        % exp.sig.text(),
                        exp.sig.file, exp.sig.line,
                        suggested_argtypes(exp)))
                else:
                    out.append(Finding(
                        "UNBOUND_ARGTYPES", "WARN", name,
                        "exported as %s and never bound (nothing under the "
                        "scanned roots calls it either -- a test hook, or a "
                        "binding that is still missing)" % fmt_args(exp.param_types),
                        exp.sig.file, exp.sig.line,
                        suggested_argtypes(exp)))
            else:
                out.append(Finding(
                    "UNBOUND_ARGTYPES", "INFO", name,
                    "no argtypes list; harmless here, the function takes no "
                    "arguments", exp.sig.file, exp.sig.line,
                    "self.dll.%s.argtypes = []" % name))
            continue

        # conflicting declarations of the same symbol
        for other in good[1:]:
            if other.argtypes != good[0].argtypes:
                out.append(Finding(
                    "BINDING_CONFLICT", "ERROR", name,
                    "%s:%d declares %s but %s declares %s"
                    % (good[0].file, good[0].line, fmt_args(good[0].argtypes),
                       other.file, fmt_args(other.argtypes)),
                    other.file, other.line))

        for b in good:
            # arity
            if len(b.argtypes) != len(exp.param_types):
                if sorted(b.argtypes) == sorted(exp.param_types):
                    sev, code = "ERROR", "ARGTYPES_SWAPPED"
                    pairs, _unresolved = swapped_pairs(b.argtypes,
                                                      exp.param_types)
                    msg = ("%d arguments but in the wrong order: the multiset "
                           "matches the C prototype %s -- swap %s"
                           % (len(b.argtypes), fmt_args(exp.param_types),
                              ", ".join("arg%d <-> arg%d" % (i + 1, j + 1)
                                        for i, j in pairs) or "?"))
                else:
                    sev, code = "ERROR", "ARG_COUNT_MISMATCH"
                    msg = ("binds %d argument(s) but the C prototype %s takes "
                           "%d%s"
                           % (len(b.argtypes), fmt_args(exp.param_types),
                              len(exp.param_types),
                              " [%s]" % ", ".join("arg%d=%s" % (i + 1, t)
                                                  for i, t in
                                                  enumerate(b.argtypes))
                              if len(b.argtypes) < 6 else ""))
                out.append(Finding(code, sev, name, msg, b.file, b.line))
                continue

            # positional types
            mism = [i for i in range(len(b.argtypes))
                    if not compatible(b.argtypes[i], exp.param_types[i])]
            if mism:
                if sorted(b.argtypes) == sorted(exp.param_types):
                    pairs, _unresolved = swapped_pairs(b.argtypes,
                                                      exp.param_types)
                    out.append(Finding(
                        "ARGTYPES_SWAPPED", "ERROR", name,
                        "argument types are in the wrong order (a swap, not a "
                        "typo): " + ", ".join(
                            "arg%d %s -> arg%d %s"
                            % (i + 1, show(exp.param_types[i]),
                               i + 1, show(b.argtypes[i]))
                            for i in mism[:6]),
                        b.file, b.line,
                        "; ".join("positions %d and %d should exchange"
                                  % (i + 1, j + 1) for i, j in pairs)))
                else:
                    out.append(Finding(
                        "ARGTYPES_MISMATCH", "ERROR", name,
                        "; ".join(
                            "arg%d: bound %s, C wants %s (%s)"
                            % (i + 1, show(b.argtypes[i]),
                               show(exp.param_types[i]),
                               exp.param_names[i] or "?")
                            for i in mism),
                        b.file, b.line,
                        "self.dll.%s.argtypes = [%s]"
                        % (name, ", ".join(show(t)
                                           for t in exp.param_types))))

            # restype
            ret = exp.ret
            if b.restype is None:
                if ret in ("i32", "u32", "long", "ulong"):
                    out.append(Finding(
                        "UNBOUND_RESTYPE", "INFO", name,
                        "no restype; ctypes' c_int default happens to match "
                        "the C return type %s" % ret, b.file, b.line,
                        "self.dll.%s.restype = ctypes.c_int" % name))
                elif ret == "void":
                    out.append(Finding(
                        "UNBOUND_RESTYPE", "INFO", name,
                        "no restype on a void export (the garbage return value "
                        "is ignored)", b.file, b.line,
                        "self.dll.%s.restype = None" % name))
                else:
                    out.append(Finding(
                        "UNBOUND_RESTYPE", "ERROR", name,
                        "no restype, but the C function returns %s -- ctypes "
                        "will truncate it to c_int" % ret, b.file, b.line,
                        "self.dll.%s.restype = %s" % (name, show(ret))))
            elif not compatible(b.restype, ret):
                sev = "ERROR" if ret == "void" or b.restype == "void" \
                    else "WARN"
                out.append(Finding(
                    "RESTYPE_MISMATCH", sev, name,
                    "bound restype %s but the C function returns %s"
                    % (show(b.restype), ret), b.file, b.line,
                    "self.dll.%s.restype = %s" % (name, show(ret))))

    # ---- bindings that point at nothing ------------------------------------
    for name, recs in sorted(bindings.items()):
        if name in exports:
            continue
        for b in recs:
            out.append(Finding(
                "BINDING_TARGET_MISSING", "ERROR", name,
                "python binds `%s` but nothing under native/ exports it "
                "(renamed/removed export?) -- assigning .argtypes on a missing "
                "CDLL attribute silently creates a dead attribute"
                % name, b.file, b.line))

    # ---- call sites --------------------------------------------------------
    for c in calls:
        if not c.check:
            continue                          # an aliased handle, see above
        exp = exports.get(c.symbol)
        if exp is None:
            continue                      # a test stub / another library
        bound = [b for b in bindings.get(c.symbol, [])
                 if b.argtypes is not None]
        want = len(bound[0].argtypes) if bound else len(exp.param_types)
        n = len(c.args)
        star = any(a.lstrip().startswith("*") for a in c.args)
        kw = [a for a in c.args if re.match(r"^\s*\w+\s*=", a)]

        if kw:
            continue                      # keyword form: count is not positional
        if not star and n != want:
            out.append(Finding(
                "CALL_ARITY", "ERROR", c.symbol,
                "call passes %d argument(s), but the argtypes binding takes "
                "%d and the C prototype takes %d: %s"
                % (n, want, len(exp.param_types), exp.sig.text()),
                c.file, c.line))

        if star or len(c.args) != len(exp.param_types):
            continue

        # byref discipline
        for i, (a, p) in enumerate(zip(c.args, exp.param_types)):
            arg = a.strip()
            is_ptr = p.endswith("*") or p == "str"
            byref = bool(re.match(r"^(?:ctypes\.)?(?:byref|pointer|cast)\s*\(",
                                  arg))
            literal = bool(re.fullmatch(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?",
                                        arg))
            ctor = bool(re.match(r"^ctypes\.c_\w+\s*\(", arg))
            kind = c.varkinds.get(arg) if re.fullmatch(r"[A-Za-z_]\w*", arg) \
                else None
            if is_ptr and (literal or ctor):
                out.append(Finding(
                    "CALL_BYREF", "WARN", c.symbol,
                    "arg%d is %s but parameter %d (%s) is a pointer %s -- "
                    "missing ctypes.byref()/array?"
                    % (i + 1, arg, i + 1, exp.param_names[i] or "?", p),
                    c.file, c.line))
            elif is_ptr and kind == "scalar":
                out.append(Finding(
                    "CALL_BYREF", "WARN", c.symbol,
                    "arg%d passes `%s` -- a ctypes scalar instance -- where "
                    "parameter %d (%s) is the pointer %s; wrap it in "
                    "ctypes.byref(%s)"
                    % (i + 1, arg, i + 1, exp.param_names[i] or "?", p, arg),
                    c.file, c.line))
            elif not is_ptr and byref:
                out.append(Finding(
                    "CALL_BYREF", "WARN", c.symbol,
                    "arg%d passes %s but parameter %d (%s) is the scalar %s "
                    "-- byref on a by-value parameter"
                    % (i + 1, arg, i + 1, exp.param_names[i] or "?", p),
                    c.file, c.line))

        # order: the caller's variable names against the C parameter names.
        # Only a real transposition counts -- `AddPolygon(x, y, r, g, b, r, g,
        # b, ...)` repeats a colour on purpose, so "the same name shows up
        # somewhere else" proves nothing; two positions that exchanged their
        # names do.
        simple = [re.sub(r"^_+", "", a.strip()).lower()
                  if re.fullmatch(r"[A-Za-z_]\w*", a.strip()) else None
                  for a in c.args]
        raw_names = exp.param_names
        norm = [re.sub(r"^_+", "", n).lower() if n else None
                for n in raw_names]
        swaps = [(i, j) for i, s in enumerate(simple) if s and norm[i]
                 for j in range(i + 1, len(simple))
                 if simple[j] and norm[j] and simple[j] == norm[i]
                 and s == norm[j]]
        if swaps:
            i, j = swaps[0]
            full = (all(s is not None and n for s, n in zip(simple, norm))
                    and sorted(simple) == sorted(norm))
            out.append(Finding(
                "CALL_SWAPPED", "ERROR", c.symbol,
                "argument %d (`%s`) and argument %d (`%s`) are exchanged: the C "
                "prototype wants `%s` at %d and `%s` at %d%s"
                % (i + 1, c.args[i].strip(), j + 1, c.args[j].strip(),
                   raw_names[i] or "?", i + 1, raw_names[j] or "?", j + 1,
                   " (every argument name is a permutation of the C parameter "
                   "names)" if full else ""),
                c.file, c.line,
                "swap arguments %d and %d -- %s" % (i + 1, j + 1,
                                                    exp.sig.text())))

    # ---- bindings nobody uses ---------------------------------------------
    for name, recs in sorted(bindings.items()):
        if name in exports and name not in called:
            for b in recs:
                if b.argtypes is None:
                    continue
                out.append(Finding(
                    "BINDING_UNUSED", "INFO", name,
                    "bound but never called from python", b.file, b.line))

    out.sort(key=lambda f: (SEVERITIES.index(f.severity), f.file, f.line))
    return out


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def dump_contract(exports: dict[str, Export],
                  bindings: dict[str, list[Binding]],
                  calls: list[Call]) -> None:
    """The parsed contract of every export: what C says, what python bound."""
    for name, exp in sorted(exports.items()):
        rec = next((b for b in bindings.get(name, [])
                    if b.argtypes is not None), None)
        n = sum(1 for c in calls if c.symbol == name)
        print(name)
        print("    C      : %s" % exp.sig.text())
        if rec is None:
            print("    python : <no argtypes>   calls: %d" % n)
            continue
        py = ", ".join(show(t) for t in rec.argtypes) or "<empty>"
        restype = show(rec.restype) if rec.restype is not None else \
            "<ctypes default: c_int>"
        print("    python : [%s]" % py)
        print("             restype = %-20s  calls: %d  (%s:%d)"
              % (restype, n, rec.file, rec.line))
        if len(rec.argtypes) != len(exp.param_types):
            print("    ^^ %d bound vs %d in C" % (len(rec.argtypes),
                                                  len(exp.param_types)))
        else:
            bad = [i for i in range(len(exp.param_types))
                   if not compatible(rec.argtypes[i], exp.param_types[i])]
            for i in bad:
                print("    ^^ arg%d (%s): bound %s, C wants %s"
                      % (i + 1, exp.param_names[i] or "?",
                         show(rec.argtypes[i]), show(exp.param_types[i])))
    print()


# --------------------------------------------------------------------------
# self test: every detector is fired against a fixture that contains exactly
# the defect it claims to find
# --------------------------------------------------------------------------

FIX_HEADER = """#ifndef FIXTURE_H
#define FIXTURE_H
__declspec(dllexport) void DrawBar(float x, float y, int r, int g, int b, float alpha);
__declspec(dllexport) int FetchSize(int *w, int *h);
__declspec(dllexport) void NoArgs(void);
#endif
"""

FIX_IMPL = """#include "fixture.h"
__declspec(dllexport) void DrawBar(float x, float y, int r, int g, int b, float alpha) { }
__declspec(dllexport) int FetchSize(int *w, int *h) { return 1; }
__declspec(dllexport) void NoArgs(void) { }
"""

FIX_PY = '''"""fixture."""
import ctypes


class Renderer:
    def __init__(self):
        self.dll = ctypes.CDLL("fixture")
        self.dll.DrawBar.restype = None
        self.dll.DrawBar.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]
        self.dll.FetchSize.restype = ctypes.c_int
        self.dll.FetchSize.argtypes = [ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int)]
        self.dll.NoArgs.restype = None
        self.dll.NoArgs.argtypes = []

    def send(self, x, y, r, g, b, a):
        self.dll.DrawBar(x, y, r, g, b, a)

    def size(self):
        w = ctypes.c_int(0)
        h = ctypes.c_int(0)
        self.dll.FetchSize(ctypes.byref(w), ctypes.byref(h))
        return w.value, h.value
'''

# (name, expected finding code, expected severity, flat [old, new, ...]
# python mutations, flat [old, new, ...] C-implementation mutations)
BINDING_BLOCK = """        self.dll.DrawBar.argtypes = [
            ctypes.c_float, ctypes.c_float,
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float,
        ]"""

SELFTEST_CASES = [
    ("clean binding", None, None, [], []),
    ("忘绑: no argtypes at all", "UNBOUND_ARGTYPES", "ERROR",
     [("        self.dll.DrawBar.argtypes = [\n"
       "            ctypes.c_float, ctypes.c_float,\n"
       "            ctypes.c_int, ctypes.c_int, ctypes.c_int,\n"
       "            ctypes.c_float,\n        ]"), ""], []),
    ("绑反: two colour/position pairs swapped", "ARGTYPES_SWAPPED", "ERROR",
     [BINDING_BLOCK,
      ("        self.dll.DrawBar.argtypes = [\n"
       "            ctypes.c_int, ctypes.c_int,\n"
       "            ctypes.c_float, ctypes.c_float, ctypes.c_int,\n"
       "            ctypes.c_float,\n        ]")], []),
    ("忘绑: list one entry short", "ARG_COUNT_MISMATCH", "ERROR",
     [BINDING_BLOCK,
      ("        self.dll.DrawBar.argtypes = [\n"
       "            ctypes.c_float, ctypes.c_float,\n"
       "            ctypes.c_int, ctypes.c_int,\n        ]")], []),
    ("类型不符: int* bound as int", "ARGTYPES_MISMATCH", "ERROR",
     [("        self.dll.FetchSize.argtypes = [ctypes.POINTER(ctypes.c_int),\n"
       "                                       ctypes.POINTER(ctypes.c_int)]"),
      ("        self.dll.FetchSize.argtypes = [ctypes.c_int,\n"
       "                                       ctypes.POINTER(ctypes.c_int)]")], []),
    ("忘绑 restype (C 返回 int，ctypes 默认恰好一致)", "UNBOUND_RESTYPE", "INFO",
     ["        self.dll.FetchSize.restype = ctypes.c_int", ""], []),
    ("restype 与 C 返回值不符", "RESTYPE_MISMATCH", "ERROR",
     ["        self.dll.FetchSize.restype = ctypes.c_int",
      "        self.dll.FetchSize.restype = None"], []),
    ("调用点参数个数不对", "CALL_ARITY", "ERROR",
     ["        self.dll.DrawBar(x, y, r, g, b, a)",
      "        self.dll.DrawBar(x, y, r)"], []),
    ("调用点绑反: g and r exchanged", "CALL_SWAPPED", "ERROR",
     ["        self.dll.DrawBar(x, y, r, g, b, a)",
      "        self.dll.DrawBar(x, y, g, r, b, a)"], []),
    ("调用点漏 byref", "CALL_BYREF", "WARN",
     ["        self.dll.FetchSize(ctypes.byref(w), ctypes.byref(h))",
      "        self.dll.FetchSize(w, ctypes.byref(h))"], []),
    ("调用点多余 byref", "CALL_BYREF", "WARN",
     ["        self.dll.DrawBar(x, y, r, g, b, a)",
      "        self.dll.DrawBar(ctypes.byref(x), y, r, g, b, a)"], []),
    ("绑定到不存在的导出", "BINDING_TARGET_MISSING", "ERROR",
     ["        self.dll.NoArgs.argtypes = []",
      ("        self.dll.NoArgs.argtypes = []\n"
       "        self.dll.Ghost.argtypes = [ctypes.c_int]")], []),
    ("C 头文件与实现不一致", "C_PARAM_MISMATCH", "ERROR", [],
     ["__declspec(dllexport) void DrawBar(float x, float y, int r, int g, int b, float alpha) { }",
      "__declspec(dllexport) void DrawBar(float x, float y, int r, int g, float b, float alpha) { }"]),
    ("同一个符号绑了两份不一致的 argtypes", "BINDING_CONFLICT", "ERROR", [],
     []),
]


def selftest(verbose: bool = True) -> bool:
    import shutil
    import tempfile

    ok = True
    for name, code, severity, mutations, impl_mutations in SELFTEST_CASES:
        tmp = tempfile.mkdtemp(prefix="rtm-bindings-")
        try:
            os.makedirs(os.path.join(tmp, "native"))
            os.makedirs(os.path.join(tmp, "pkg"))
            impl = FIX_IMPL
            for i in range(0, len(impl_mutations), 2):
                impl = impl.replace(impl_mutations[i], impl_mutations[i + 1])
            with open(os.path.join(tmp, "native", "fixture.h"), "w",
                      encoding="utf-8") as fh:
                fh.write(FIX_HEADER)
            with open(os.path.join(tmp, "native", "fixture.c"), "w",
                      encoding="utf-8") as fh:
                fh.write(impl)

            py = FIX_PY
            for i in range(0, len(mutations), 2):
                old, new = mutations[i], mutations[i + 1]
                if old not in py:
                    raise AssertionError("fixture mutation not found: %r" % old)
                py = py.replace(old, new)
            with open(os.path.join(tmp, "pkg", "mod.py"), "w",
                      encoding="utf-8") as fh:
                fh.write(py)
            if name.startswith("同一个符号"):
                with open(os.path.join(tmp, "pkg", "other.py"), "w",
                          encoding="utf-8") as fh:
                    fh.write('import ctypes\n\n\nclass Other:\n'
                             '    def __init__(self):\n'
                             '        self.dll = ctypes.CDLL("fixture")\n'
                             '        self.dll.DrawBar.argtypes = '
                             '[ctypes.c_int, ctypes.c_int, ctypes.c_int,\n'
                             '                                     ctypes.c_int,'
                             ' ctypes.c_int, ctypes.c_int]\n')

            exports = scan_native(os.path.join(tmp, "native"), tmp)
            paths = python_roots(False, tmp, roots=["pkg"])
            bindings, calls, _ = scan_python(paths, tmp)
            findings = check(exports, bindings, calls)

            if code is None:
                bad = [f for f in findings if f.severity == "ERROR"]
                good = not bad
            else:
                good = any(f.code == code and f.severity == severity
                           for f in findings)
            ok = ok and good
            if verbose:
                print("%-4s %s" % ("PASS" if good else "FAIL", name))
                if not good:
                    for f in findings:
                        print("       %s %s %s" % (f.severity, f.code, f.message))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return ok


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Check every native DLL parameter binding.")
    ap.add_argument("--dump", action="store_true",
                    help="print the parsed contract of every export")
    ap.add_argument("--json", action="store_true", help="machine readable output")
    ap.add_argument("--only", default="", metavar="SUBSTR",
                    help="only report findings whose symbol contains SUBSTR")
    ap.add_argument("--allow", action="append", default=[], metavar="REGEX",
                    help="suppress findings for symbols matching REGEX "
                         "(repeatable), e.g. --allow '^RtmTest_'")
    ap.add_argument("--include-tests", action="store_true",
                    help="also scan tests/ and tools/ (stub DLLs live there)")
    ap.add_argument("--info", action="store_true",
                    help="include INFO level findings")
    ap.add_argument("--selftest", action="store_true",
                    help="run the checker against fixtures that contain every "
                         "defect it claims to detect")
    args = ap.parse_args(argv)

    if sys.platform == "win32":          # keep the report readable in a console
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass

    if args.selftest:
        print("check_bindings self test")
        print("-" * 78)
        ok = selftest()
        print("-" * 78)
        print("self test %s" % ("passed" if ok else "FAILED"))
        return 0 if ok else 1

    exports = scan_native()
    paths = python_roots(args.include_tests)
    bindings, calls, aliases = scan_python(paths)
    findings = check(exports, bindings, calls)
    if args.only:
        findings = [f for f in findings if args.only in f.symbol]
    for pattern in args.allow:
        findings = [f for f in findings
                    if not re.search(pattern, f.symbol)]
    if not args.info:
        findings = [f for f in findings if f.severity != "INFO"]

    if args.dump:
        dump_contract(exports, bindings, calls)

    if args.json:
        print(json.dumps({
            "exports": len(exports),
            "bindings": {k: len(v) for k, v in bindings.items()},
            "call_sites": len(calls),
            "findings": [f.as_dict() for f in findings],
        }, indent=2))
        return 1 if any(f.severity == "ERROR" for f in findings) else 0

    n_bound = sum(1 for n in exports
                  if any(b.argtypes is not None for b in bindings.get(n, [])))
    counts = {s: sum(1 for f in findings if f.severity == s)
              for s in SEVERITIES}

    print("native exports: %d   bound in python: %d   call sites: %d   "
          "alias handles: %d   files scanned: %d"
          % (len(exports), n_bound, len(calls), len(aliases), len(paths)))
    print("-" * 78)

    for f in findings:
        print("%-5s %-22s %-18s %s" % (f.severity, f.code, f.symbol,
                                       f.location()))
        print("      %s" % f.message)
        if f.hint:
            for line in f.hint.splitlines():
                print("      | %s" % line)

    print("-" * 78)
    print("errors: %d   warnings: %d   info: %d"
          % (counts["ERROR"], counts["WARN"], counts["INFO"]))
    if not findings:
        print("all native parameter bindings match the C prototypes.")
    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
