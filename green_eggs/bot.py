# -*- coding: utf-8 -*-
import inspect
from typing import Awaitable, Callable, Dict, Mapping, Optional

command_func_type = Callable[..., Awaitable[Optional[str]]]


def validate_callback_signature(callback, args):
    sig = inspect.signature(callback)
    parameters = list(sig.parameters.values())
    pos_only_no_default = [
        p.name
        for p in parameters
        if p.kind == p.POSITIONAL_ONLY and p.default is p.empty
    ]

    if len(pos_only_no_default):
        arg_names = ', '.join(map(repr, pos_only_no_default))
        raise TypeError(
            f'Command callbacks may not have any non-default positional-only parameters ({arg_names})'
        )

    keyword_kinds = (
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    )
    unexpected = [
        p.name
        for p in parameters
        if p.kind in keyword_kinds and p.default is p.empty and p.name not in args
    ]
    if len(unexpected):
        arg_names = ', '.join(map(repr, unexpected))
        raise TypeError(
            f'Unexpected required keyword parameter{"" if len(unexpected) == 1 else "s"}: {arg_names}'
        )


class ChatBot:
    def __init__(self, username: str, token: str):
        self._login = (username, token)
        self.commands: Dict[str, Callable[..., Awaitable[Optional[str]]]] = dict()

    def register_basic_commands(self, commands: Mapping[str, str]):
        for invoke, response in commands.items():

            async def respond():
                return response

            self.commands[invoke] = respond

    def register_command(self, invoke: str):
        def register(callback):
            validate_callback_signature(callback, [])

            if not inspect.iscoroutinefunction(callback):
                sync_callback = callback

                async def async_cb(**kwargs):
                    return sync_callback(**kwargs)

                callback = async_cb

            self.commands[invoke] = callback

        return register

    def register_caster_command(self, invoke: str, username: Optional[str] = None):
        def register(callback):
            validate_callback_signature(callback, [])

            async def caster(message):
                target = (
                    message.args[0]
                    if username is None and len(message.args)
                    else username
                )

                # TODO: api
                if target is not None:
                    name = target
                    link = f'https://twitch.tv/{name}'
                    game = 'Just Chatting'

                    return callback(name, link, game)

            self.commands[invoke] = caster

        return register
