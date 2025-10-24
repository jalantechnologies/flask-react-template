from typing import Dict, Union

AllowedConfigValueTypes = Union[int, str, bool, float, list, Dict[str, "AllowedConfigValueTypes"], None, "Config"]

Config = Dict[str, AllowedConfigValueTypes]
