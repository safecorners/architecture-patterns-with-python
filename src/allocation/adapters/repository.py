import abc

from allocation.domain.model import Product


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: Product) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku) -> Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session) -> None:
        self.session = session

    def add(self, product: Product) -> None:
        self.session.add(product)

    def get(self, sku: str) -> Product:
        return self.session.query(Product).filter_by(sku=sku).first()
