from __future__ import annotations

from dataclasses import asdict
from typing import Callable, Dict, List, Type

from sqlalchemy.sql import text

from allocation.adapters import notifications
from allocation.domain import commands, events, model
from allocation.service import unit_of_work


class InvalidSku(Exception):
    ...


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    cmd: commands.Allocate,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    line = model.OrderLine(cmd.orderid, cmd.sku, cmd.qty)
    with uow:
        product = uow.products.get(line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        product.allocate(line)
        uow.commit()


def reallocate(
    event: events.Deallocated,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    allocate(commands.Allocate(**asdict(event)), uow)


def add_batch(
    cmd: commands.CreateBatch,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        product = uow.products.get(cmd.sku)
        if product is None:
            product = model.Product(cmd.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(cmd.ref, cmd.sku, cmd.qty, cmd.eta))
        uow.commit()


def change_batch_quantity(
    cmd: commands.ChangeBatchQuantity,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        product = uow.products.get_by_batchref(cmd.ref)
        product.change_batch_quantity(cmd.ref, cmd.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock, notifications: notifications.AbstractNotifications
) -> None:
    notifications.send("stock@made.com", f"Out of stock for {event.sku}")


def publish_allocated_event(event: events.Allocated, publish: Callable) -> None:
    publish("line_allocated", event)


def add_allocation_to_read_model(
    event: events.Allocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
) -> None:
    with uow:
        stmt = text(
            """
            INSERT INTO allocations_view (orderid, sku, batchref)
            VALUES (:orderid, :sku, :batchref)
            """
        )
        uow.session.execute(
            stmt, dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref)
        )
        uow.commit()


def remove_allocation_from_read_model(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        stmt = text(
            """
            DELETE FROM allocations_view
            WHERE orderid = :orderid AND sku = :sku
            """
        )
        uow.session.execute(
            stmt,
            dict(orderid=event.orderid, sku=event.sku),
        )
        uow.commit()


EVENT_HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],
    events.Allocated: [
        publish_allocated_event,
        add_allocation_to_read_model,
    ],
    events.Deallocated: [
        remove_allocation_from_read_model,
        reallocate,
    ],
}

COMMAND_HANDLERS: Dict[Type[commands.Command], Callable] = {
    commands.Allocate: allocate,
    commands.CreateBatch: add_batch,
    commands.ChangeBatchQuantity: change_batch_quantity,
}
