import re

def clean_essay_text(raw_text: str) -> str:
    # 1. Remove non-ASCII characters (e.g., Arabic letters at the end)
    text = raw_text.encode("ascii", errors="ignore").decode()

    # 2. Merge hyphenated line-break words (e.g., "wear-\ning" → "wearing")
    text = re.sub(r'-\n', '', text)

    # 3. Replace newlines within text with a space
    text = re.sub(r'\n+', ' ', text)

    # 4. Collapse multiple spaces into one
    text = re.sub(r'\s{2,}', ' ', text)

    # 5. Optional: strip leading/trailing whitespace
    text = text.strip()

    return text
