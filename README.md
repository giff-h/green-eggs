# WIP

### What is this

This will eventually be a library/framework that you can use to create a channel chatbot with either config or Python code.

It is intended to be very quick and simple to set up and use, and either be stopped and started whenever, or stay running indefinitely.

### Features

- A complete suite of dataclasses to represent all possible data that comes through the IRC chat. This allows for robust typings.
- An expandable way of specifying how messages trigger command, beyond just the first word being `!command`.
- A robust IRC client that ensures that expected responses to actions have happened, such as joining and leaving a channel, and reconnects or fails as necessary.
- A Helix API accessor with functions for each documented endpoint, fully typed for URL parameter and payload body values.

### Features soon coming

- Link detection and conditional deletion, so you don't have to disallow links in channel settings.

### Eventual future features

- A suite of SQLAlchemy models to save incoming data from IRC, with columns to match the dataclasses.
- A suite of CLI options to quickly make API calls and database queries.
