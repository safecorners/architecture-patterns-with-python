import pytest

from allocation.adapters import repository
from allocation.domain import model
from allocation.service import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATE-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATE-LAMP", 100, eta=None)
    repo = repository.InMemoryRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_erorr_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREAL-SKU", 100, eta=None)
    repo = repository.InMemoryRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = repository.InMemoryRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
