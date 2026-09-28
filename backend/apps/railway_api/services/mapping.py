API_TO_CANONICAL = {
    "VSH": "VASHI",
    "NEU": "NERUL",
    "KHAG": "KHARGHAR",
    "GNSL": "GHANSOLI",
    "SWDK": "SEAWOODSDARAWE",
    "BAP": "BAP",
    "PNVL": "PNVL",
    "TNA": "TNA"
}

CANONICAL_TO_API = {
    "VASHI": "VSH",
    "NERUL": "NEU",
    "KHARGHAR": "KHAG",
    "GHANSOLI": "GNSL",
    "SEAWOODSDARAWE": "SWDK",
    "BAP": "BAP",
    "PNVL": "PNVL",
    "TNA": "TNA"
}

def to_canonical_station(code):
    if not code: return code
    return API_TO_CANONICAL.get(code.upper(), code.upper())

def to_api_station(code):
    if not code: return code
    return CANONICAL_TO_API.get(code.upper(), code.upper())
