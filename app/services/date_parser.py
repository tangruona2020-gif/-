import re
from datetime import date


def parse_date_range(text: str) -> tuple[date | None, date | None]:
    found = re.findall(r"(20\d{2})[年/.\-](\d{1,2})[月/.\-](\d{1,2})日?", text)
    dates = []
    for y, m, d in found:
        try:
            dates.append(date(int(y), int(m), int(d)))
        except ValueError:
            pass
    return (dates[0] if dates else None, dates[1] if len(dates) > 1 else None)
