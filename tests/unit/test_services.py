import pytest

from allocation.adapters import repository
from allocation.service import services, unit_of_work

FakeRepository = repository.InMemoryRepository


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        ...


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)

    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "COMPLICATE-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATE-LAMP", 10, uow)
    assert result == "b1"


def test_erorr_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREAL-SKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)

    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True
