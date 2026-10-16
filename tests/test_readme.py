from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"


def test_readme_exists():
    assert README.is_file()


def test_readme_has_expected_sections():
    content = README.read_text(encoding="utf-8")
    for heading in ("# orderbook-sim", "## Projektidee", "## Struktur", "## Beispiele"):
        assert heading in content
