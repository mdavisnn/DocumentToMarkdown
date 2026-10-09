# Document to Markdown

A small developer CLI that recursively finds supported documents and converts
them to Markdown using
[Microsoft MarkItDown](https://github.com/microsoft/markitdown).

The generated files are written to a `markdown_output` folder by default.
The input folder structure is preserved, and existing Markdown files are
skipped unless `--overwrite` is supplied.

Each source folder also receives a `conversion_log.csv` file. Successful
conversions are appended with the source file's relative name, original format,
and conversion date. Existing log entries are preserved on later runs.

## Supported files

- PDF
- Word (`.docx`)
- PowerPoint (`.pptx`)
- Excel (`.xlsx` and `.xls`)
- HTML
- CSV
- JSON
- XML
- EPUB
- Outlook messages (`.msg`)
- Plain text

## Setup

From PowerShell:

```powershell
cd "D:\Data Lab\DocumentToMarkdown"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If MarkItDown is already installed in the active environment, you can run the
script immediately without installing the project.

## Usage

```powershell
python .\convert_folder.py "D:\Data Lab\DocumentLibrary"
```

After installing the project, the shorter command is also available:

```powershell
documents-to-markdown "C:\path\to\documents"
```

By default, a file such as:

```text
C:\path\to\documents\reports\status.pdf
```

becomes:

```text
C:\path\to\documents\markdown_output\reports\status.md
```

Use a different output folder:

```powershell
python .\convert_folder.py "C:\path\to\documents" --output "C:\temp\markdown"
```

Replace files that have already been converted:

```powershell
python .\convert_folder.py "C:\path\to\documents" --overwrite
```

Show all options:

```powershell
python .\convert_folder.py --help
```

## Tests

```powershell
python -m pytest
```
