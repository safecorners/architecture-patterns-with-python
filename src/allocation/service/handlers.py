from __future__ import annotations

from typing import Optional

from allocation.adapters import email
from allocation.domain import events, model
from allocation.service import unit_of_work


class InvalidSku(Exception):
    ...


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    event: events.AllocationRequired, uow: unit_of_work.AbstractUnitOfWork
) -> Optional[str]:
    line = model.OrderLine(event.orderid, event.sku, event.qty)
    with uow:
        product = uow.products.get(line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def add_batch(
    event: events.BatchCreated,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        product = uow.products.get(event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(event.ref, event.sku, event.qty, event.eta))
        uow.commit()


def change_batch_quantity(
    event: events.BatchQuantityChanged, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get_by_batchref(event.ref)
        product.change_batch_quantity(event.ref, event.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock, uow: unit_of_work.AbstractUnitOfWork
):
    email.send("stock@made.com", f"Out of stock for {event.sku}")
