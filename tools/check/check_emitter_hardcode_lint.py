"""
emitter 責務違反チェッカー（P6-EMITTER-LINT）

src/toolchain2/emit/*/ 配下の .py ファイルを対象に、禁止パターンを grep して
言語 × カテゴリのマトリクスを stdout に出力する。

exit code は常に 0（違反があっても fail しない。結果はレポートのみ）。

使い方:
    python3 tools/check/check_emitter_hardcode_lint.py
    python3 tools/check/check_emitter_hardcode_lint.py --verbose
    python3 tools/check/check_emitter_hardcode_lint.py --lang go
    python3 tools/check/check_emitter_hardcode_lint.py --category module_name
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EMIT_DIR = ROOT / "src" / "toolchain2" / "emit"

# ---------------------------------------------------------------------------
# 検出カテゴリ定義
# ---------------------------------------------------------------------------

CATEGORIES: dict[str, list[str]] = {
    "module_name": [
        # emitter が runtime_module_id ではなくモジュール名を文字列で知っている
        r'"math"',
        r'"pathlib"',
        r'"json"',
        r'"sys"',
        r'"os"',
        r'"glob"',
        r'"time"',
        r'"subprocess"',
        r'"re"',
        r'"argparse"',
    ],
    "runtime_symbol": [
        # emitter が runtime_call / runtime_symbol ではなく関数名を直接知っている
        r'"perf_counter"',
        r'"py_len"',
        r'"py_print"',
        r'"py_range"',
        r'"write_rgb_png"',
        r'"save_gif"',
        r'"grayscale_palette"',
    ],
    "target_constant": [
        # mapping.json の calls テーブルの責務を emitter が横取りしている
        r'"M_PI"',
        r'"M_E"',
        r'"std::sqrt"',
        r'"std::stoll"',
        r'"math\.Sqrt"',
        r'"Math\.PI"',
    ],
    "prefix_match": [
        # runtime_call_adapter_kind で判定すべきところをプレフィックスで分岐
        r'"pytra\.std\."',
        r'"pytra\.core\."',
        r'"pytra\.built_in\."',
    ],
    "class_name": [
        # EAST3 の型情報から来るべき判定を emitter がクラス名で分岐
        r'"Path"',
        r'"ArgumentParser"',
        r'"Exception"',
    ],
    "python_syntax": [
        # EAST3 では既に正規化済みの Python 構文が emitter に残っている
        r'"__main__"',
        r'"super\(\)"',
    ],
}

CATEGORY_LABELS: dict[str, str] = {
    "module_name":    "module name   ",
    "runtime_symbol": "runtime symbol",
    "target_constant":"target const  ",
    "prefix_match":   "prefix match  ",
    "class_name":     "class name    ",
    "python_syntax":  "Python syntax ",
}


# ---------------------------------------------------------------------------
# Hit = (lang, category, file, lineno, line)
# ---------------------------------------------------------------------------

def collect_hits(
    filter_lang: str | None,
    filter_cat: str | None,
) -> list[tuple[str, str, Path, int, str]]:
    hits: list[tuple[str, str, Path, int, str]] = []

    files = sorted(
        f for f in EMIT_DIR.rglob("*.py")
        if "__pycache__" not in str(f) and f.name != "__init__.py"
    )

    for fpath in files:
        # ファイルの言語を parts から取得（emit/<lang>/...）
        rel = fpath.relative_to(EMIT_DIR)
        lang = rel.parts[0] if len(rel.parts) > 1 else "common"

        if filter_lang and lang != filter_lang:
            continue

        lines = fpath.read_text(encoding="utf-8").splitlines()
        for lineno, raw in enumerate(lines, 1):
            stripped = raw.strip()
            # コメント行はスキップ
            if stripped.startswith("#"):
                continue
            # docstring の先頭行（""" で始まる）はスキップ
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue

            for cat, patterns in CATEGORIES.items():
                if filter_cat and cat != filter_cat:
                    continue
                for pat in patterns:
                    if re.search(pat, raw):
                        hits.append((lang, cat, fpath, lineno, stripped[:120]))
                        break  # 1行につき同カテゴリの重複カウントを避ける

    return hits


# ---------------------------------------------------------------------------
# 出力
# ---------------------------------------------------------------------------

def build_matrix(
    hits: list[tuple[str, str, Path, int, str]],
    langs: list[str],
) -> dict[str, dict[str, int]]:
    mat: dict[str, dict[str, int]] = {
        cat: {lang: 0 for lang in langs}
        for cat in CATEGORIES
    }
    for lang, cat, _f, _ln, _line in hits:
        if lang in mat[cat]:
            mat[cat][lang] += 1
    return mat


def print_matrix(mat: dict[str, dict[str, int]], langs: list[str]) -> None:
    header = "| カテゴリ           | " + " | ".join(f"{l:<6}" for l in langs) + " |"
    sep    = "|" + "-" * (len(header) - 2) + "|"
    print(header)
    print(sep)
    for cat, label in CATEGORY_LABELS.items():
        row_counts = mat[cat]
        cells = []
        for l in langs:
            n = row_counts[l]
            cells.append(f"{'🟥' + str(n) if n else '🟩0':<6}")
        print(f"| {label} | " + " | ".join(cells) + " |")


def print_verbose(
    hits: list[tuple[str, str, Path, int, str]],
    langs: list[str],
) -> None:
    from itertools import groupby
    key = lambda h: (h[1], h[0])
    for (cat, lang), group in groupby(sorted(hits, key=key), key=key):
        entries = list(group)
        print(f"\n  [{cat}] {lang} ({len(entries)} 件)")
        for _lang, _cat, fpath, lineno, line in entries:
            rel = fpath.relative_to(ROOT)
            print(f"    {rel}:{lineno}: {line}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="emitter 責務違反チェッカー")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="違反箇所を詳細表示する")
    parser.add_argument("--lang", default=None,
                        help="対象言語を絞り込む（例: go, cpp, rs, ts）")
    parser.add_argument("--category", default=None,
                        help="対象カテゴリを絞り込む（例: module_name）")
    args = parser.parse_args()

    hits = collect_hits(args.lang, args.category)

    # 対象言語一覧（common 含む）
    all_langs = sorted(set(h[0] for h in hits) | {
        p.name for p in EMIT_DIR.iterdir()
        if p.is_dir() and p.name not in ("__pycache__", "profiles")
    })
    if args.lang:
        all_langs = [l for l in all_langs if l == args.lang]

    total = len(hits)
    print(f"\n=== emitter hardcode lint — {total} 件の違反 ===\n")

    mat = build_matrix(hits, all_langs)
    print_matrix(mat, all_langs)

    if args.verbose and hits:
        print("\n--- 詳細 ---")
        print_verbose(hits, all_langs)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
