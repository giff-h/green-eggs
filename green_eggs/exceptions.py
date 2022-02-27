# -*- coding: utf-8 -*-
class ChannelPresenceRaceCondition(Exception):
    pass


class CooldownNotElapsed(Exception):
    remaining: float

    def __init__(self, remaining: float, *args, **kwargs):
        self.remaining = remaining
        super(*args, **kwargs)


class GlobalCooldownNotElapsed(CooldownNotElapsed):
    pass


class UserCooldownNotElapsed(CooldownNotElapsed):
    pass
