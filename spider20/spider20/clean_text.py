import unicodedata

def clean_text(text):
    if not text:
        return ""
    # 1. Normalize unicode (handles combined characters like accents)
    text = unicodedata.normalize('NFKC', text)
    text = text.replace('\u2013', '-')
    
    # 2. Keep only printable characters
    # 'C' = Control/Format/Invisible, 'Z' = Separator (we keep 'Zs' which is normal space)
    cleaned = "".join(
        ch for ch in text 
        if unicodedata.category(ch)[0] != 'C' 
        and (unicodedata.category(ch) == 'Zs' or not unicodedata.category(ch).startswith('Z'))
    )
    
    # 3. Clean up any resulting double spaces or leading/trailing junk
    return " ".join(cleaned.split())

# Usage in your parse method:
