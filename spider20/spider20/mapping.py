# The keys match your website's category slugs exactly.
PRODUCT_MAPPING = {
    "t-shirt": ("t-shirt", "tee", "top", "tank", "v-neck", "u-shaped", "square neck", "short sleeve", "long sleeve", "halter", "baby tee", "boat neck", "one shoulder", "off shoulder", "cami", "u-shaped", "round neck"),
    "sweatshirt": ("sweatshirt", "crew neck", "crewneck", "quarter zip", "quarter-zip", "half-zip", "half zip", "zip up", "zip-up", "zipper", "comfort+", "mock neck"),
    "hoodie": ("hoodie", "hooded", "blanket hoodie"),
    "sweater": ("knit", "knitted", "pullover", "cardigan", "sweater", "jumper"),
    "coat": ("jacket", "sculpt jacket", "coat", "bomber", "puffer", "blazer", "shacket"),
    "pants": ("pants", "sweatpants", "joggers", "trousers", "flared pants", "yoga pants", "elastic hem", "track pants"),
    "jeans": ("jeans", "denim", "baggy", "flare jeans", "straight leg", "high waist", "high rise", "balloon denim"),
    "leggings": ("leggings", "tights", "sculpt leggings"),
    "shorts": ("shorts", "denim shorts", "swimwear", "bermuda"),
    "dress": ("dress", "maxi", "mini dress", "skirt"), 
    "pyjama": ("set", "spaghetti strap set", "button up set", "piped set", "satin", "nightwear", "loungewear"),
    "accessories": ("bag", "belt", "hat", "cap", "scarf", "socks"),
    "shoes": ("footwear", "sneakers", "boots", "shoes", "slides"),
    "sportswear": ("move", "sculpt", "crossover", "activewear")
}

def classify_product(title):
    if not title:
        return "uncategorized"
    
    name_clean = title.lower()

    # --- PHASE 1: HIGH-PRIORITY PHRASES (Specific Overrides) ---
    
    # Check for Denim/Jeans first so "Denim Jacket" doesn't get lost, 
    # though we prioritize Jacket for "Denim Jacket" specifically.
    if "jacket" in name_clean:
        return "coat"
        
    if "hoodie" in name_clean:
        return "hoodie"
        
    if "jeans" in name_clean or "denim" in name_clean or "baggy" in name_clean:
        return "jeans"

    if "set" in name_clean:
        return "pyjama"

    # Distinction: If it says 'Knit' or 'Sweater' it's usually the Sweater category, 
    # even if it's a 'Knit Hoodie' or 'Knit Crewneck'.
    if "knit" in name_clean or "sweater" in name_clean:
        return "sweater"

    # --- PHASE 2: GENERAL KEYWORD MATCHING ---
    for category, keywords in PRODUCT_MAPPING.items():
        if any(word in name_clean for word in keywords):
            return category
            
    return "uncategorized"