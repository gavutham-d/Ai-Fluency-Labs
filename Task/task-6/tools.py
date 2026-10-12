"""Two small gardening tools and the schemas shared with the model and validator."""
PLANT_CARE = {
    "basil": {
        "spring": "Water when the top 2 cm of soil feels dry; give bright light.",
        "summer": "Check soil daily and water when the top 2 cm feels dry; give bright light.",
        "autumn": "Water when the top 2 cm of soil feels dry; give bright light.",
        "winter": "Water sparingly when the top 2 cm is dry; keep in a bright, warm spot.",
    },
    "tomato": {
        "spring": "Keep soil evenly moist and provide at least 6 hours of sun.",
        "summer": "Check soil daily, keep it evenly moist, and provide at least 6 hours of sun.",
        "autumn": "Keep soil evenly moist and provide at least 6 hours of sun while fruit ripens.",
        "winter": "Protect from cold; water only when the top 2 cm of soil feels dry.",
    },
    "mint": {
        "spring": "Keep soil lightly moist and provide bright indirect light.",
        "summer": "Check soil often, keep it lightly moist, and provide bright indirect light.",
        "autumn": "Keep soil lightly moist and provide bright indirect light.",
        "winter": "Water less often, keeping soil just slightly moist.",
    },
}

PLANTS = list(PLANT_CARE)
SEASONS = ["spring", "summer", "autumn", "winter"]

SCHEMAS = {
    "lookup_plant_care": {
        "type": "object",
        "properties": {
            "plant": {"type": "string", "enum": PLANTS},
            "season": {"type": "string", "enum": SEASONS},
        },
        "required": ["plant", "season"],
        "additionalProperties": False,
    },
    "calculate_watering_volume": {
        "type": "object",
        "properties": {
            "plant": {"type": "string", "enum": PLANTS},
            "pot_size_liters": {"type": "number", "minimum": 0.1, "maximum": 100},
        },
        "required": ["plant", "pot_size_liters"],
        "additionalProperties": False,
    },
}


def lookup_plant_care(plant: str, season: str) -> str:
    """Look up a simple seasonal care note for a supported plant."""
    return PLANT_CARE[plant][season]


def calculate_watering_volume(plant: str, pot_size_liters: float) -> str:
    """Estimate one watering amount at 75 mL per litre of pot capacity."""
    volume_ml = round(pot_size_liters * 75)
    return f"For a {pot_size_liters:g} L pot, use about {volume_ml} mL per watering; check soil moisture first."


TOOL_FUNCTIONS = {
    "lookup_plant_care": lookup_plant_care,
    "calculate_watering_volume": calculate_watering_volume,
}

TOOLS = [
    {"type": "function", "function": {
        "name": name,
        "description": (
            "Look up seasonal care advice for one supported houseplant."
            if name == "lookup_plant_care"
            else "Estimate water per watering from plant and pot capacity; soil moisture still takes priority."
        ),
        "parameters": schema,
    }}
    for name, schema in SCHEMAS.items()
]
