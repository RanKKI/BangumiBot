from dataclasses import fields


def from_dict_to_dataclass(cls, data: dict):
    field_set = {f.name for f in fields(cls) if f.init}
    return cls(**{k: v for k, v in data.items() if k in field_set})
