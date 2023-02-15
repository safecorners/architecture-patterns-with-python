from __future__ import annotations

from datetime import date
from typing import Optional

from allocation.adapters.repository import AbstractRepository
from allocation.domain import model


class InvalidSku(Exception):
    ...


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    orderid: str, sku: str, qty: int, repo: AbstractRepository, session
) -> str:
    line = model.OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session
):
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()
