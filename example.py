# -*- coding: utf-8 -*-
import random
import re

from green_eggs import ChatBot
from green_eggs.channel import Channel
from green_eggs.config import LinkAllowUserConditions
from green_eggs.data_types import PrivMsg

bot = ChatBot(
    channel='your_channel_goes_here',
    config=dict(
        block_links=True,
        link_allow_user_condition=LinkAllowUserConditions.USER_VIP | LinkAllowUserConditions.USER_SUBSCRIBED,
        link_allow_target_conditions=[
            dict(domain='clips.twitch.tv'),  # main twitch clips link
            dict(domain=re.compile(r'(www\.)?twitch\.tv'), path=re.compile(r'/.+/clips/.+')),  # alternate clips link
            dict(domain=re.compile(r'(.+\.)?imgur\.com')),  # who doesn't want memes
        ],
    ),
)

bot.register_basic_commands(
    {
        '!power': "IT'S OVER 9000!!!!!!",
        '!ruleone': "Don't talk about Twitch chat.",
    }
)


@bot.register_command('!roll', global_cooldown=2)
def roll(message: PrivMsg):
    dice_regex = re.compile(r'(?P<count>\d*)d(?P<sides>\d+)')
    spec = message.words[1] if len(message.words) >= 2 else '1d20'
    match_result = dice_regex.match(spec)
    if match_result is not None:
        count = int(match_result.group('count') or 1)
        sides = int(match_result.group('sides'))

        if count > 0 and sides > 1:
            response = f'{message.tags.display_name} rolled {count} d{sides} and got '
            roll_result = [random.randint(1, sides) for _ in range(count)]
            total = sum(roll_result)

            if count == 1:
                response += str(total)
            elif count == 2:
                response += ' and '.join(map(str, roll_result)) + f' for a total of {total}'
            else:
                result_display = ', '.join(map(str, roll_result[:-1])) + f', and {roll_result[-1]}'
                response += f'{result_display} for a total of {total}'

            return response

        return 'You need to roll at least 1 die with at least 2 sides'

    return 'Usage: !roll [count]d[sides]'


@bot.register_command('!calm', user_cooldown=10)
async def calm(channel: Channel):
    await channel.send('EVERYBODY PANIC!')
    await channel.send('/me =============\\o\\')
    await channel.send('/me /o/=============')


@bot.register_caster_command('!caster')
def caster(display_name: str, user_link: str, game_name: str):
    return f'We love {display_name}, check them out at {user_link} for fun times such as {game_name}'


if __name__ == '__main__':
    bot.run_sync(chat_bot_username='bot_username', chat_bot_token='oauth:bot_token', api_token='api_token')
