"""Convert supported documents in a folder to Markdown using MarkItDown."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from markitdown import MarkItDown


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".docx",
    ".epub",
    ".htm",
    ".html",
    ".json",
    ".msg",
    ".pdf",
    ".pptx",
    ".txt",
    ".xls",
    ".xlsx",
    ".xml",
}


class Converter(Protocol):
    def convert_local(self, path: Path): ...


@dataclass
class ConversionSummary:
    converted: int = 0
    skipped: int = 0
    failed: int = 0


def is_within(path: Path, directory: Path) -> bool:
    """Return whether path is inside directory."""
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def find_documents(source: Path, output: Path) -> list[Path]:
    """Find supported files recursively, excluding the generated output."""
    return sorted(
        path
        for path in source.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and not is_within(path.resolve(), output)
    )


def convert_folder(
    source: Path,
    output: Path | None = None,
    *,
    overwrite: bool = False,
    converter: Converter | None = None,
) -> ConversionSummary:
    """Convert supported documents under source and return conversion counts."""
    source = source.expanduser().resolve()
    if not source.is_dir():
        raise NotADirectoryError(f"Source folder does not exist: {source}")

    output = (
        output.expanduser().resolve()
        if output is not None
        else source / "markdown_output"
    )
    converter = converter or MarkItDown()
    summary = ConversionSummary()

    for document in find_documents(source, output):
        relative_path = document.relative_to(source)
        destination = (output / relative_path).with_suffix(".md")

        if destination.exists() and not overwrite:
            print(f"[skipped]   {relative_path} (output already exists)")
            summary.skipped += 1
            continue

        try:
            result = converter.convert_local(document)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(result.markdown, encoding="utf-8")
        except Exception as exc:
            print(f"[failed]    {relative_path}: {exc}")
            summary.failed += 1
            continue

        print(f"[converted] {relative_path} -> {destination.relative_to(output)}")
        summary.converted += 1

    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Recursively convert supported documents in a folder to Markdown."
        )
    )
    parser.add_argument("source", type=Path, help="Folder containing documents")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output folder (default: SOURCE/markdown_output)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace Markdown files that already exist",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        summary = convert_folder(
            args.source,
            args.output,
            overwrite=args.overwrite,
        )
    except NotADirectoryError as exc:
        print(f"Error: {exc}")
        return 2

    print(
        "\nFinished: "
        f"{summary.converted} converted, "
        f"{summary.skipped} skipped, "
        f"{summary.failed} failed."
    )
    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
