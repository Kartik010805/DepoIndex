import json


with open("data/lines.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)


cases = [
    ("Topics 2 and 3", 11, 2, 14, 12),
    ("Topics 14 and 15", 27, 1, 31, 20),
    ("Topics 16 and 17", 31, 21, 35, 8),
    ("Topics 18 and 19", 35, 11, 37, 1),
    ("Topics 20 and 21", 37, 23, 42, 4),
    ("Topics 28 and 29", 55, 14, 60, 1),
]


def location_key(page, line):
    return page * 1000 + line


for name, start_page, start_line, end_page, end_line in cases:

    start = location_key(start_page, start_line)
    end = location_key(end_page, end_line)

    print("\n" + "=" * 100)
    print(name)
    print(f"Range: {start_page}:{start_line} -> {end_page}:{end_line}")
    print("=" * 100)

    for item in transcript:
        current = location_key(item["page"], item["line"])

        if start <= current <= end:
            print(
                f"[{item['page']}:{item['line']}] "
                f"{item['text']}"
            )