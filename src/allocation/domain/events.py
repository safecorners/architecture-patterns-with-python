from dataclasses import dataclass


class Event:
    ...


@dataclass
class OutOfStock(Event):
    sku: str
