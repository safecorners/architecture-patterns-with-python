from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, List, Type, Union

from tenacity import RetryError, Retrying, stop_after_attempt, wait_exponential

from allocation.domain import commands, events

if TYPE_CHECKING:
    from allocation.service import unit_of_work

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus:
    def __init__(
        self,
        uow: unit_of_work.AbstractUnitOfWork,
        event_handlers: Dict[Type[events.Event], List[Callable]],
        command_handlers: Dict[Type[commands.Command], Callable],
    ) -> None:
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message) -> None:
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)

            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

    def handle_event(self, event: events.Event) -> None:
        for handler in self.event_handlers[type(event)]:
            try:
                for attempt in Retrying(
                    stop=stop_after_attempt(3), wait=wait_exponential()
                ):
                    with attempt:
                        logger.debug(
                            "handling event %s with handler %s", event, handler
                        )
                        handler(event)
                        self.queue.extend(self.uow.collect_new_events())
            except RetryError as retry_failure:
                logger.exception(
                    "Failed to handle events %s times",
                    retry_failure.last_attempt.attempt_number,
                )
                continue

    def handle_command(self, command: commands.Command) -> None:
        logger.debug("handling commnad %s", command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            self.queue.extend(self.uow.collect_new_events())

        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
