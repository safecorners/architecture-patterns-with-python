from datetime import datetime
from typing import Optional

from flask import Flask, jsonify
from flask_pydantic import validate
from pydantic import BaseModel

from allocation import bootstrap, views
from allocation.domain import commands
from allocation.service import handlers, unit_of_work

bus = bootstrap.bootstrap()
app = Flask(__name__)


class AddBatchRequest(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: Optional[str]


@app.route("/add_batch", methods=["POST"])
@validate()
def add_batch(body: AddBatchRequest):
    if body.eta is not None:
        eta = datetime.fromisoformat(body.eta).date()
    else:
        eta = None

    cmd = commands.CreateBatch(
        body.ref,
        body.sku,
        body.qty,
        eta,
    )

    bus.handle(cmd)
    return "OK", 201


class AllocateRequest(BaseModel):
    orderid: str
    sku: str
    qty: int


@app.route("/allocate", methods=["POST"])
@validate()
def allocate_endpoint(body: AllocateRequest):
    try:
        cmd = commands.Allocate(
            body.orderid,
            body.sku,
            body.qty,
        )

        bus.handle(cmd)
    except handlers.InvalidSku as e:
        return jsonify({"message": str(e)}), 400

    return "OK", 202


@app.route("/allocations/<orderid>", methods=["GET"])
def allocations_view_endpoint(orderid):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return "not found", 404
    return jsonify(result), 200
