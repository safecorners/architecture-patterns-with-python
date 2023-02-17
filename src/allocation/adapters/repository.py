import abc
from typing import Set

from allocation.domain.model import Product


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        self.seen: Set[Product] = set()

    def add(self, product: Product) -> None:
        self._add(product)
        self.seen.add(product)

    @abc.abstractmethod
    def _add(self, product: Product) -> None:
        raise NotImplementedError

    def get(self, sku) -> Product:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _get(self, sku) -> Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session) -> None:
        super().__init__()
        self.session = session

    def _add(self, product: Product) -> None:
        self.session.add(product)

    def _get(self, sku: str) -> Product:
        return self.session.query(Product).filter_by(sku=sku).first()
