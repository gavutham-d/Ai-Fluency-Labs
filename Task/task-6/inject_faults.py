"""Exercise defensive tool-call handling with broken calls and no model requests."""
from robust_agent import handle_tool_call


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeCall:
    def __init__(self, name, arguments):
        self.function = FakeFunction(name, arguments)


FAULTS = [
    ("malformed JSON", FakeCall("lookup_plant_care", '{"plant":"basil"')),
    ("unknown function", FakeCall("send_message", '{"text":"water it"}')),
    ("missing season", FakeCall("lookup_plant_care", '{"plant":"basil"}')),
    ("invented property", FakeCall("lookup_plant_care", '{"plant":"basil","season":"summer","zone":"indoors"}')),
    ("wrong type", FakeCall("lookup_plant_care", '{"plant":7,"season":"summer"}')),
    ("invalid enum", FakeCall("lookup_plant_care", '{"plant":"orchid","season":"summer"}')),
    ("water too little", FakeCall("calculate_watering_volume", '{"plant":"mint","pot_size_liters":0}')),
    ("pot beyond supported size", FakeCall("calculate_watering_volume", '{"plant":"tomato","pot_size_liters":250}')),
    ("boolean masquerading as number", FakeCall("calculate_watering_volume", '{"plant":"basil","pot_size_liters":true}')),
    ("malformed root type", FakeCall("calculate_watering_volume", '["tomato", 2]')),
]


if __name__ == "__main__":
    for label, call in FAULTS:
        result = handle_tool_call(call, log=False)
        print(f"{label}: {result}")
        assert isinstance(result, str)
