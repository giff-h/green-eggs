# -*- coding: utf-8 -*-
import random
import re

from green_eggs import ChatBot

bot = ChatBot(username='', token='')

bot.register_basic_commands(
    {
        '!power': "IT'S OVER 9000!!!!!!",
        '!ruleone': "Don't talk about Twitch chat.",
    }
)


@bot.register_command('!roll')
def roll(message):
    dice_regex = re.compile(r'(?P<count>\d+)d(?P<sides>\d+)')
    spec = message.args[0] if len(message.args) else '1d20'
    match = dice_regex.match(spec)
    if match is not None:
        count = int(match.group('count'))
        sides = int(match.group('sides'))

        if sides > 1:
            response = f'{message.sender_display} rolled {count} d{sides} and got '

            if count == 1:
                result = random.randint(1, sides)
                return response + str(result)

            if count > 1:
                result = [random.randint(1, sides) for _ in range(count)]
                result_display = (
                    ', '.join(map(str, result[:-1])) + f', and {result[-1]}'
                )
                total = sum(result)
                return response + f'{result_display} for a total of {total}'

        return 'You need to roll at least 1 die with at least 2 sides'

    return 'Usage: !roll [count]d[sides]'


@bot.register_command('!calm')
async def calm(channel):
    await channel.send('EVERYBODY PANIC!')
    await channel.send('=============\\o\\')
    await channel.send('/o/=============')


@bot.register_caster_command('!caster')
def caster(name, link, game):
    return f'We love {name}, check them out at {link} for fun times such as {game}'
