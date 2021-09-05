# -*- coding: utf-8 -*-
import random
import re

from green_eggs import ChatBot
from green_eggs.data_types import PrivMsg

bot = ChatBot(channel='')

bot.register_basic_commands(
    {
        '!power': "IT'S OVER 9000!!!!!!",
        '!ruleone': "Don't talk about Twitch chat.",
    }
)


@bot.register_command('!roll')
def roll(message: PrivMsg):
    dice_regex = re.compile(r'(?P<count>\d*)d(?P<sides>\d+)')
    spec = message.words[1] if len(message.words) >= 1 else '1d20'
    match = dice_regex.match(spec)
    if match is not None:
        count = int(match.group('count') or 1)
        sides = int(match.group('sides'))

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


@bot.register_command('!calm')
async def calm(channel):
    await channel.send('EVERYBODY PANIC!')
    await channel.send('/me =============\\o\\')
    await channel.send('/me /o/=============')


@bot.register_caster_command('!caster')
def caster(name, link, game):
    return f'We love {name}, check them out at {link} for fun times such as {game}'


if __name__ == '__main__':
    bot.run(username='', token='')
