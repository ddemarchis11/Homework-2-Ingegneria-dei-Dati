import os, json, re, tiktoken, html  # type: ignore

INPUT_FOLDER = "speech_dataset"
OUTPUT_FOLDER = "to_index_dataset"
CHUNK_SIZE = 10_000
OVERLAP = 1_000

enc = tiktoken.get_encoding("cl100k_base")
encode, decode = enc.encode, enc.decode
approx = False

def clean_name(s: str) -> str:
    s = re.sub(r'[\\/*?:"<>|,]', "", s or "")
    return re.sub(r"\s+", " ", s).strip()

def strip_html(s: str) -> str:
    if not s: return ""
    s = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1\s*>", "", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</p\s*>", "\n\n", s)
    s = re.sub(r"(?is)<p\b[^>]*>", "", s)
    s = re.sub(r"(?s)<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def chunk_tokens(tokens, size, overlap):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Chunk parameters not valid.")
    stride = size - overlap
    return [tokens[i:i+size] for i in range(0, len(tokens), stride)]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def build_dataset() -> list:
    tokens_per_file = []

    for fn in os.listdir(INPUT_FOLDER):
        if not fn.lower().endswith(".txt"):
            continue

        in_path = os.path.join(INPUT_FOLDER, fn)
        try:
            with open(in_path, "r", encoding="utf-8") as f:
                raw_text = f.read().strip()
        except Exception as e:
            print(f"Error reading{fn}: {e}")
            continue

        if not raw_text:
            print(f"No text in {fn}, skip.")
            continue

        base_title = os.path.splitext(fn)[0]
        title = clean_name(base_title)

        text = strip_html(raw_text)
        if not text:
            print(f"No text after HTML clean {fn}, skip.")
            continue

        toks = encode(text)
        if not toks:
            print(f"No token in {fn} after cleaning, skip.")
            continue

        chunks = chunk_tokens(toks, CHUNK_SIZE, OVERLAP)
        tokens_per_file.append(len(toks))

        base_for_filename = re.sub(r"\s+", " ", title)
        for i, tok_chunk in enumerate(chunks, 1):
            out_name = f"{base_for_filename}_chunk{i:02d}.json"
            out_name = clean_name(out_name)
            out_path = os.path.join(OUTPUT_FOLDER, out_name)

            obj = {
                "title": title,       
                "content": decode(tok_chunk)
            }
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(obj, f, ensure_ascii=False)
                print(f"Saved {out_name} ({len(tok_chunk)} token{' ~' if approx else ''})")
            except Exception as e:
                print(f"Error writing {out_name}: {e}")

    return tokens_per_file

if __name__ == "__main__":
    build_dataset()