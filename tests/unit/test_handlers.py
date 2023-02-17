import pytest

from allocation.adapters import repository
from allocation.service import handlers, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products) -> None:
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        ...


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()
    handlers.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)

    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed


def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()
    handlers.add_batch("b1", "GARISH-RUG", 100, None, uow)
    handlers.add_batch("b2", "GARISH-RUG", 99, None, uow)
    assert "b2" in [b.reference for b in uow.products.get("GARISH-RUG").batches]


def test_returns_allocation():
    uow = FakeUnitOfWork()
    handlers.add_batch("b1", "COMPLICATE-LAMP", 100, None, uow)
    result = handlers.allocate("o1", "COMPLICATE-LAMP", 10, uow)
    assert result == "b1"


def test_erorr_for_invalid_sku():
    uow = FakeUnitOfWork()
    handlers.add_batch("b1", "AREAL-SKU", 100, None, uow)

    with pytest.raises(handlers.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        handlers.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    handlers.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    handlers.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True
