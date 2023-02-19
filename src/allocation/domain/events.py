from dataclasses import dataclass


class Event:
    ...


@dataclass
class OutOfStock(Event):
    sku: str


@dataclass
class Allocated(Event):
    orderid: str
    sku: str
    qty: int
    batchref: str
