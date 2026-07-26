"""Generate a placeholder discharge-summary image for M0 pipeline testing.

Not real handwriting -- just proves the Digitise -> extract plumbing end to end,
and exercises the refusal path via one deliberately illegible line. Swap for
real redacted photographed summaries as soon as they're available.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path(__file__).resolve().parents[2] / "resources" / "test_docs" / "synthetic_discharge_summary.png"

LINES = [
    "CITY CARE MULTISPECIALITY HOSPITAL",
    "Discharge Summary",
    "",
    "Patient Name: Rekha Suresh Patil",
    "Admit Date: 03-06-2026    Discharge Date: 07-06-2026",
    "Room Category: Twin Sharing    Room Rent/Day: Rs. 3500",
    "",
    "Diagnosis: /////// [illegible smudge] ///////",
    "Procedure: Laparoscopic Cholecystectomy",
    "",
    "Total Bill Amount: Rs. 72,000",
]


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (900, 500), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    y = 20
    for line in LINES:
        draw.text((30, y), line, fill="black", font=font)
        y += 35

    img.save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
