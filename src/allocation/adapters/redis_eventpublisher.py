import json
import logging
from dataclasses import asdict

import redis

from allocation import config
from allocation.domain import events

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel, event: events.Event):
    logging.debug(f"publishing: channel={channel}, event={event}")
    r.publish(channel, json.dumps(asdict(event)))
