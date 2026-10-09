import csv
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from convert_folder import convert_folder


class FakeConverter:
    def __init__(self) -> None:
        self.converted: list[Path] = []

    def convert_local(self, path: Path):
        self.converted.append(path)
        return SimpleNamespace(markdown=f"# Converted\n\n{path.name}\n")


def test_converts_recursively_and_preserves_folders(tmp_path: Path) -> None:
    source = tmp_path / "documents"
    nested = source / "nested"
    nested.mkdir(parents=True)
    (source / "report.pdf").write_bytes(b"fake pdf")
    (nested / "workbook.xlsx").write_bytes(b"fake workbook")
    (nested / "ignored.py").write_text("print('ignored')", encoding="utf-8")

    converter = FakeConverter()
    summary = convert_folder(source, converter=converter)

    assert summary.converted == 2
    assert summary.skipped == 0
    assert summary.failed == 0
    assert (source / "markdown_output" / "report.md").read_text(
        encoding="utf-8"
    ).endswith("report.pdf\n")
    assert (
        source / "markdown_output" / "nested" / "workbook.md"
    ).exists()

    with (source / "conversion_log.csv").open(
        encoding="utf-8", newline=""
    ) as log_file:
        rows = list(csv.DictReader(log_file))

    assert rows == [
        {
            "file_name": "nested/workbook.xlsx",
            "original_format": "xlsx",
            "conversion_date": date.today().isoformat(),
        },
        {
            "file_name": "report.pdf",
            "original_format": "pdf",
            "conversion_date": date.today().isoformat(),
        },
    ]


def test_skips_existing_output_by_default(tmp_path: Path) -> None:
    source = tmp_path / "documents"
    output = source / "markdown_output"
    source.mkdir()
    output.mkdir()
    (source / "report.pdf").write_bytes(b"fake pdf")
    destination = output / "report.md"
    destination.write_text("keep me", encoding="utf-8")

    summary = convert_folder(source, converter=FakeConverter())

    assert summary.converted == 0
    assert summary.skipped == 1
    assert destination.read_text(encoding="utf-8") == "keep me"


def test_overwrite_replaces_existing_output(tmp_path: Path) -> None:
    source = tmp_path / "documents"
    output = source / "markdown_output"
    source.mkdir()
    output.mkdir()
    (source / "report.pdf").write_bytes(b"fake pdf")
    destination = output / "report.md"
    destination.write_text("old", encoding="utf-8")

    summary = convert_folder(
        source,
        overwrite=True,
        converter=FakeConverter(),
    )

    assert summary.converted == 1
    assert summary.skipped == 0
    assert destination.read_text(encoding="utf-8").startswith("# Converted")


def test_appends_to_existing_log_without_converting_it(tmp_path: Path) -> None:
    source = tmp_path / "documents"
    source.mkdir()
    (source / "first.pdf").write_bytes(b"fake pdf")

    converter = FakeConverter()
    convert_folder(source, converter=converter)
    (source / "second.docx").write_bytes(b"fake docx")
    convert_folder(source, converter=converter)

    with (source / "conversion_log.csv").open(
        encoding="utf-8", newline=""
    ) as log_file:
        rows = list(csv.DictReader(log_file))

    assert [row["file_name"] for row in rows] == ["first.pdf", "second.docx"]
    assert [path.name for path in converter.converted] == [
        "first.pdf",
        "second.docx",
    ]


def test_creates_empty_log_when_nothing_is_converted(tmp_path: Path) -> None:
    source = tmp_path / "documents"
    source.mkdir()

    summary = convert_folder(source, converter=FakeConverter())

    assert summary.converted == 0
    assert (source / "conversion_log.csv").read_text(encoding="utf-8").splitlines() == [
        "file_name,original_format,conversion_date"
    ]
