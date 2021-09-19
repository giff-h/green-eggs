# Green Eggs

### About

This is a library/framework that you can use to easily create a channel chatbot with Python code.

It is intended to be very quick and simple to set up and use, and either be stopped and started whenever, or stay running indefinitely.

### Usage

See `example.py` for an example bot setup. That's all there is for now, more in-depth documentation is coming soon.
- `bot.register_basic_commands` is a function that takes a mapping of first word invoke to response strings.
- `bot.register_command` is a decorator that takes a first word invoke and decorates a function that's called when the command is run.
  - Notice in the example that this can be a sync or async function.
  - The parameters must be accessible by keyword, and the value depends on the name of the keyword.

### Features

- A robust IRC client that ensures that expected responses to actions have happened, such as joining and leaving a channel, and reconnects or fails as necessary.
- A Helix API accessor with functions for each documented endpoint, fully typed for URL parameter and payload body values.
- An expandable way of specifying how messages trigger command, beyond just the first word being `!command`.
- A complete suite of dataclasses to represent all possible data that comes through the IRC chat. This allows for robust typings.

### Features soon coming

- Cooldowns on commands, per user and global.
- Link detection and conditional deletion, so you don't have to disallow links in channel settings.

### Eventual future features

- A way to write the bot with a config file and/or a python file.
- A suite of SQLAlchemy models to save incoming data from IRC, with columns to match the dataclasses.
- API result caching.
- A suite of CLI options to quickly make API calls and database queries.
- Webhooks for handling events that don't come through in chat, and better handling of events that do.
