# -*- coding: utf-8 -*-
from typing import List, Mapping, Optional

from green_eggs.api import TwitchApi
from green_eggs.commands import CommandRegistry, FirstWordTrigger, SenderIsModTrigger
from green_eggs.data_types import PrivMsg
from green_eggs.types import RegisterAbleFunc


class ChatBot:
    def __init__(self, *, channel: str):
        self.channel = channel
        self._commands = CommandRegistry()

    def register_basic_commands(self, commands: Mapping[str, str]):
        for invoke, response in commands.items():
            trigger = FirstWordTrigger(invoke, case_sensitive=False)
            self._commands.add(trigger, lambda: response)

    def register_command(self, invoke: str):
        trigger = FirstWordTrigger(invoke, case_sensitive=False)
        return self._commands.decorator(trigger)

    def register_caster_command(self, invoke: str):
        """
        Decorator to register a function as a caster command.

        :param invoke: The command part in the chat message
        :return: The decorator
        """
        trigger = FirstWordTrigger(invoke, case_sensitive=False) & SenderIsModTrigger()

        def factory(callback: RegisterAbleFunc, callback_keywords: List[str]) -> RegisterAbleFunc:
            async def command(message: PrivMsg, api: TwitchApi) -> Optional[str]:
                if not len(message.words):
                    return 'I need a name for that'

                callback_kwargs = dict()
                name = message.words[0]
                user_result = await api.get_users(login=name.lstrip('@'))
                if not len(user_result['data']):
                    return f'Could not find user data for {name}'

                user = user_result['data'][0]
                streams = await api.get_channel_information(broadcaster_id=user['id'])
                stream = streams['data'][0]

                if 'name' in callback_keywords:
                    callback_kwargs['name'] = user['display_name']
                if 'link' in callback_keywords:
                    callback_kwargs['link'] = 'https://twitch.tv/' + user['login']
                if 'game' in callback_keywords:
                    callback_kwargs['game'] = stream['game_name']
                if 'api_result' in callback_keywords:
                    callback_kwargs['api_result'] = stream

                output = callback(**callback_kwargs)
                if output is None or isinstance(output, str):
                    return output
                else:
                    return await output

            return command

        return self._commands.decorator(
            trigger, target_keywords=['name', 'link', 'game', 'api_result'], command_factory=factory
        )

    def run(self, *, username: str, token: str):
        """
        Main loop to run the bot after configuring.
        """
