import json

INPUT_PATH = "data/lines.json"
METADATA_PATH = "data/metadata.json"
OUTPUT_PATH = "data/chunks.json"

CHUNK_SIZE = 100
OVERLAP = 20


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_chunks(lines, metadata):
    chunks = []
    step = CHUNK_SIZE - OVERLAP

    for start in range(0, len(lines), step):
        chunk_lines = lines[start:start + CHUNK_SIZE]

        if not chunk_lines:
            break

        chunks.append({
            "chunk_id": len(chunks) + 1,
            "start_index": start,
            "end_index": start + len(chunk_lines) - 1,
            "start_page": chunk_lines[0]["page"],
            "start_line": chunk_lines[0]["line"],
            "end_page": chunk_lines[-1]["page"],
            "end_line": chunk_lines[-1]["line"],
            "metadata": metadata,
            "lines": chunk_lines
        })

        if start + CHUNK_SIZE >= len(lines):
            break

    return chunks


def main():
    lines = load_json(INPUT_PATH)
    metadata = load_json(METADATA_PATH)

    chunks = build_chunks(lines, metadata)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Created {len(chunks)} chunks.")
    print(f"Chunk size: {CHUNK_SIZE} lines")
    print(f"Overlap: {OVERLAP} lines")
    print(f"Metadata propagated: {len(chunks)} chunks")
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
