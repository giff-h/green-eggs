Release History
===============

0.1.1 (2022-02-15)
------------------

- Python 3.10 support
- Fix: Parse API documentation correctly for request payload fields that are objects and object lists

0.1.0 (2021-09-19)
------------------

- Initial build
- Basic structure for classes
  - Websocket connection that handles channel presence and yields incoming messages
  - dataclasses to match the incoming messages from the websocket
  - Channel state
  - Annotated API endpoint functions, automatically generated from documentation
  - Main entry bot class for setting basic commands and actions
