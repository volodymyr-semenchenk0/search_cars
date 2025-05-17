def normalize_filters(data: dict) -> dict:
    def clean(key, lower=False, dashify=False):
        v = data.get(key, "").strip()
        if not v:
            return None
        if lower:
            v = v.lower()
        if dashify:
            v = v.replace(" ", "-")
        return v

    return {
        "make": clean("make", lower=True, dashify=True),
        "model": clean("model", lower=True, dashify=True),
        "pricefrom": clean("pricefrom"),
        "priceto": clean("priceto"),
        "fregfrom": clean("fregfrom"),
        "fregto": clean("fregto"),
        "kmfrom": clean("kmfrom"),
        "kmto": clean("kmto"),
        "cy": clean("cy"),
        "fuel": clean("fuel"),
    }
