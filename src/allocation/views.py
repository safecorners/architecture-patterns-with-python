import logging

from sqlalchemy.sql import text

from allocation.domain import model
from allocation.service import unit_of_work

logger = logging.getLogger(__name__)


def allocations(orderid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        batches = (
            uow.session.query(model.Batch)
            .join(model.OrderLine, model.Batch._allocations)
            .filter(model.OrderLine.orderid == orderid)
        )
        return [{"sku": b.sku, "batchref": b.reference} for b in batches]
