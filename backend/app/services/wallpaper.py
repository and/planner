"""Render a WeeklyPlan into a bird's-eye PNG sized for a phone wallpaper.

Pure presentation of data the planner/LLM already produced — no reasoning
happens here, it just draws the structured plan as a 7-day grid.
"""
import colorsys
import hashlib
import io
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.models.plan import WeeklyPlan

WIDTH, HEIGHT = 1080, 2280
BG_COLOR = (15, 17, 26, 255)
GRID_START_Y = 560
GRID_END_Y = 1900
MARGIN_X = 48
DAY_GAP = 8
DAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOUR_START, HOUR_END = 6, 23  # visible day window on the grid

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]

_TIME_RE = re.compile(r"(\d{1,2}):?(\d{2})?\s*-\s*(\d{1,2}):?(\d{2})?")
_INTENSITY_ALPHA = {"low": 130, "medium": 190, "high": 255}


def _font(size: int):
    for path in _FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _parse_time_range(time_range: str) -> tuple[float, float] | None:
    match = _TIME_RE.search(time_range)
    if not match:
        return None
    sh, sm, eh, em = match.groups()
    start = int(sh) + int(sm or 0) / 60
    end = int(eh) + int(em or 0) / 60
    if end <= start:
        end = start + 1  # malformed or crosses midnight — still show a sliver
    return start, end


def _day_index(day: str) -> int | None:
    normalized = day.strip().lower()
    for i, name in enumerate(DAY_ORDER):
        if normalized.startswith(name[:3]):
            return i
    return None


def _interest_color(interest_area: str) -> tuple[int, int, int]:
    digest = hashlib.md5(interest_area.lower().encode()).hexdigest()
    hue = int(digest[:4], 16) / 0xFFFF
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.95)
    return int(r * 255), int(g * 255), int(b * 255)


def render_weekly_plan_png(plan: WeeklyPlan) -> bytes:
    base = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_font = _font(56)
    day_font = _font(30)
    note_font = _font(28)

    draw.text((MARGIN_X, 60), "This Week", font=title_font, fill=(255, 255, 255, 255))

    day_width = (WIDTH - 2 * MARGIN_X - 6 * DAY_GAP) / 7
    hour_span = HOUR_END - HOUR_START
    grid_height = GRID_END_Y - GRID_START_Y

    for i, label in enumerate(DAY_LABELS):
        x = MARGIN_X + i * (day_width + DAY_GAP)
        draw.text(
            (x + day_width / 2, GRID_START_Y - 40),
            label,
            font=day_font,
            fill=(200, 200, 210, 255),
            anchor="mm",
        )
        draw.rectangle(
            [x, GRID_START_Y, x + day_width, GRID_END_Y],
            outline=(255, 255, 255, 30),
            width=1,
        )

    for block in plan.blocks:
        day_index = _day_index(block.day)
        parsed = _parse_time_range(block.time_range)
        if day_index is None or parsed is None:
            continue
        start, end = parsed
        start = max(start, HOUR_START)
        end = min(end, HOUR_END)
        if end <= start:
            continue

        x = MARGIN_X + day_index * (day_width + DAY_GAP)
        y0 = GRID_START_Y + (start - HOUR_START) / hour_span * grid_height
        y1 = GRID_START_Y + (end - HOUR_START) / hour_span * grid_height

        r, g, b = _interest_color(block.interest_area)
        alpha = _INTENSITY_ALPHA.get(block.intensity, 190)
        draw.rounded_rectangle(
            [x + 4, y0 + 2, x + day_width - 4, max(y1 - 2, y0 + 14)],
            radius=8,
            fill=(r, g, b, alpha),
        )

    notes = f"{plan.week_summary}\n\n{plan.burnout_risk_notes}".strip()
    wrapped = textwrap.wrap(notes, width=46)[:6]
    ny = GRID_END_Y + 50
    for line in wrapped:
        draw.text((MARGIN_X, ny), line, font=note_font, fill=(210, 210, 220, 230))
        ny += 38

    composed = Image.alpha_composite(base, overlay).convert("RGB")
    buf = io.BytesIO()
    composed.save(buf, format="PNG")
    return buf.getvalue()
