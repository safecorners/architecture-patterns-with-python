import pytest
import requests

from allocation import config

from ..random_refs import random_batchref, random_orderid, random_sku
from . import api_client


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_202_and_allocated_batch():
    orderid = random_orderid()
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    api_client.post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    api_client.post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    api_client.post_to_add_batch(otherbatch, othersku, 100, None)

    data = {"orderid": orderid, "sku": sku, "qty": 3}

    url = config.get_api_url()
    response = requests.post(f"{url}/allocate", json=data)

    assert response.status_code == 202

    response = requests.get(f"{url}/allocations/{orderid}")
    assert response.ok
    assert response.json() == [{"sku": sku, "batchref": earlybatch}]


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()
    response = requests.post(f"{url}/allocate", json=data)
    assert response.status_code == 400
    assert response.json()["message"] == f"Invalid sku {unknown_sku}"

    response = requests.get(f"{url}/allocate/{orderid}")
    assert response.status_code == 404
