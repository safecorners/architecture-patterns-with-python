from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Type

from allocation.domain import events
from allocation.service import handlers

if TYPE_CHECKING:
    from allocation.service import unit_of_work


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow))
            queue.extend(uow.collect_new_events())
    return results


HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.BatchCreated: [handlers.add_batch],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.AllocationRequired: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
