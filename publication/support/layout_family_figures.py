"""Reflow the archived S5–S7 vector figures into one page per preparation."""
import argparse
from collections import Counter
from pathlib import Path

import fitz

FIGURES = (
    "p07_support_constitution_families.pdf",
    "p07_support_interface_families.pdf",
    "p07_support_L_removal_families.pdf",
)
TITLE = fitz.Rect(220, 6, 500, 31)
PANEL_COLUMNS = (fitz.Rect(4, 48, 307, 628), fitz.Rect(308, 48, 612, 628))
SCALE = fitz.Rect(627, 139, 703, 514)


def placed(page, original, clip, origin):
    x, y = origin
    destination = fitz.Rect(x, y, x + clip.width, y + clip.height)
    page.show_pdf_page(destination, original, 0, clip=clip)
    return destination


def words(page, rect=None):
    return Counter(word[4] for word in page.get_text("words", clip=rect))


def reflow(source, output):
    with fitz.open(source) as original, fitz.open() as result:
        source_page = original[0]
        expected = words(source_page, TITLE) + words(source_page, SCALE)
        for panel in PANEL_COLUMNS:
            expected.update(words(source_page, panel))
        if expected != words(source_page):
            raise ValueError(f"Clipping would omit or duplicate visible text in {source}")
        for panel in PANEL_COLUMNS:
            page = result.new_page(width=400, height=605)
            placed(page, original, TITLE, (60, 0))
            placed(page, original, panel, (0, 25))
            placed(page, original, SCALE, (319, 132))
            if words(page) != words(source_page, TITLE) + words(source_page, panel) + words(source_page, SCALE):
                raise ValueError(f"Visible text changed during reflow of {source}")
        result.set_metadata({"title": source_page.parent.metadata.get("title", "") or source.stem})
        result.save(output, garbage=4, deflate=True, no_new_id=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    for name in FIGURES:
        reflow(args.source_directory / name, args.output_directory / name)
        print(f"PASS: {name}, all original vector labels and values retained")
