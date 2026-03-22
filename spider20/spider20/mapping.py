# mapping.py

# The keys match your website's category slugs exactly.
PRODUCT_MAPPING = {
    "t-shirt": ("t-shirt", "tee", "top", "tank", "v-neck", "u-shaped", "square neck", "short sleeve", "long sleeve", "halter", "baby tee", "boat neck", "one shoulder", "off shoulder", "cami", "u-shaped"),
    "sweatshirt": ("sweatshirt", "crewneck", "quarter zip", "zip up", "zip-up", "zipper", "comfort+", "mock neck"),
    "hoodie": ("hoodie", "hooded", "blanket hoodie"),
    "sweater": ("knit", "pullover", "cardigan", "sweater", "jumper"),
    "coat": ("jacket", "sculpt jacket", "coat", "bomber", "puffer", "blazer", "shacket"),
    "pants": ("pants", "sweatpants", "joggers", "trousers", "flared pants", "yoga pants", "elastic hem"),
    "jeans": ("jeans", "denim", "baggy", "flare jeans", "straight leg", "high waist", "high rise"),
    "leggings": ("leggings", "tights", "sculpt leggings"),
    "shorts": ("shorts", "denim shorts", "swimwear", "bermuda"),
    "dress": ("dress", "maxi", "mini dress", "skirt"), # Skirt added here or as own category
    "pyjama": ("set", "spaghetti strap set", "button up set", "piped set", "satin", "nightwear", "loungewear"),
    "accessories": ("bag", "belt", "hat", "cap", "scarf", "socks"),
    "shoes": ("footwear", "sneakers", "boots", "shoes", "slides"),
    "sportswear": ("move", "sculpt", "crossover", "activewear")
}

def classify_product(title):
    if not title:
        return "uncategorized"
    
    name_clean = title.lower()

    # --- PHASE 1: HIGH-PRIORITY PHRASES ---
    # We check these first because they often contain keywords from other categories.
    
    if "set" in name_clean:
        return "pyjama"  # Prevents 'Pants Set' from being just 'Pants'
        
    if "jacket" in name_clean or "sculpt jacket" in name_clean:
        return "coat"    # Prevents 'Zip Up Jacket' from being 'Sweatshirt'
        
    if "jeans" in name_clean or "baggy" in name_clean:
        return "jeans"   # Catches "Baggy Men's Jeans" accurately
        
    if "hoodie" in name_clean:
        return "hoodie"  # Catches "Blanket Hoodie" or "Comfort+ Hoodie"

    # --- PHASE 2: GENERAL KEYWORD MATCHING ---
    for category, keywords in PRODUCT_MAPPING.items():
        if any(word in name_clean for word in keywords):
            return category
            
    return "uncategorized"