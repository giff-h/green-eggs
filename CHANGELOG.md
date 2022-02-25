Release History
===============

0.2.0 (2022-02-24)
------------------

- Added a class for first class access to common API usage
  - An instance of this is now passed to decorated function commands instead of the original raw API class. No
    deprecation warning was given because this is still in pre-release state and is subject to change without notice
- Changed the names of the possible kwargs of decorated caster commands and added more
- Added a config class to hold user config choices
- Added configurable link detection and purging

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
