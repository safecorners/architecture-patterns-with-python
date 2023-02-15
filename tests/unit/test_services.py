import pytest

from allocation.adapters import repository
from allocation.domain import model
from allocation.service import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = repository.InMemoryRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)

    assert repo.get("b1") is not None
    assert session.committed


def test_returns_allocation():
    repo, session = repository.InMemoryRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATE-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATE-LAMP", 10, repo, session)
    assert result == "b1"


def test_erorr_for_invalid_sku():
    repo, session = repository.InMemoryRepository([]), FakeSession()
    services.add_batch("b1", "AREAL-SKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = repository.InMemoryRepository([batch])
    session = FakeSession()

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True
