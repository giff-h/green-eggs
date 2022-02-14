# -*- coding: utf-8 -*-
from types import TracebackType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Type, Union
from urllib.parse import urlencode

import aiohttp
from aiologger import Logger

_empty: Any = object()
UrlParams = Union[
    Mapping[Any, Any],
    Mapping[Any, Sequence[Any]],
    Sequence[Tuple[Any, Any]],
    Sequence[Tuple[Any, Sequence[Any]]],
]


def exclude_non_empty(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not _empty}


class TwitchApi:
    _base_url = 'https://api.twitch.tv/helix/'

    def __init__(self, *, client_id: str, token: str, logger: Logger):
        headers = {'Client-ID': client_id, 'Authorization': f'Bearer {token}'}
        self._logger: Logger = logger
        self._session: aiohttp.ClientSession = aiohttp.ClientSession(headers=headers)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: UrlParams = _empty,
        data: Optional[Dict[str, Any]] = None,
        raise_for_status: bool = True,
    ) -> Any:
        """
        Executes a request on helix.

        :param str method: The HTTP method
        :param str path: The helix API path
        :param params: The params for `urlencode`
        :param data: The data for the request body
        :param bool raise_for_status:
        :return:
        """
        url = self._base_url + path
        if params is not _empty and params:
            if isinstance(params, Mapping):
                params = {k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()}
            url += f'?{urlencode(params, doseq=True)}'

        self._logger.debug(f'Making {method} request to {url}')

        async with self._session.request(method, url, json=data) as response:
            if raise_for_status:
                response.raise_for_status()
            response_data = await response.json()

        return response_data

    async def __aenter__(self) -> 'TwitchApi':
        self._session = await self._session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        await self._session.__aexit__(exc_type, exc_val, exc_tb)

    # API endpoint functions

    async def start_commercial(self, *, broadcaster_id: str, length: int):
        """
        Starts a commercial on a specified channel.

        # Authentication:
        - OAuth Token required

        - Required scope: `channel:edit:commercial`

        # Pagination Support:
        None

        # URL:
        `POST https://api.twitch.tv/helix/channels/commercial`

        # Required Query Parameter:
        None

        # Required Body Parameter:
        +------------------+---------+----------------------------------------------+
        | Parameter        | Type    | Description                                  |
        +------------------+---------+----------------------------------------------+
        | `broadcaster_id` | string  | ID of the channel requesting a commercial    |
        |                  |         | Minimum: 1 Maximum: 1                        |
        +------------------+---------+----------------------------------------------+
        | `length`         | integer | Desired length of the commercial in seconds. |
        |                  |         | Valid options are 30, 60, 90, 120, 150, 180. |
        +------------------+---------+----------------------------------------------+

        # Optional Query Parameters:
        None

        # Response Fields:
        +---------------+---------+-----------------------------------------------------------------+
        | Parameter     | Type    | Description                                                     |
        +---------------+---------+-----------------------------------------------------------------+
        | `length`      | integer | Length of the triggered commercial                              |
        +---------------+---------+-----------------------------------------------------------------+
        | `message`     | string  | Provides contextual information on why the request failed       |
        +---------------+---------+-----------------------------------------------------------------+
        | `retry_after` | integer | Seconds until the next commercial can be served on this channel |
        +---------------+---------+-----------------------------------------------------------------+
        """
        data = exclude_non_empty(broadcaster_id=broadcaster_id, length=length)
        return await self._request('POST', 'channels/commercial', data=data)

    async def get_extension_analytics(
        self,
        *,
        after: str = _empty,
        ended_at: str = _empty,
        extension_id: str = _empty,
        first: int = _empty,
        started_at: str = _empty,
        type_: str = _empty,
    ):
        """
        Gets a URL that Extension developers can use to download analytics reports (CSV files) for their Extensions. The
        URL is valid for 5 minutes.

        If you specify a future date, the response will be “Report Not Found For Date Range.” If you leave both `started_at` and `ended_at` blank, the API returns the most recent date of data.

        # Authentication:
        - OAuth token required

        - Required scope: `analytics:read:extensions`

        # URL:
        `GET https://api.twitch.tv/helix/analytics/extensions`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name           | Type    | Description                                                                                                                                                                                                                                                                                                                                                |
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`        | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries without `extension_id`. If an `extension_id `is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query. |
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`     | string  | Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`. The report covers the entire ending date; e.g., if `2018-05-01T00:00:00Z` is specified, the report covers up to `2018-05-01T23:59:59Z`.                                                             |
        |                |         |                                                                                                                                                                                                                                                                                                                                                            |
        |                |         | If this is provided, `started_at` also must be specified. If `ended_at` is later than the default end date, the default date is used. Default: 1-2 days before the request was issued (depending on report availability).                                                                                                                                  |
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `extension_id` | string  | Client ID value assigned to the extension when it is created. If this is specified, the returned URL points to an analytics report for just the specified extension. If this is not specified, the response includes multiple URLs (paginated), pointing to separate analytics reports for each of the authenticated user’s Extensions.                    |
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`        | integer | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                                                                                                                                                            |
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at`   | string  | Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`. This must be on or after January 31, 2018.                                                                                                                                                        |
        |                |         |                                                                                                                                                                                                                                                                                                                                                            |
        |                |         | If this is provided, `ended_at` also must be specified. If `started_at` is earlier than the default start date, the default date is used. The file contains one row of data per day.                                                                                                                                                                       |
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`         | string  | Type of analytics report that is returned. Currently, this field has no affect on the response as there is only one report type. If additional types were added, using this field would return only the URL for the specified report. Limit: 1. Valid values: `"overview_v2"`.                                                                             |
        +----------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field          | Type                       | Description                                                                                                                                                                           |
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`     | string                     | Report end date/time.                                                                                                                                                                 |
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `extension_id` | string                     | ID of the extension whose analytics data is being provided.                                                                                                                           |
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`   | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results. This is returned only if `extension_id` is not specified in the request. |
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at`   | string                     | Report start date/time. Note this may differ from (be later than) the `started_at` value in the request; the response value is the date when data for the extension is available.     |
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`         | string                     | Type of report.                                                                                                                                                                       |
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `URL`          | string                     | URL to the downloadable CSV file containing analytics data. Valid for 5 minutes.                                                                                                      |
        +----------------+----------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after, ended_at=ended_at, extension_id=extension_id, first=first, started_at=started_at, type=type_
        )
        return await self._request('GET', 'analytics/extensions', params=params)

    async def get_game_analytics(
        self,
        *,
        after: str = _empty,
        ended_at: str = _empty,
        first: int = _empty,
        game_id: str = _empty,
        started_at: str = _empty,
        type_: str = _empty,
    ):
        """
        Gets a URL that game developers can use to download analytics reports (CSV files) for their games. The URL is
        valid for 5 minutes. For detail about analytics and the fields returned, see the Insights & Analytics guide.

        The response has a JSON payload with a `data` field containing an array of games information elements and can contain a `pagination` field containing information required to query for more streams.

        If you specify a future date, the response will be “Report Not Found For Date Range.” If you leave both `started_at` and `ended_at` blank, the API returns the most recent date of data.

        # Authentication:
        - OAuth token required

        - Required scope: `analytics:read:games`

        # URL:
        `GET https://api.twitch.tv/helix/analytics/games`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name         | Type    | Description                                                                                                                                                                                                                                                                                                                                     |
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`      | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries without `game_id`. If a `game_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query. |
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`   | string  | Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`. The report covers the entire ending date; e.g., if `2018-05-01T00:00:00Z` is specified, the report covers up to `2018-05-01T23:59:59Z`.                                                  |
        |              |         |                                                                                                                                                                                                                                                                                                                                                 |
        |              |         | If this is provided, `started_at` also must be specified. If `ended_at` is later than the default end date, the default date is used. Default: 1-2 days before the request was issued (depending on report availability).                                                                                                                       |
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`      | integer | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                                                                                                                                                 |
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`    | string  | Game ID. If this is specified, the returned URL points to an analytics report for just the specified game. If this is not specified, the response includes multiple URLs (paginated), pointing to separate analytics reports for each of the authenticated user’s games.                                                                        |
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at` | string  | Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`.                                                                                                                                                                                        |
        |              |         |                                                                                                                                                                                                                                                                                                                                                 |
        |              |         | If this is provided, `ended_at` also must be specified. If `started_at` is earlier than the default start date, the default date is used. Default: 365 days before the report was issued. The file contains one row of data per day.                                                                                                            |
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`       | string  | Type of analytics report that is returned. Currently, this field has no affect on the response as there is only one report type. If additional types were added, using this field would return only the URL for the specified report. Limit: 1. Valid values: `"overview_v2"`.                                                                  |
        +--------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field        | Type                       | Description                                                                                                                                                                      |
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`   | string                     | Report end date/time.                                                                                                                                                            |
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`    | string                     | ID of the game whose analytics data is being provided.                                                                                                                           |
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination` | Object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results. This is returned only if `game_id` is not specified in the request. |
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at` | string                     | Report start date/time.                                                                                                                                                          |
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`       | string                     | Type of report.                                                                                                                                                                  |
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `URL`        | string                     | URL to the downloadable CSV file containing analytics data. Valid for 5 minutes.                                                                                                 |
        +--------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after, ended_at=ended_at, first=first, game_id=game_id, started_at=started_at, type=type_
        )
        return await self._request('GET', 'analytics/games', params=params)

    async def get_bits_leaderboard(
        self, *, count: int = _empty, period: str = _empty, started_at: str = _empty, user_id: str = _empty
    ):
        """
        Gets a ranked list of Bits leaderboard information for an authorized broadcaster.

        # Authentication:
        - OAuth token required

        - Required scope: `bits:read`

        # URL:
        `GET https://api.twitch.tv/helix/bits/leaderboard`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +--------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name         | Type    | Description                                                                                                                                                                                                                                                |
        +--------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `count`      | integer | Number of results to be returned. Maximum: 100. Default: 10.                                                                                                                                                                                               |
        +--------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `period`     | string  | Time period over which data is aggregated (PST time zone). This parameter interacts with `started_at`. Valid values follow. Default: `"all"`.                                                                                                              |
        |              |         | - None`"day"` – 00:00:00 on the day specified in `started_at`, through 00:00:00 on the following day.                                                                                                                                                      |
        |              |         | - None`"week"` – 00:00:00 on Monday of the week specified in `started_at`, through 00:00:00 on the following Monday.                                                                                                                                       |
        |              |         | - None`"month"` – 00:00:00 on the first day of the month specified in `started_at`, through 00:00:00 on the first day of the following month.                                                                                                              |
        |              |         | - None`"year"` – 00:00:00 on the first day of the year specified in `started_at`, through 00:00:00 on the first day of the following year.                                                                                                                 |
        |              |         | - None`"all"` – The lifetime of the broadcaster's channel. If this is specified (or used by default), `started_at` is ignored.                                                                                                                             |
        +--------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at` | string  | Timestamp for the period over which the returned data is aggregated. Must be in RFC 3339 format. If this is not provided, data is aggregated over the current period; e.g., the current day/week/month/year. This value is ignored if `period` is `"all"`. |
        |              |         |                                                                                                                                                                                                                                                            |
        |              |         | Any `+` operator should be URL encoded.                                                                                                                                                                                                                    |
        |              |         |                                                                                                                                                                                                                                                            |
        |              |         | Currently, the HH:MM:SS part of this value is used only to identify a given day in PST and otherwise ignored. For example, if the `started_at` value resolves to 5PM PST yesterday and `period` is `"day"`, data is returned for all of yesterday.         |
        +--------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`    | string  | ID of the user whose results are returned; i.e., the person who paid for the Bits.                                                                                                                                                                         |
        |              |         |                                                                                                                                                                                                                                                            |
        |              |         | As long as `count` is greater than 1, the returned data includes additional users, with Bits amounts above and below the user specified by `user_id`.                                                                                                      |
        |              |         |                                                                                                                                                                                                                                                            |
        |              |         | If `user_id` is not provided, the endpoint returns the Bits leaderboard data across top users (subject to the value of `count`).                                                                                                                           |
        +--------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | Field        | Type    | Description                                                                                                                     |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`   | string  | End of the date range for the returned data.                                                                                    |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `rank`       | integer | Leaderboard rank of the user.                                                                                                   |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `score`      | integer | Leaderboard score (number of Bits) of the user.                                                                                 |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `started_at` | string  | Start of the date range for the returned data.                                                                                  |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `total`      | integer | Total number of results (users) returned. This is `count` or the total number of entries in the leaderboard, whichever is less. |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`    | string  | ID of the user (viewer) in the leaderboard entry.                                                                               |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `user_login` | string  | User login name.                                                                                                                |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`  | string  | Display name corresponding to `user_id`.                                                                                        |
        +--------------+---------+---------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(count=count, period=period, started_at=started_at, user_id=user_id)
        return await self._request('GET', 'bits/leaderboard', params=params)

    async def get_cheermotes(self, *, broadcaster_id: str = _empty):
        """
        Retrieves the list of available Cheermotes, animated emotes to which viewers can assign Bits, to cheer in chat.
        Cheermotes returned are available throughout Twitch, in all Bits-enabled channels.

        # URL:
        `GET https://api.twitch.tv/helix/bits/cheermotes`

        # Authentication:
        OAuth or App Access Token required.

        # Optional Query Parameter:
        +------------------+--------+--------------------------------------------------------------+
        | Parameter        | Type   | Description                                                  |
        +------------------+--------+--------------------------------------------------------------+
        | `broadcaster_id` | string | ID for the broadcaster who might own specialized Cheermotes. |
        +------------------+--------+--------------------------------------------------------------+

        # Response Fields:
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Type    | Description                                                                                                                      |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `prefix`            | string  | The string used to Cheer that precedes the Bits amount.                                                                          |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `tiers`             | array   | An array of Cheermotes with their metadata.                                                                                      |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `min_bits`          | integer | Minimum number of bits needed to be used to hit the given tier of emote.                                                         |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `id`                | string  | ID of the emote tier. Possible tiers are: 1,100,500,1000,5000, 10k, or 100k.                                                     |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `color`             | string  | Hex code for the color associated with the bits of that tier. Grey, Purple, Teal, Blue, or Red color to match the base bit type. |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `images`            | object  | Structure containing both animated and static image sets, sorted by light and dark.                                              |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `can_cheer`         | Boolean | Indicates whether or not emote information is accessible to users.                                                               |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `show_in_bits_card` | Boolean | Indicates whether or not we hide the emote from the bits card.                                                                   |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `type`              | string  | Shows whether the emote is `global_first_party`, `global_third_party`, `channel_custom`, `display_only`, or `sponsored`.         |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `order`             | integer | Order of the emotes as shown in the bits card, in ascending order.                                                               |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `last_updated`      | string  | The data when this Cheermote was last updated.                                                                                   |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        | `is_charitable`     | Boolean | Indicates whether or not this emote provides a charity contribution match during charity campaigns.                              |
        +---------------------+---------+----------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'bits/cheermotes', params=params)

    async def get_extension_transactions(
        self, *, after: str = _empty, extension_id: str, first: int = _empty, id_: Union[str, List[str]] = _empty
    ):
        """
        Gets the list of Extension transactions for a given Extension. This allows Extension back-end servers to fetch a
        list of transactions that have occurred for their Extension across all of Twitch. A transaction is a record of a
        user exchanging Bits for an in-Extension digital good.

        # URL:
        `GET https://api.twitch.tv/helix/extensions/transactions`

        # Authentication:
        - App Access Token

        # Required Query Parameters:
        +----------------+--------+-----------------------------------------------+
        | Parameter      | Type   | Description                                   |
        +----------------+--------+-----------------------------------------------+
        | `extension_id` | string | ID of the Extension to list transactions for. |
        |                |        |                                               |
        |                |        | Maximum: 1                                    |
        +----------------+--------+-----------------------------------------------+

        # Optional Query Parameters:
        +-----------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type    | Description                                                                                                                               |
        +-----------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`      | string  | Transaction IDs to look up. Can include multiple to fetch multiple transactions in a single request.                                      |
        |           |         |                                                                                                                                           |
        |           |         | For example, `/helix/extensions/transactions?extension_id=1234&id=1&id=2&id=3`                                                            |
        |           |         |                                                                                                                                           |
        |           |         | Maximum: 100.                                                                                                                             |
        +-----------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string  | The cursor used to fetch the next page of data. This only applies to queries without ID. If an ID is specified, it supersedes the cursor. |
        +-----------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | integer | Maximum number of objects to return.                                                                                                      |
        |           |         |                                                                                                                                           |
        |           |         | Maximum: 100. Default: 20.                                                                                                                |
        +-----------+---------+-------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                    | Type                       | Description                                                                                                                            |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `data`                       | array                      | Array of requested transactions.                                                                                                       |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                         | string                     | Unique identifier of the Bits-in-Extensions transaction.                                                                               |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `timestamp`                  | string                     | UTC timestamp when this transaction occurred.                                                                                          |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`             | string                     | Twitch user ID of the channel the transaction occurred on.                                                                             |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`          | string                     | Login name of the broadcaster.                                                                                                         |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`           | string                     | Twitch display name of the broadcaster.                                                                                                |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`                    | string                     | Twitch user ID of the user who generated the transaction.                                                                              |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login`                 | string                     | Login name of the user who generated the transaction.                                                                                  |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`                  | string                     | Twitch display name of the user who generated the transaction.                                                                         |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_type`               | string                     | Enum of the product type. Currently only `BITS_IN_EXTENSION`.                                                                          |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data`               | object                     | Represents the product acquired, as it looked at the time of the transaction.                                                          |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data.domain`        | string                     | Set to twitch.ext + your Extension ID.                                                                                                 |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data.sku`           | string                     | Unique identifier for the product across the Extension.                                                                                |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data.cost`          | object                     | Represents the cost to acquire the product.                                                                                            |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data.cost.amount`   | integer                    | Number of Bits required to acquire the product.                                                                                        |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data.cost.type`     | string                     | Identifies the contribution method. Currently only `bits`.                                                                             |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data.inDevelopment` | boolean                    | Indicates if the product is in development.                                                                                            |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `product_data.displayName`   | string                     | Display name of the product.                                                                                                           |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `expiration`                 | string                     | Always empty since only unexpired products can be purchased.                                                                           |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcast`                  | boolean                    | Indicates whether or not the data was sent over the Extension PubSub to all instances of the Extension.                                |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`                 | object containing a string | If provided, is the key used to fetch the next page of data. If not provided, the current response is the last page of data available. |
        +------------------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, extension_id=extension_id, first=first, id=id_)
        return await self._request('GET', 'extensions/transactions', params=params)

    async def get_channel_information(self, *, broadcaster_id: str):
        """
        Gets channel information for users.

        # Authentication:
        Valid user token or app access token.

        # URL:
        `GET https://api.twitch.tv/helix/channels`

        # Required Query Parameters:
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                                                                                                                      |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | The ID of the broadcaster whose channel you want to get. To specify more than one ID, include this parameter for each broadcaster you want to get. For example, `broadcaster_id=1234&broadcaster_id=5678`. You may specify a maximum of 100 IDs. |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Optional Query Parameters:
        None

        # Return Values:
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | Parameter              | Type    | Description                                                                                                                   |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`       | string  | Twitch User ID of this channel owner.                                                                                         |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`    | string  | Broadcaster’s user login name.                                                                                                |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`     | string  | Twitch user display name of this channel owner.                                                                               |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `game_name`            | string  | Name of the game being played on the channel.                                                                                 |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`              | string  | Current game ID being played on the channel.                                                                                  |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_language` | string  | Language of the channel. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”. |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `title`                | string  | Title of the stream.                                                                                                          |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | `delay`                | integer | Stream delay in seconds.                                                                                                      |
        +------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+----------------------------------------------------------+
        | HTTP Code | Meaning                                                  |
        +-----------+----------------------------------------------------------+
        | 200       | Channel/Stream returned successfully                     |
        +-----------+----------------------------------------------------------+
        | 400       | Missing Query Parameter                                  |
        +-----------+----------------------------------------------------------+
        | 500       | Internal Server Error; Failed to get channel information |
        +-----------+----------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'channels', params=params)

    async def modify_channel_information(
        self,
        *,
        broadcaster_id: str,
        broadcaster_language: str = _empty,
        delay: int = _empty,
        game_id: str = _empty,
        title: str = _empty,
    ):
        """
        Modifies channel information for users.

        # Authentication:
        -
            OAuth Token required


        -
            Required scope: `channel:manage:broadcast`

        # URL:
        `PATCH https://api.twitch.tv/helix/channels`

        # Required Query Parameters:
        +------------------+--------+---------------------------------+
        | Parameter        | Type   | Description                     |
        +------------------+--------+---------------------------------+
        | `broadcaster_id` | string | ID of the channel to be updated |
        +------------------+--------+---------------------------------+

        # Body Parameters:
        All parameters are optional, but at least one parameter must be provided.

        +------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter              | Type    | Description                                                                                                                                  |
        +------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`              | string  | The current game ID being played on the channel. Use “0” or “” (an empty string) to unset the game.                                          |
        +------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_language` | string  | The language of the channel. A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”.       |
        +------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                | string  | The title of the stream. Value must not be an empty string.                                                                                  |
        +------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `delay`                | integer | Stream delay in seconds. Stream delay is a Twitch Partner feature; trying to set this value for other account types will return a 400 error. |
        +------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+-------------------------------------------------+
        | HTTP Code | Meaning                                         |
        +-----------+-------------------------------------------------+
        | 204       | Channel/Stream updated successfully             |
        +-----------+-------------------------------------------------+
        | 400       | Missing or invalid parameter                    |
        +-----------+-------------------------------------------------+
        | 500       | Internal server error; failed to update channel |
        +-----------+-------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        data = exclude_non_empty(broadcaster_language=broadcaster_language, delay=delay, game_id=game_id, title=title)
        return await self._request('PATCH', 'channels', params=params, data=data)

    async def get_channel_editors(self, *, broadcaster_id: str):
        """
        Gets a list of users who have editor permissions for a specific channel.

        # Authentication:
        - OAuth user token required

        - Required scope: `channel:read:editors`

        # URL:
        `GET https://api.twitch.tv/helix/channels/editors`

        # Required Query Parameters:
        +------------------+--------+----------------------------------------------------+
        | Parameter        | Type   | Description                                        |
        +------------------+--------+----------------------------------------------------+
        | `broadcaster_id` | string | Broadcaster’s user ID associated with the channel. |
        +------------------+--------+----------------------------------------------------+

        # Optional Query Parameters:
        None.

        # Response Fields:
        +--------------+--------+--------------------------------------------------------+
        | Field        | Type   | Description                                            |
        +--------------+--------+--------------------------------------------------------+
        | `user_id`    | string | User ID of the editor.                                 |
        +--------------+--------+--------------------------------------------------------+
        | `user_name`  | string | Display name of the editor.                            |
        +--------------+--------+--------------------------------------------------------+
        | `created_at` | string | Date and time the editor was given editor permissions. |
        +--------------+--------+--------------------------------------------------------+

        # Response Codes:
        +------+----------------------------------------------------------------+
        | Code | Meaning                                                        |
        +------+----------------------------------------------------------------+
        | 200  | A list of channel editors is returned.                         |
        +------+----------------------------------------------------------------+
        | 400  | Query parameter is missing.                                    |
        +------+----------------------------------------------------------------+
        | 401  | Authorization is missing or there was an OAuth token mismatch. |
        +------+----------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'channels/editors', params=params)

    async def create_custom_rewards(
        self,
        *,
        broadcaster_id: str,
        background_color: str = _empty,
        cost: int,
        global_cooldown_seconds: int = _empty,
        is_enabled: bool = _empty,
        is_global_cooldown_enabled: bool = _empty,
        is_max_per_stream_enabled: bool = _empty,
        is_max_per_user_per_stream_enabled: bool = _empty,
        is_user_input_required: bool = _empty,
        max_per_stream: int = _empty,
        max_per_user_per_stream: int = _empty,
        prompt: str = _empty,
        should_redemptions_skip_request_queue: bool = _empty,
        title: str,
    ):
        """
        Creates a Custom Reward on a channel.

        # Authentication:
        - User OAuth token

        - Required scope: `channel:manage:redemptions`

        # URL:
        `POST https://api.twitch.tv/helix/channel_points/custom_rewards`

        # Pagination:
        None.

        # Required Query Parameter:
        +------------------+--------+-----------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                 |
        +------------------+--------+-----------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        +------------------+--------+-----------------------------------------------------------------------------+

        # Required Body Parameters:
        +-----------+---------+--------------------------+
        | Parameter | Type    | Description              |
        +-----------+---------+--------------------------+
        | `title`   | string  | The title of the reward. |
        +-----------+---------+--------------------------+
        | `cost`    | integer | The cost of the reward.  |
        +-----------+---------+--------------------------+

        # Optional Body Parameters:
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                               | Type    | Description                                                                                                                                                  |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `prompt`                                | string  | The prompt for the viewer when redeeming the reward.                                                                                                         |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_enabled`                            | boolean | Is the reward currently enabled, if false the reward won’t show up to viewers. Default: true                                                                 |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `background_color`                      | string  | Custom background color for the reward. Format: Hex with # prefix. Example: `#00E5CB`.                                                                       |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_user_input_required`                | boolean | Does the user need to enter information when redeeming the reward. Default: false.                                                                           |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_max_per_stream_enabled`             | boolean | Whether a maximum per stream is enabled. Default: false.                                                                                                     |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_stream`                        | integer | The maximum number per stream if enabled. Required when any value of `is_max_per_stream_enabled` is included.                                                |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_max_per_user_per_stream_enabled`    | boolean | Whether a maximum per user per stream is enabled. Default: false.                                                                                            |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_user_per_stream`               | integer | The maximum number per user per stream if enabled. Required when any value of `is_max_per_user_per_stream_enabled` is included.                              |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_global_cooldown_enabled`            | boolean | Whether a cooldown is enabled. Default: false.                                                                                                               |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `global_cooldown_seconds`               | integer | The cooldown in seconds if enabled. Required when any value of `is_global_cooldown_enabled` is included.                                                     |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `should_redemptions_skip_request_queue` | boolean | Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status. Default: false. |
        +-----------------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                               | Type    | Description                                                                                                                                                                                             |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`                        | string  | ID of the channel the reward is for.                                                                                                                                                                    |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`                     | string  | Broadcaster’s user login name.                                                                                                                                                                          |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`                      | string  | Display name of the channel the reward is for.                                                                                                                                                          |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                                    | string  | ID of the reward.                                                                                                                                                                                       |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                                 | string  | The title of the reward.                                                                                                                                                                                |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `prompt`                                | string  | The prompt for the viewer when they are redeeming the reward.                                                                                                                                           |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`                                  | integer | The cost of the reward.                                                                                                                                                                                 |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `image`                                 | object  | Set of custom images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }, can be null if no images have been uploaded                                              |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `default_image`                         | object  | Set of default images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }                                                                                          |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `background_color`                      | string  | Custom background color for the reward. Format: Hex with # prefix. Example: `#00E5CB`.                                                                                                                  |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_enabled`                            | boolean | Is the reward currently enabled, if false the reward won’t show up to viewers                                                                                                                           |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_user_input_required`                | boolean | Does the user need to enter information when redeeming the reward                                                                                                                                       |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_stream_setting`                | object  | Whether a maximum per stream is enabled and what the maximum is. { is_enabled: bool, max_per_stream: int }                                                                                              |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_user_per_stream_setting`       | object  | Whether a maximum per user per stream is enabled and what the maximum is. { is_enabled: bool, max_per_user_per_stream: int }                                                                            |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `global_cooldown_setting`               | object  | Whether a cooldown is enabled and what the cooldown is. { is_enabled: bool, global_cooldown_seconds: int }                                                                                              |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_paused`                             | boolean | Is the reward currently paused, if true viewers can’t redeem                                                                                                                                            |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_in_stock`                           | boolean | Is the reward currently in stock, if false viewers can’t redeem                                                                                                                                         |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `should_redemptions_skip_request_queue` | boolean | Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status.                                                            |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `redemptions_redeemed_current_stream`   | integer | The number of redemptions redeemed during the current live stream. Counts against the max_per_stream_setting limit. Null if the broadcasters stream isn’t live or max_per_stream_setting isn’t enabled. |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cooldown_expires_at`                   | string  | Timestamp of the cooldown expiration. Null if the reward isn’t on cooldown.                                                                                                                             |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+-----------------------------------------------------------------+
        | HTTP Code | Meaning                                                         |
        +-----------+-----------------------------------------------------------------+
        | 200       | OK: A list of the Custom Rewards is returned                    |
        +-----------+-----------------------------------------------------------------+
        | 400       | Bad Request: Query Parameter missing or invalid                 |
        +-----------+-----------------------------------------------------------------+
        | 401       | Unauthenticated: Missing/invalid Token                          |
        +-----------+-----------------------------------------------------------------+
        | 403       | Forbidden: Channel Points are not available for the broadcaster |
        +-----------+-----------------------------------------------------------------+
        | 500       | Internal Server Error: Something bad happened on our side       |
        +-----------+-----------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        data = exclude_non_empty(
            background_color=background_color,
            cost=cost,
            global_cooldown_seconds=global_cooldown_seconds,
            is_enabled=is_enabled,
            is_global_cooldown_enabled=is_global_cooldown_enabled,
            is_max_per_stream_enabled=is_max_per_stream_enabled,
            is_max_per_user_per_stream_enabled=is_max_per_user_per_stream_enabled,
            is_user_input_required=is_user_input_required,
            max_per_stream=max_per_stream,
            max_per_user_per_stream=max_per_user_per_stream,
            prompt=prompt,
            should_redemptions_skip_request_queue=should_redemptions_skip_request_queue,
            title=title,
        )
        return await self._request('POST', 'channel_points/custom_rewards', params=params, data=data)

    async def delete_custom_reward(self, *, broadcaster_id: str, id_: str):
        """
        Deletes a Custom Reward on a channel.

        The Custom Reward specified by `id` must have been created by the `client_id` attached to the OAuth token in order to be deleted. Any `UNFULFILLED` Custom Reward Redemptions of the deleted Custom Reward will be updated to the `FULFILLED` status.

        # Authentication:
        - User OAuth token

        - Required scope: `channel:manage:redemptions`

        # URL:
        `DELETE https://api.twitch.tv/helix/channel_points/custom_rewards`

        # Pagination:
        None.

        # Required Query Parameters:
        +------------------+--------+----------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                  |
        +------------------+--------+----------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the user OAuth token.                  |
        +------------------+--------+----------------------------------------------------------------------------------------------+
        | `id`             | string | ID of the Custom Reward to delete, must match a Custom Reward on `broadcaster_id`’s channel. |
        +------------------+--------+----------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | HTTP Code | Meaning                                                                                                                     |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 204       | No Content.                                                                                                                 |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 400       | Bad Request: Query/Body Parameter missing or invalid.                                                                       |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 401       | Unauthenticated: Missing/invalid Token.                                                                                     |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 403       | Forbidden: The Custom Reward was created by a different `client_id` or Channel Points are not available for the broadcaster |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 404       | Not Found: The Custom Reward doesn't exist with the id and broadcaster_id specified                                         |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 500       | Internal Server Error: Something bad happened on our side                                                                   |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, id=id_)
        return await self._request('DELETE', 'channel_points/custom_rewards', params=params)

    async def get_custom_reward(
        self, *, broadcaster_id: str, id_: Union[str, List[str]] = _empty, only_manageable_rewards: bool = _empty
    ):
        """
        Returns a list of Custom Reward objects for the Custom Rewards on a channel.

        # Authentication:
        - User OAuth token

        - Required scope: `channel:read:redemptions`

        # URL:
        `GET https://api.twitch.tv/helix/channel_points/custom_rewards`

        # Pagination:
        None.

        There is a limit of 50 Custom Rewards on a channel at a time. This includes both enabled and disabled Custom Rewards.

        # Required Query Parameters:
        +------------------+--------+-----------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                 |
        +------------------+--------+-----------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        +------------------+--------+-----------------------------------------------------------------------------+

        # Optional Query Parameters:
        +---------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                 | Type    | Description                                                                                                                        |
        +---------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                      | string  | When used, this parameter filters the results and only returns reward objects for the Custom Rewards with matching ID. Maximum: 50 |
        +---------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------+
        | `only_manageable_rewards` | Boolean | When set to true, only returns custom rewards that the calling `client_id` can manage. Default: false.                             |
        +---------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                               | Type    | Description                                                                                                                                                                                             |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`                        | string  | ID of the channel the reward is for.                                                                                                                                                                    |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`                     | string  | Login of the channel the reward is for.                                                                                                                                                                 |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`                      | string  | Display name of the channel the reward is for.                                                                                                                                                          |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                                    | string  | ID of the reward.                                                                                                                                                                                       |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                                 | string  | The title of the reward.                                                                                                                                                                                |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `prompt`                                | string  | The prompt for the viewer when redeeming the reward.                                                                                                                                                    |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`                                  | integer | The cost of the reward.                                                                                                                                                                                 |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `image`                                 | object  | Set of custom images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }, can be null if no images have been uploaded.                                             |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `default_image`                         | object  | Set of default images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }                                                                                          |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `background_color`                      | string  | Custom background color for the reward. Format: Hex with # prefix. Example: `#00E5CB`.                                                                                                                  |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_enabled`                            | boolean | Is the reward currently enabled, if false the reward won’t show up to viewers.                                                                                                                          |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_user_input_required`                | boolean | Does the user need to enter information when redeeming the reward                                                                                                                                       |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_stream_setting`                | object  | Whether a maximum per stream is enabled and what the maximum is. { is_enabled: bool, max_per_stream: int }                                                                                              |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_user_per_stream_setting`       | object  | Whether a maximum per user per stream is enabled and what the maximum is. { is_enabled: bool, max_per_user_per_stream: int }                                                                            |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `global_cooldown_setting`               | object  | Whether a cooldown is enabled and what the cooldown is. { is_enabled: bool, global_cooldown_seconds: int }                                                                                              |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_paused`                             | boolean | Is the reward currently paused, if true viewers can’t redeem.                                                                                                                                           |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_in_stock`                           | boolean | Is the reward currently in stock, if false viewers can’t redeem.                                                                                                                                        |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `should_redemptions_skip_request_queue` | boolean | Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status.                                                            |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `redemptions_redeemed_current_stream`   | integer | The number of redemptions redeemed during the current live stream. Counts against the max_per_stream_setting limit. Null if the broadcasters stream isn’t live or max_per_stream_setting isn’t enabled. |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cooldown_expires_at`                   | string  | Timestamp of the cooldown expiration. Null if the reward isn’t on cooldown.                                                                                                                             |
        +-----------------------------------------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+-----------------------------------------------------------------+
        | HTTP Code | Meaning                                                         |
        +-----------+-----------------------------------------------------------------+
        | 200       | OK: A list of the Custom Rewards is returned                    |
        +-----------+-----------------------------------------------------------------+
        | 400       | Bad Request: Query Parameter missing or invalid                 |
        +-----------+-----------------------------------------------------------------+
        | 401       | Unauthenticated: Missing/invalid Token                          |
        +-----------+-----------------------------------------------------------------+
        | 403       | Forbidden: Channel Points are not available for the broadcaster |
        +-----------+-----------------------------------------------------------------+
        | 404       | Not Found: No Custom Rewards with the specified IDs were found  |
        +-----------+-----------------------------------------------------------------+
        | 500       | Internal Server Error: Something bad happened on our side       |
        +-----------+-----------------------------------------------------------------+
        """
        params = exclude_non_empty(
            broadcaster_id=broadcaster_id, id=id_, only_manageable_rewards=only_manageable_rewards
        )
        return await self._request('GET', 'channel_points/custom_rewards', params=params)

    async def get_custom_reward_redemption(
        self,
        *,
        after: str = _empty,
        broadcaster_id: str,
        first: int = _empty,
        id_: Union[str, List[str]] = _empty,
        reward_id: str,
        sort: str = _empty,
        status: str = _empty,
    ):
        """
        Returns Custom Reward Redemption objects for a Custom Reward on a channel that was created by the same
        `client_id`.

        Developers only have access to get and update redemptions for the rewards created programmatically by the same `client_id`.

        # Authentication:
        - User OAuth token

        - Required scope: `channel:read:redemptions`

        # URL:
        `GET https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions`

        # Pagination:
        Maximum of 50 per page. Returns oldest first.

        # Required Query Parameters:
        +------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                          |
        +------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the user OAuth token.                                                                          |
        +------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `reward_id`      | string | When ID is not provided, this parameter returns paginated Custom Reward Redemption objects for redemptions of the Custom Reward with ID `reward_id`. |
        +------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Optional Query Parameters:
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type    | Description                                                                                                                                                                                                                                                                                                                      |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`      | string  | When used, this param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID. Maximum: 50                                                                                                                                                                                    |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`  | string  | When id is not provided, this param is required and filters the paginated Custom Reward Redemption objects for redemptions with the matching status. Can be one of UNFULFILLED, FULFILLED or CANCELED                                                                                                                            |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `sort`    | string  | Sort order of redemptions returned when getting the paginated Custom Reward Redemption objects for a reward. One of: OLDEST, NEWEST. Default: OLDEST.                                                                                                                                                                            |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries without ID. If an ID is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the pagination response field of a prior query. |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | integer | Number of results to be returned when getting the paginated Custom Reward Redemption objects for a reward. Limit: 50. Default: 20.                                                                                                                                                                                               |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Type   | Description                                                                                                                                                |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`    | string | The id of the broadcaster that the reward belongs to.                                                                                                      |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login` | string | Broadcaster’s user login name.                                                                                                                             |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`  | string | The display name of the broadcaster that the reward belongs to.                                                                                            |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                | string | The ID of the redemption.                                                                                                                                  |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login`        | string | The login of the user who redeemed the reward.                                                                                                             |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`           | string | The ID of the user that redeemed the reward.                                                                                                               |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`         | string | The display name of the user that redeemed the reward.                                                                                                     |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `reward`            | object | Basic information about the Custom Reward that was redeemed at the time it was redeemed. { “id”: string, “title”: string, “prompt”: string, “cost”: int, } |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_input`        | string | The user input provided. Empty string if not provided.                                                                                                     |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`            | string | One of UNFULFILLED, FULFILLED or CANCELED                                                                                                                  |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `redeemed_at`       | string | RFC3339 timestamp of when the reward was redeemed.                                                                                                         |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | HTTP Code | Meaning                                                                                                                     |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 200       | Ok: A list of the Custom Reward Redemptions is returned                                                                     |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 400       | Bad Request: Query Parameter missing or invalid                                                                             |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 401       | Unauthenticated: Missing/invalid Token                                                                                      |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 403       | Forbidden: The Custom Reward was created by a different `client_id` or Channel Points are not available for the broadcaster |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 404       | Not Found: No Custom Reward Redemptions with the specified ids were found                                                   |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 500       | Internal Server Error: Something bad happened on our side                                                                   |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after,
            broadcaster_id=broadcaster_id,
            first=first,
            id=id_,
            reward_id=reward_id,
            sort=sort,
            status=status,
        )
        return await self._request('GET', 'channel_points/custom_rewards/redemptions', params=params)

    async def update_custom_reward(
        self,
        *,
        broadcaster_id: str,
        id_: str,
        background_color: str = _empty,
        cost: int = _empty,
        global_cooldown_seconds: int = _empty,
        is_enabled: bool = _empty,
        is_global_cooldown_enabled: bool = _empty,
        is_max_per_stream_enabled: bool = _empty,
        is_max_per_user_per_stream_enabled: bool = _empty,
        is_paused: bool = _empty,
        is_user_input_required: bool = _empty,
        max_per_stream: int = _empty,
        max_per_user_per_stream: int = _empty,
        prompt: str = _empty,
        should_redemptions_skip_request_queue: bool = _empty,
        title: str = _empty,
    ):
        """
        Updates a Custom Reward created on a channel.

        The Custom Reward specified by `id` must have been created by the `client_id` attached to the user OAuth token.

        # Authentication:
        - User OAuth token

        - Required scope: `channel:manage:redemptions`

        # URL:
        `PATCH https://api.twitch.tv/helix/channel_points/custom_rewards`

        # Pagination:
        None.

        # Required Query Parameters:
        +------------------+--------+-------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                           |
        +------------------+--------+-------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the user OAuth token.                           |
        +------------------+--------+-------------------------------------------------------------------------------------------------------+
        | `id`             | string | ID of the Custom Reward to update. Must match a Custom Reward on the channel of the `broadcaster_id`. |
        +------------------+--------+-------------------------------------------------------------------------------------------------------+

        # Optional Body Values:
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                               | Type    | Description                                                                                                                                  |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                                 | string  | The title of the reward.                                                                                                                     |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `prompt`                                | string  | The prompt for the viewer when they are redeeming the reward.                                                                                |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`                                  | integer | The cost of the reward.                                                                                                                      |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `background_color`                      | string  | Custom background color for the reward as a hexadecimal value. Example: `#00E5CB`.                                                           |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_enabled`                            | boolean | Is the reward currently enabled, if false the reward won’t show up to viewers.                                                               |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_user_input_required`                | boolean | Does the user need to enter information when redeeming the reward.                                                                           |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_max_per_stream_enabled`             | boolean | Whether a maximum per stream is enabled. Required when any value of `max_per_stream` is included.                                            |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_stream`                        | integer | The maximum number per stream if enabled. Required when any value of `is_max_per_stream_enabled` is included.                                |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_max_per_user_per_stream_enabled`    | boolean | Whether a maximum per user per stream is enabled. Required when any value of `max_per_user_per_stream` is included.                          |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_user_per_stream`               | integer | The maximum number per user per stream if enabled. Required when any value of `is_max_per_user_per_stream_enabled` is included.              |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_global_cooldown_enabled`            | boolean | Whether a cooldown is enabled. Required when any value of `global_cooldown_seconds` is included.                                             |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `global_cooldown_seconds`               | integer | The cooldown in seconds if enabled. Required when any value of `is_global_cooldown_enabled` is included.                                     |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_paused`                             | boolean | Is the reward currently paused, if true viewers cannot redeem.                                                                               |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+
        | `should_redemptions_skip_request_queue` | boolean | Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status. |
        +-----------------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                               | Type    | Description                                                                                                                                                                                                 |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`                        | string  | ID of the channel the reward is for.                                                                                                                                                                        |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`                     | string  | Broadcaster’s user login name.                                                                                                                                                                              |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`                      | string  | Display name of the channel the reward is for.                                                                                                                                                              |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                                    | string  | ID of the reward.                                                                                                                                                                                           |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                                 | string  | The title of the reward.                                                                                                                                                                                    |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `prompt`                                | string  | The prompt for the viewer when they are redeeming the reward.                                                                                                                                               |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`                                  | integer | The cost of the reward.                                                                                                                                                                                     |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `image`                                 | object  | Set of custom images of 1x, 2x, and 4x sizes for the reward, can be null if no images have been uploaded.                                                                                                   |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `default_image`                         | object  | Set of default images of 1x, 2x, and 4x sizes for the reward.                                                                                                                                               |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `background_color`                      | string  | Custom background color for the reward as a hexadecimal value. Example: `#00E5CB`.                                                                                                                          |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_enabled`                            | boolean | Is the reward currently enabled, if false the reward won’t show up to viewers.                                                                                                                              |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_user_input_required`                | boolean | Does the user need to enter information when redeeming the reward.                                                                                                                                          |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_stream_setting`                | object  | Whether a maximum per stream is enabled and what the maximum is.                                                                                                                                            |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_per_user_per_stream_setting`       | object  | Whether a maximum per user per stream is enabled and what the maximum is.                                                                                                                                   |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `global_cooldown_setting`               | object  | Whether a cooldown is enabled and what the cooldown is.                                                                                                                                                     |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_paused`                             | boolean | Is the reward currently paused, if true viewers cannot redeem.                                                                                                                                              |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_in_stock`                           | boolean | Is the reward currently in stock, if false viewers can’t redeem.                                                                                                                                            |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `should_redemptions_skip_request_queue` | boolean | Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status.                                                                |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `redemptions_redeemed_current_stream`   | integer | The number of redemptions redeemed during the current live stream. Counts against the max_per_stream_setting limit. `null` if the broadcasters stream is not live or max_per_stream_setting is not enabled. |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cooldown_expires_at`                   | string  | Timestamp of the cooldown expiration. `null` if the reward is not on cooldown.                                                                                                                              |
        +-----------------------------------------+---------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | HTTP Code | Meaning                                                                                                                                                          |
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 200       | OK: A list of the Custom Rewards is returned.                                                                                                                    |
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 400       | Bad Request: Query Parameter missing or invalid. This includes the required parameter pairs to set max per stream, max per user per stream, and global cooldown. |
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 401       | Unauthenticated: Missing/invalid Token.                                                                                                                          |
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 403       | Forbidden: The Custom Reward was created by a different `client_id` or Channel Points are not available for the broadcaster.                                     |
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 404       | Not Found: The Custom Reward does not exist with the `id` and `broadcaster_id` specified.                                                                        |
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 500       | Internal Server Error: Could not update the Custom Reward.                                                                                                       |
        +-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, id=id_)
        data = exclude_non_empty(
            background_color=background_color,
            cost=cost,
            global_cooldown_seconds=global_cooldown_seconds,
            is_enabled=is_enabled,
            is_global_cooldown_enabled=is_global_cooldown_enabled,
            is_max_per_stream_enabled=is_max_per_stream_enabled,
            is_max_per_user_per_stream_enabled=is_max_per_user_per_stream_enabled,
            is_paused=is_paused,
            is_user_input_required=is_user_input_required,
            max_per_stream=max_per_stream,
            max_per_user_per_stream=max_per_user_per_stream,
            prompt=prompt,
            should_redemptions_skip_request_queue=should_redemptions_skip_request_queue,
            title=title,
        )
        return await self._request('PATCH', 'channel_points/custom_rewards', params=params, data=data)

    async def update_redemption_status(
        self, *, broadcaster_id: str, id_: Union[str, List[str]], reward_id: str, status: str
    ):
        """
        Updates the status of Custom Reward Redemption objects on a channel that are in the UNFULFILLED status.

        The Custom Reward Redemption specified by `id` must be for a Custom Reward created by the `client_id` attached to the user OAuth token.

        # Authentication:
        - User OAuth token

        - Required scope: `channel:manage:redemptions`

        # URL:
        `PATCH https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions`

        # Pagination:
        None.

        # Required Query Parameters:
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                     |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------+
        | `id`             | string | ID of the Custom Reward Redemption to update, must match a Custom Reward Redemption on `broadcaster_id`’s channel. Maximum: 50. |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the user OAuth token.                                                     |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------+
        | `reward_id`      | string | ID of the Custom Reward the redemptions to be updated are for.                                                                  |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------+

        # Required Body Values:
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                |
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`  | string | The new status to set redemptions to. Can be either FULFILLED or CANCELED. Updating to CANCELED will refund the user their Channel Points. |
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Type   | Description                                                                                                                                                |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`    | string | The ID of the broadcaster that the reward belongs to.                                                                                                      |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login` | string | Broadcaster’s user login name.                                                                                                                             |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`  | string | The display name of the broadcaster that the reward belongs to.                                                                                            |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                | string | The ID of the redemption.                                                                                                                                  |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`           | string | The ID of the user that redeemed the reward.                                                                                                               |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`         | string | The display name of the user that redeemed the reward.                                                                                                     |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login`        | string | The login of the user that redeemed the reward.                                                                                                            |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `reward`            | object | Basic information about the Custom Reward that was redeemed at the time it was redeemed. { “id”: string, “title”: string, “prompt”: string, “cost”: int, } |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_input`        | string | The user input provided. Null if not provided.                                                                                                             |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`            | string | One of UNFULFILLED, FULFILLED or CANCELED.                                                                                                                 |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `redeemed_at`       | string | RFC3339 timestamp of when the reward was redeemed.                                                                                                         |
        +---------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | HTTP Code | Meaning                                                                                                                     |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 200       | OK: A list of the updated Custom Reward Redemptions is returned                                                             |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 400       | Bad Request: Query Parameter missing or invalid                                                                             |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 401       | Unauthenticated: Missing/invalid Token                                                                                      |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 403       | Forbidden: The Custom Reward was created by a different `client_id` or Channel Points are not available for the broadcaster |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 404       | Not Found: No Custom Reward Redemptions with the specified IDs were found with a status of `UNFULFILLED`.                   |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        | 500       | Internal Server Error: Something bad happened on our side                                                                   |
        +-----------+-----------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, id=id_, reward_id=reward_id)
        data = exclude_non_empty(status=status)
        return await self._request('PATCH', 'channel_points/custom_rewards/redemptions', params=params, data=data)

    async def get_channel_emotes(self, *, broadcaster_id: str):
        """
        Gets all emotes that the specified Twitch channel created. Broadcasters create these custom emotes for users who
        subscribe to or follow the channel, or cheer Bits in the channel’s chat window. For information about the custom
        emotes, see subscriber emotes, Bits tier emotes, and follower emotes.

        NOTE: With the exception of custom follower emotes, users may use custom emotes in any Twitch chat.

        Learn More

        # Authorization:
        Requires a user or application OAuth access token.

        # URL:
        `GET https://api.twitch.tv/helix/chat/emotes`

        # Required Query Parameter:
        +------------------+--------+---------------------------------------------------------------+
        | Parameter        | Type   | Description                                                   |
        +------------------+--------+---------------------------------------------------------------+
        | `broadcaster_id` | string | An ID that identifies the broadcaster to get the emotes from. |
        +------------------+--------+---------------------------------------------------------------+

        # Response Fields:
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Type         | Description                                                                                                                                                                                                                                                                                                                                       |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`         | object array | A list of emotes that the specified channel created.                                                                                                                                                                                                                                                                                              |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`           | string       | An ID that identifies the emote.                                                                                                                                                                                                                                                                                                                  |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `name`         | string       | The name of the emote. This is the name that viewers type in the chat window to get the emote to appear.                                                                                                                                                                                                                                          |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `images`       | object       | Contains the image URLs for the emote. These image URLs will always provide a static (i.e., non-animated) emote image with a light background. NOTE: The preference is for you to use the templated URL in the `template` field to fetch the image instead of using these URLs.                                                                   |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_1x`       | string       | A URL to the small version (28px x 28px) of the emote.                                                                                                                                                                                                                                                                                            |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_2x`       | string       | A URL to the medium version (56px x 56px) of the emote.                                                                                                                                                                                                                                                                                           |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_4x`       | string       | A URL to the large version (112px x 112px) of the emote.                                                                                                                                                                                                                                                                                          |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tier`         | string       | The subscriber tier at which the emote is unlocked. This field contains the tier information only if `emote_type` is set to `subscriptions`, otherwise, it’s an empty string.                                                                                                                                                                     |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `emote_type`   | string       | The type of emote. The possible values are:                                                                                                                                                                                                                                                                                                       |
        |                |              | - bitstier — Indicates a custom Bits tier emote.                                                                                                                                                                                                                                                                                                  |
        |                |              | - follower — Indicates a custom follower emote.                                                                                                                                                                                                                                                                                                   |
        |                |              | - subscriptions — Indicates a custom subscriber emote.                                                                                                                                                                                                                                                                                            |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `emote_set_id` | string       | An ID that identifies the emote set that the emote belongs to.                                                                                                                                                                                                                                                                                    |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `format`       | string array | The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only `static`. But if it’s available as a static PNG and an animated GIF, the array contains `static` and `animated`. The possible formats are:                                                                       |
        |                |              | - animated — Indicates an animated GIF is available for this emote.                                                                                                                                                                                                                                                                               |
        |                |              | - static — Indicates a static PNG file is available for this emote.                                                                                                                                                                                                                                                                               |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `scale`        | string array | The sizes that the emote is available in. For example, if the emote is available in small and medium sizes, the array contains 1.0 and 2.0. Possible sizes are:                                                                                                                                                                                   |
        |                |              | - 1.0 — A small version (28px x 28px) is available.                                                                                                                                                                                                                                                                                               |
        |                |              | - 2.0 — A medium version (56px x 56px) is available.                                                                                                                                                                                                                                                                                              |
        |                |              | - 3.0 — A large version (112px x 112px) is available.                                                                                                                                                                                                                                                                                             |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `theme_mode`   | string array | The background themes that the emote is available in. Possible themes are:                                                                                                                                                                                                                                                                        |
        |                |              | - dark                                                                                                                                                                                                                                                                                                                                            |
        |                |              | - light                                                                                                                                                                                                                                                                                                                                           |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `template`     | string       | A templated URL. Use the values from `id`, `format`, `scale`, and `theme_mode` to replace the like-named placeholder strings in the templated URL to create a CDN (content delivery network) URL that you use to fetch the emote. For information about what the template looks like and how to use it to fetch emotes, see Emote CDN URL format. |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                  |
        +------+------------------------------------------------------------------------------------------+
        | 200  | Successfully returned the custom emotes for the specified broadcaster.                   |
        +------+------------------------------------------------------------------------------------------+
        | 400  | The request was invalid.                                                                 |
        +------+------------------------------------------------------------------------------------------+
        | 401  | The caller failed authentication. Verify that your access token and client ID are valid. |
        +------+------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'chat/emotes', params=params)

    async def get_global_emotes(self):
        """
        Gets all global emotes. Global emotes are Twitch-created emoticons that users can use in any Twitch chat.

        Learn More

        # Authorization:
        Requires a user or application OAuth access token.

        # URL:
        `GET https://api.twitch.tv/helix/chat/emotes/global`

        # Response Fields:
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter    | Type         | Description                                                                                                                                                                                                                                                                                                                                       |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`       | object array | The list of global emotes.                                                                                                                                                                                                                                                                                                                        |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`         | string       | An ID that identifies the emote.                                                                                                                                                                                                                                                                                                                  |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `name`       | string       | The name of the emote. This is the name that viewers type in the chat window to get the emote to appear.                                                                                                                                                                                                                                          |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `images`     | object       | Contains the image URLs for the emote. These image URLs will always provide a static (i.e., non-animated) emote image with a light background. NOTE: The preference is for you to use the templated URL in the `template` field to fetch the image instead of using these URLs.                                                                   |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_1x`     | string       | A URL to the small version (28px x 28px) of the emote.                                                                                                                                                                                                                                                                                            |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_2x`     | string       | A URL to the medium version (56px x 56px) of the emote.                                                                                                                                                                                                                                                                                           |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_4x`     | string       | A URL to the large version (112px x 112px) of the emote.                                                                                                                                                                                                                                                                                          |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `format`     | string array | The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only `static`. But if it’s available as a static PNG and an animated GIF, the array contains `static` and `animated`. The possible formats are:                                                                       |
        |              |              | - animated — Indicates an animated GIF is available for this emote.                                                                                                                                                                                                                                                                               |
        |              |              | - static — Indicates a static PNG file is available for this emote.                                                                                                                                                                                                                                                                               |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `scale`      | string array | The sizes that the emote is available in. For example, if the emote is available in small and medium sizes, the array contains 1.0 and 2.0. Possible sizes are:                                                                                                                                                                                   |
        |              |              | - 1.0 — A small version (28px x 28px) is available.                                                                                                                                                                                                                                                                                               |
        |              |              | - 2.0 — A medium version (56px x 56px) is available.                                                                                                                                                                                                                                                                                              |
        |              |              | - 3.0 — A large version (112px x 112px) is available.                                                                                                                                                                                                                                                                                             |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `theme_mode` | string array | The background themes that the emote is available in. Possible themes are:                                                                                                                                                                                                                                                                        |
        |              |              | - dark                                                                                                                                                                                                                                                                                                                                            |
        |              |              | - light                                                                                                                                                                                                                                                                                                                                           |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `template`   | string       | A templated URL. Use the values from `id`, `format`, `scale`, and `theme_mode` to replace the like-named placeholder strings in the templated URL to create a CDN (content delivery network) URL that you use to fetch the emote. For information about what the template looks like and how to use it to fetch emotes, see Emote CDN URL format. |
        +--------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                  |
        +------+------------------------------------------------------------------------------------------+
        | 200  | Successfully returned the global emotes.                                                 |
        +------+------------------------------------------------------------------------------------------+
        | 400  | The request was invalid.                                                                 |
        +------+------------------------------------------------------------------------------------------+
        | 401  | The caller failed authentication. Verify that your access token and client ID are valid. |
        +------+------------------------------------------------------------------------------------------+
        """
        return await self._request('GET', 'chat/emotes/global')

    async def get_emote_sets(self, *, emote_set_id: str):
        """
        Gets emotes for one or more specified emote sets.

        An emote set groups emotes that have a similar context. For example, Twitch places all the subscriber emotes that a broadcaster uploads for their channel in the same emote set.

        Learn More

        # Authorization:
        Requires a user or application OAuth access token.

        # URL:
        `GET https://api.twitch.tv/helix/chat/emotes/set`

        # Required Query Parameter:
        +----------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Type   | Description                                                                                                                                                                             |
        +----------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `emote_set_id` | string | An ID that identifies the emote set. Include the parameter for each emote set you want to get. For example, `emote_set_id=1234&emote_set_id=5678`. You may specify a maximum of 25 IDs. |
        +----------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Type         | Description                                                                                                                                                                                                                                                                                                                                       |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`         | object array | The list of emotes found in the specified emote sets.                                                                                                                                                                                                                                                                                             |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`           | string       | An ID that identifies the emote.                                                                                                                                                                                                                                                                                                                  |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `name`         | string       | The name of the emote. This is the name that viewers type in the chat window to get the emote to appear.                                                                                                                                                                                                                                          |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `images`       | object       | Contains the image URLs for the emote. These image URLs will always provide a static (i.e., non-animated) emote image with a light background. NOTE: The preference is for you to use the templated URL in the `template` field to fetch the image instead of using these URLs.                                                                   |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_1x`       | string       | A URL to the small version (28px x 28px) of the emote.                                                                                                                                                                                                                                                                                            |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_2x`       | string       | A URL to the medium version (56px x 56px) of the emote.                                                                                                                                                                                                                                                                                           |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url_4x`       | string       | A URL to the large version (112px x 112px) of the emote.                                                                                                                                                                                                                                                                                          |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `emote_type`   | string       | The type of emote. The possible values are:                                                                                                                                                                                                                                                                                                       |
        |                |              | - bitstier — Indicates a Bits tier emote.                                                                                                                                                                                                                                                                                                         |
        |                |              | - follower — Indicates a follower emote.                                                                                                                                                                                                                                                                                                          |
        |                |              | - subscriptions — Indicates a subscriber emote.                                                                                                                                                                                                                                                                                                   |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `emote_set_id` | string       | An ID that identifies the emote set that the emote belongs to.                                                                                                                                                                                                                                                                                    |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `owner_id`     | string       | The ID of the broadcaster who owns the emote.                                                                                                                                                                                                                                                                                                     |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `format`       | string array | The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only `static`. But if it’s available as a static PNG and an animated GIF, the array contains `static` and `animated`. The possible formats are:                                                                       |
        |                |              | - animated — Indicates an animated GIF is available for this emote.                                                                                                                                                                                                                                                                               |
        |                |              | - static — Indicates a static PNG file is available for this emote.                                                                                                                                                                                                                                                                               |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `scale`        | string array | The sizes that the emote is available in. For example, if the emote is available in small and medium sizes, the array contains 1.0 and 2.0. Possible sizes are:                                                                                                                                                                                   |
        |                |              | - 1.0 — A small version (28px x 28px) is available.                                                                                                                                                                                                                                                                                               |
        |                |              | - 2.0 — A medium version (56px x 56px) is available.                                                                                                                                                                                                                                                                                              |
        |                |              | - 3.0 — A large version (112px x 112px) is available.                                                                                                                                                                                                                                                                                             |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `theme_mode`   | string array | The background themes that the emote is available in. Possible themes are:                                                                                                                                                                                                                                                                        |
        |                |              | - dark                                                                                                                                                                                                                                                                                                                                            |
        |                |              | - light                                                                                                                                                                                                                                                                                                                                           |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `template`     | string       | A templated URL. Use the values from `id`, `format`, `scale`, and `theme_mode` to replace the like-named placeholder strings in the templated URL to create a CDN (content delivery network) URL that you use to fetch the emote. For information about what the template looks like and how to use it to fetch emotes, see Emote CDN URL format. |
        +----------------+--------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                  |
        +------+------------------------------------------------------------------------------------------+
        | 200  | Successfully returned emotes for the specified emote set.                                |
        +------+------------------------------------------------------------------------------------------+
        | 400  | The request was invalid.                                                                 |
        +------+------------------------------------------------------------------------------------------+
        | 401  | The caller failed authentication. Verify that your access token and client ID are valid. |
        +------+------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(emote_set_id=emote_set_id)
        return await self._request('GET', 'chat/emotes/set', params=params)

    async def get_channel_chat_badges(self, *, broadcaster_id: str):
        """
        Gets a list of custom chat badges that can be used in chat for the specified channel. This includes subscriber
        badges and Bit badges.

        # Authorization:
        - User OAuth Token or App Access Token

        # URL:
        `GET https://api.twitch.tv/helix/chat/badges`

        # Pagination Support:
        None.

        # Required Query Parameter:
        +------------------+--------+------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                        |
        +------------------+--------+------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | The broadcaster whose chat badges are being requested. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                                                    |
        |                  |        | Maximum: 1                                                                                                                         |
        +------------------+--------+------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +----------------------------+------------------+------------------------------------------+
        | Parameter                  | Type             | Description                              |
        +----------------------------+------------------+------------------------------------------+
        | `data`                     | Array of objects | An array of chat badge sets.             |
        +----------------------------+------------------+------------------------------------------+
        | `set.set_id`               | string           | ID for the chat badge set.               |
        +----------------------------+------------------+------------------------------------------+
        | `set.versions`             | Array of objects | Contains chat badge objects for the set. |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.id`           | string           | ID of the chat badge version.            |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.image_url_1x` | string           | Small image URL.                         |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.image_url_2x` | string           | Medium image URL.                        |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.image_url_4x` | string           | Large image URL.                         |
        +----------------------------+------------------+------------------------------------------+

        # Response Codes:
        +------+--------------------------------------------+
        | Code | Meaning                                    |
        +------+--------------------------------------------+
        | 200  | Channel chat badges returned successfully. |
        +------+--------------------------------------------+
        | 400  | Request was invalid.                       |
        +------+--------------------------------------------+
        | 401  | Authorization failed.                      |
        +------+--------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'chat/badges', params=params)

    async def get_global_chat_badges(self):
        """
        Gets a list of chat badges that can be used in chat for any channel.

        # Authorization:
        - User OAuth Token or App Access Token

        # URL:
        `GET https://api.twitch.tv/helix/chat/badges/global`

        # Pagination Support:
        None.

        # Return Values:
        +----------------------------+------------------+------------------------------------------+
        | Parameter                  | Type             | Description                              |
        +----------------------------+------------------+------------------------------------------+
        | `data`                     | Array of objects | An array of chat badge sets.             |
        +----------------------------+------------------+------------------------------------------+
        | `set.set_id`               | string           | ID for the chat badge set.               |
        +----------------------------+------------------+------------------------------------------+
        | `set.versions`             | Array of objects | Contains chat badge objects for the set. |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.id`           | string           | ID of the chat badge version.            |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.image_url_1x` | string           | Small image URL.                         |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.image_url_2x` | string           | Medium image URL.                        |
        +----------------------------+------------------+------------------------------------------+
        | `set.version.image_url_4x` | string           | Large image URL.                         |
        +----------------------------+------------------+------------------------------------------+

        # Response Codes:
        +------+-------------------------------------------+
        | Code | Meaning                                   |
        +------+-------------------------------------------+
        | 200  | Global chat badges returned successfully. |
        +------+-------------------------------------------+
        | 400  | Request was invalid.                      |
        +------+-------------------------------------------+
        | 401  | Authorization failed.                     |
        +------+-------------------------------------------+
        """
        return await self._request('GET', 'chat/badges/global')

    async def get_chat_settings(self, *, broadcaster_id: str, moderator_id: str = _empty):
        """
        NEW Gets the broadcaster’s chat settings.

        For an overview of chat settings, see Chat Commands for Broadcasters and Moderators and Moderator Preferences.

        # Authorization:
        Requires an App access token. However, to include the `non_moderator_chat_delay` or `non_moderator_chat_delay_duration` settings in the response, you must specify a User access token with scope set to `moderator:read:chat_settings`.

        # URL:
        `GET https://api.twitch.tv/helix/chat/settings`

        # Query Parameters:
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                        |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster whose chat settings you want to get.                                                                                     |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | No       | String | Required only to access the `non_moderator_chat_delay` or `non_moderator_chat_delay_duration` settings.                                            |
        |                |          |        |                                                                                                                                                    |
        |                |          |        | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token. |
        |                |          |        |                                                                                                                                                    |
        |                |          |        | If the broadcaster wants to get their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.       |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field                             | Type         | Description                                                                                                                                                                                                              |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | data                              | object array | The list of chat settings. The list contains a single object with all the settings.                                                                                                                                      |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id                    | String       | The ID of the broadcaster specified in the request.                                                                                                                                                                      |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | emote_mode                        | Boolean      | A Boolean value that determines whether chat messages must contain only emotes. Is true, if only messages that are 100% emotes are allowed; otherwise, false.                                                            |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | follower_mode                     | Boolean      | A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed.                                                                                   |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster restricts the chat room to followers only; otherwise, false.                                                                                                                                 |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | See `follower_mode_duration` for how long the followers must have followed the broadcaster to participate in the chat room.                                                                                              |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | follower_mode_duration            | Integer      | The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room. See `follower_mode`.                                                                              |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is null if `follower_mode` is false.                                                                                                                                                                                     |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id                      | String       | The moderator’s ID. The response includes this field only if the request specifies a User access token that includes the  moderator:read:chat_settings scope.                                                            |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | non_moderator_chat_delay          | Boolean      | A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room. This gives chat moderators and bots a chance to remove them before viewers can see the message. |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster applies a delay; otherwise, false.                                                                                                                                                           |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | See `non_moderator_chat_delay_duration` for the length of the delay.                                                                                                                                                     |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | The response includes this field only if the request specifies a User access token that includes the  moderator:read:chat_settings scope.                                                                                |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | non_moderator_chat_delay_duration | Integer      | The amount of time, in seconds, that messages are delayed from appearing in chat. See `non_moderator_chat_delay`.                                                                                                        |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is null if non_moderator_chat_delay is false.                                                                                                                                                                            |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | The response includes this field only if the request specifies a User access token that includes the  moderator:read:chat_settings scope.                                                                                |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | slow_mode                         | Boolean      | A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages.                                                                                            |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster applies a delay; otherwise, false.                                                                                                                                                           |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | See `slow_mode_wait_time` for the delay.                                                                                                                                                                                 |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | slow_mode_wait_time               | Integer      | The amount of time, in seconds, that users need to wait between sending messages. See `slow_mode`.                                                                                                                       |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is null if slow_mode is false.                                                                                                                                                                                           |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | subscriber_mode                   | Boolean      | A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room.                                                                                                |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster restricts the chat room to subscribers only; otherwise, false.                                                                                                                               |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | unique_chat_mode                  | Boolean      | A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room.                                                                                                    |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster requires unique messages only; otherwise, false.                                                                                                                                             |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-------------------------+
        | Code | Meaning                 |
        +------+-------------------------+
        | 200  | Success.                |
        +------+-------------------------+
        | 400  | Malformed request.      |
        +------+-------------------------+
        | 401  | Authentication failure. |
        +------+-------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        return await self._request('GET', 'chat/settings', params=params)

    async def update_chat_settings(
        self,
        *,
        broadcaster_id: str,
        moderator_id: str,
        emote_mode: bool = _empty,
        follower_mode: bool = _empty,
        follower_mode_duration: int = _empty,
        non_moderator_chat_delay: bool = _empty,
        non_moderator_chat_delay_duration: int = _empty,
        slow_mode: bool = _empty,
        slow_mode_wait_time: int = _empty,
        subscriber_mode: bool = _empty,
        unique_chat_mode: bool = _empty,
    ):
        """
        NEW Updates the broadcaster’s chat settings.

        # Authentication:
        Requires a User access token with scope set to `moderator:manage:chat_settings`.

        # URL:
        `PATCH https://api.twitch.tv/helix/chat/settings`

        # Query Parameters:
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                        |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster whose chat settings you want to update. This ID must match the user ID associated with the user OAuth token.             |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token. |
        |                |          |        |                                                                                                                                                    |
        |                |          |        | If the broadcaster wants to update their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.    |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+

        # Request Body:
        Specify only those fields that you want to update.

        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field                             | Type    | Description                                                                                                                                                                                                              |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | emote_mode                        | Boolean | A Boolean value that determines whether chat messages must contain only emotes.                                                                                                                                          |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | Set to true, if only messages that are 100% emotes are allowed; otherwise, false. Default is false.                                                                                                                      |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | follower_mode                     | Boolean | A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed.                                                                                   |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | Set to true, if the broadcaster restricts the chat room to followers only; otherwise, false. Default is true.                                                                                                            |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | See `follower_mode_duration` for how long the followers must have followed the broadcaster to participate in the chat room.                                                                                              |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | follower_mode_duration            | Integer | The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room (see `follower_mode`).                                                                             |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | You may specify a value in the range: 0 (no restriction) through 129600 (3 months). The default is 0.                                                                                                                    |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | non_moderator_chat_delay          | Boolean | A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room. This gives chat moderators and bots a chance to remove them before viewers can see the message. |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | Set to true, if the broadcaster applies a delay; otherwise, false. Default is false.                                                                                                                                     |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | See `non_moderator_chat_delay_duration` for the length of the delay.                                                                                                                                                     |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | non_moderator_chat_delay_duration | Integer | The amount of time, in seconds, that messages are delayed from appearing in chat.                                                                                                                                        |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | Possible values are:                                                                                                                                                                                                     |
        |                                   |         | - 2  —  2 second delay (recommended)                                                                                                                                                                                     |
        |                                   |         | - 4  —  4 second delay                                                                                                                                                                                                   |
        |                                   |         | - 6  —  6 second delaySee `non_moderator_chat_delay`.                                                                                                                                                                    |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | slow_mode                         | Boolean | A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages.                                                                                            |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | Set to true, if the broadcaster applies a wait period messages; otherwise, false. Default is false.                                                                                                                      |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | See `slow_mode_wait_time` for the delay.                                                                                                                                                                                 |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | slow_mode_wait_time               | Integer | The amount of time, in seconds, that users need to wait between sending messages (see `slow_mode`).                                                                                                                      |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | You may specify a value in the range: 3 (3 second delay) through 120 (2 minute delay). The default is 30 seconds.                                                                                                        |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | subscriber_mode                   | Boolean | A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room.                                                                                                |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | Set to true, if the broadcaster restricts the chat room to subscribers only; otherwise, false. Default is false.                                                                                                         |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | unique_chat_mode                  | Boolean | A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room.                                                                                                    |
        |                                   |         |                                                                                                                                                                                                                          |
        |                                   |         | Set to true, if the broadcaster requires unique messages only; otherwise, false. Default is false.                                                                                                                       |
        +-----------------------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field                             | Type         | Description                                                                                                                                                                                                              |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | data                              | object array | The list of chat settings. The list will contain the single object with all the settings.                                                                                                                                |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id                    | String       | The ID of the broadcaster specified in the request.                                                                                                                                                                      |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | emote_mode                        | Boolean      | A Boolean value that determines whether chat messages must contain only emotes. Is true, if only messages that are 100% emotes are allowed; otherwise, false.                                                            |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | follower_mode                     | Boolean      | A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed.                                                                                   |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster restricts the chat room to followers only; otherwise, false.                                                                                                                                 |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | See `follower_mode_duration` for how long the followers must have followed the broadcaster to participate in the chat room.                                                                                              |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | follower_mode_duration            | Integer      | The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room. See `follower_mode`.                                                                              |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is null if `follower_mode` is false.                                                                                                                                                                                     |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id                      | String       | The ID of the moderator specified in the request.                                                                                                                                                                        |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | non_moderator_chat_delay          | Boolean      | A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room. This gives chat moderators and bots a chance to remove them before viewers can see the message. |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster applies a delay; otherwise, false.                                                                                                                                                           |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | See `non_moderator_chat_delay_duration` for the length of the delay.                                                                                                                                                     |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | non_moderator_chat_delay_duration | Integer      | The amount of time, in seconds, that messages are delayed from appearing in chat. See `non_moderator_chat_delay`.                                                                                                        |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is null if non_moderator_chat_delay is false.                                                                                                                                                                            |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | slow_mode                         | Boolean      | A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages.                                                                                            |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster applies a delay; otherwise, false.                                                                                                                                                           |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | See `slow_mode_wait_time` for the delay.                                                                                                                                                                                 |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | slow_mode_wait_time               | Integer      | The amount of time, in seconds, that users need to wait between sending messages. See `slow_mode`.                                                                                                                       |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is null if slow_mode is false.                                                                                                                                                                                           |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | subscriber_mode                   | Boolean      | A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room.                                                                                                |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster restricts the chat room to subscribers only; otherwise, false.                                                                                                                               |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | unique_chat_mode                  | Boolean      | A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room.                                                                                                    |
        |                                   |              |                                                                                                                                                                                                                          |
        |                                   |              | Is true, if the broadcaster requires unique messages only; otherwise, false.                                                                                                                                             |
        +-----------------------------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        data = exclude_non_empty(
            emote_mode=emote_mode,
            follower_mode=follower_mode,
            follower_mode_duration=follower_mode_duration,
            non_moderator_chat_delay=non_moderator_chat_delay,
            non_moderator_chat_delay_duration=non_moderator_chat_delay_duration,
            slow_mode=slow_mode,
            slow_mode_wait_time=slow_mode_wait_time,
            subscriber_mode=subscriber_mode,
            unique_chat_mode=unique_chat_mode,
        )
        return await self._request('PATCH', 'chat/settings', params=params, data=data)

    async def create_clip(self, *, broadcaster_id: str, has_delay: bool = _empty):
        """
        Creates a clip programmatically. This returns both an ID and an edit URL for the new clip.

        Note: The clips service returns a maximum of 1000 clips,

        Clip creation takes time. We recommend that you query Get Clips, with the clip ID that is returned here. If Get Clips returns a valid clip, your clip creation was successful. If, after 15 seconds, you still have not gotten back a valid clip from Get Clips, assume that the clip was not created and retry Create Clip.

        This endpoint has a global rate limit, across all callers. The limit may change over time, but the response includes informative headers:

            `Ratelimit-Helixclipscreation-Limit: <int value>
            Ratelimit-Helixclipscreation-Remaining: <int value>
            `

        # Authentication:
        - OAuth token required

        - Required scope: `clips:edit`

        # URL:
        `POST https://api.twitch.tv/helix/clips`

        # Required Query Parameter:
        +------------------+--------+----------------------------------------------------+
        | Name             | Type   | Description                                        |
        +------------------+--------+----------------------------------------------------+
        | `broadcaster_id` | string | ID of the stream from which the clip will be made. |
        +------------------+--------+----------------------------------------------------+

        # Optional Query Parameter:
        +-------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name        | Type    | Description                                                                                                                                                                                                                                                           |
        +-------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `has_delay` | boolean | If `false`, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream). Default: `false`. |
        +-------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +------------+--------+------------------------------------+
        | Field      | Type   | Description                        |
        +------------+--------+------------------------------------+
        | `edit_url` | string | URL of the edit page for the clip. |
        +------------+--------+------------------------------------+
        | `id`       | string | ID of the clip that was created.   |
        +------------+--------+------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, has_delay=has_delay)
        return await self._request('POST', 'clips', params=params)

    async def get_clips(
        self,
        *,
        after: str = _empty,
        before: str = _empty,
        broadcaster_id: str,
        ended_at: str = _empty,
        first: int = _empty,
        game_id: str,
        id_: Union[str, List[str]],
        started_at: str = _empty,
    ):
        """
        Gets clip information by clip ID (one or more), broadcaster ID (one only), or game ID (one only).

        Note: The clips service returns a maximum of 1000 clips.

        The response has a JSON payload with a `data` field containing an array of clip information elements and a `pagination` field containing information required to query for more streams.

        # Authentication:
        OAuth or App Access Token required.

        # URL:
        `GET https://api.twitch.tv/helix/clips`

        # Required Query Parameter:
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name             | Type   | Description                                                                                                                                                                           |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | ID of the broadcaster for whom clips are returned. The number of clips returned is determined by the `first` query-string parameter (default: 20). Results are ordered by view count. |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`        | string | ID of the game for which clips are returned. The number of clips returned is determined by the `first` query-string parameter (default: 20). Results are ordered by view count.       |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`             | string | ID of the clip being queried. Limit: 100.                                                                                                                                             |
        +------------------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        For a query to be valid, `id` (one or more), `broadcaster_id`, or `game_id` must be specified. You may specify only one of these parameters.

        # Optional Query Parameters:
        +--------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name         | Type    | Description                                                                                                                                                                                                                                                                                  |
        +--------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`      | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries specifying `broadcaster_id` or `game_id`. The cursor value specified here is from the `pagination` response field of a prior query.  |
        +--------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `before`     | string  | Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries specifying `broadcaster_id` or `game_id`. The cursor value specified here is from the `pagination` response field of a prior query. |
        +--------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`   | string  | Ending date/time for returned clips, in RFC3339 format. (Note that the seconds value is ignored.) If this is specified, `started_at` also must be specified; otherwise, the time period is ignored.                                                                                          |
        +--------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`      | integer | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                                                                                              |
        +--------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at` | string  | Starting date/time for returned clips, in RFC3339 format. (The seconds value is ignored.) If this is specified, `ended_at` also should be specified; otherwise, the `ended_at` date/time will be 1 week after the `started_at` value.                                                        |
        +--------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field              | Type                       | Description                                                                                                                                                  |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`               | string                     | ID of the clip being queried.                                                                                                                                |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `url`              | string                     | URL where the clip can be viewed.                                                                                                                            |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `embed_url`        | string                     | URL to embed the clip.                                                                                                                                       |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`   | string                     | User ID of the stream from which the clip was created.                                                                                                       |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name` | string                     | Display name corresponding to `broadcaster_id`.                                                                                                              |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `creator_id`       | string                     | ID of the user who created the clip.                                                                                                                         |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `creator_name`     | string                     | Display name corresponding to `creator_id`.                                                                                                                  |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `video_id`         | string                     | ID of the video from which the clip was created.                                                                                                             |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`          | string                     | ID of the game assigned to the stream when the clip was created.                                                                                             |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `language`         | string                     | Language of the stream from which the clip was created. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”. |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`            | string                     | Title of the clip.                                                                                                                                           |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `view_count`       | int                        | Number of times the clip has been viewed.                                                                                                                    |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`       | string                     | Date when the clip was created.                                                                                                                              |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `thumbnail_url`    | string                     | URL of the clip thumbnail.                                                                                                                                   |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `duration`         | float                      | Duration of the Clip in seconds (up to 0.1 precision).                                                                                                       |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`       | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results.                                                 |
        +--------------------+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after,
            before=before,
            broadcaster_id=broadcaster_id,
            ended_at=ended_at,
            first=first,
            game_id=game_id,
            id=id_,
            started_at=started_at,
        )
        return await self._request('GET', 'clips', params=params)

    async def get_code_status(self):
        """
        Gets the status of one or more provided codes. This API requires that the caller is an authenticated Twitch
        user. The API is throttled to one request per second per authenticated user. Codes are redeemable alphanumeric
        strings tied only to the bits product. This third-party API allows other parties to redeem codes on behalf of
        users. Third-party app and extension developers can use the API to provide rewards of bits from within their
        games.

        We provide sets of codes to the third party as part of a contract agreement. The third-party program then calls this API to credit a Twitch user by submitting any specific codes. This means that a bits reward can be applied without users having to follow any manual steps.

        All codes are single-use. Once a code has been redeemed, via either this API or the site page, then the code is no longer valid for any further use.

        # URL:
        `GET https://api.twitch.tv/helix/entitlements/codes`

        # Authentication:
        Access is controlled via an app access token on the calling service. The client ID associated with the app access token must be approved by Twitch as part of a contracted arrangement.

        # Authorization:
        Callers with an app access token are authorized to redeem codes on behalf of any Twitch user account.

        # Query Parameters:
        +-----------+---------+------------------------------------------------------------------------------------------------------------------+
        | Param     | Type    | Description                                                                                                      |
        +-----------+---------+------------------------------------------------------------------------------------------------------------------+
        | `code`    | String  | The code to get the status of. Repeat this query parameter additional times to get the status of multiple codes. |
        |           |         | Ex:` ?code=code1&code=code2`                                                                                     |
        |           |         | 1-20 code parameters are allowed.                                                                                |
        +-----------+---------+------------------------------------------------------------------------------------------------------------------+
        | `user_id` | Integer | Represents a numeric Twitch user ID.                                                                             |
        |           |         | The user account which is going to receive the entitlement associated with the code.                             |
        +-----------+---------+------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +--------+---------------------------------------------------------------------------------+--------------------------------------------------------------------+
        | Param  | Type                                                                            | Description                                                        |
        +--------+---------------------------------------------------------------------------------+--------------------------------------------------------------------+
        | `data` | Array of payloads each of which includes `code` (string) and `status` (string). | Indicates the current status of each key when checking key status. |
        |        |                                                                                 |                                                                    |
        |        |                                                                                 | Indicates the success or error state of each key when redeeming.   |
        +--------+---------------------------------------------------------------------------------+--------------------------------------------------------------------+

        # Code Statuses:
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Code                    | Description                                                                                                                                                      |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `SUCCESSFULLY_REDEEMED` | Request successfully redeemed this code to the authenticated user’s account.This status will only ever be encountered when calling the POST API to redeem a key. |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `ALREADY_CLAIMED`       | Code has already been claimed by a Twitch user.                                                                                                                  |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `EXPIRED`               | Code has expired and can no longer be claimed.                                                                                                                   |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `USER_NOT_ELIGIBLE`     | User is not eligible to redeem this code.                                                                                                                        |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `NOT_FOUND`             | Code is not valid and/or does not exist in our database.                                                                                                         |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `INACTIVE`              | Code is not currently active.                                                                                                                                    |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `UNUSED`                | Code has not been claimed.This status will only ever be encountered when calling the GET API to get a keys status.                                               |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `INCORRECT_FORMAT`      | Code was not properly formatted.                                                                                                                                 |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `INTERNAL_ERROR`        | Indicates some internal and/or unknown failure handling this code.                                                                                               |
        +-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        return await self._request('GET', 'entitlements/codes')

    async def get_drops_entitlements(
        self,
        *,
        after: str = _empty,
        first: int = _empty,
        fulfillment_status: str = _empty,
        game_id: str = _empty,
        id_: str = _empty,
        user_id: str = _empty,
    ):
        """
        Gets a list of entitlements for a given organization that have been granted to a game, user, or both.

        # Authentication:
        - User OAuth Token or App Access Token

        # Authorization:
        The client ID associated with the access token must have ownership of the game:

        - None`Client ID` > `Organization ID` > `Game ID`

        # Pagination support:
        Forward only

        # URL:
        `GET https://api.twitch.tv/helix/entitlements/drops`

        # Optional Query Parameters:
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+
        | Parameter            | Type    | Description                                                                                                |
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+
        | `id`                 | string  | Unique identifier of the entitlement.                                                                      |
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+
        | `user_id`            | string  | A Twitch user ID.                                                                                          |
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+
        | `game_id`            | string  | A Twitch game ID.                                                                                          |
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+
        | `fulfillment_status` | string  | An optional fulfillment status used to filter entitlements. Valid values are `"CLAIMED"` or `"FULFILLED"`. |
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+
        | `after`              | string  | The cursor used to fetch the next page of data.                                                            |
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+
        | `first`              | integer | Maximum number of entitlements to return.                                                                  |
        |                      |         |                                                                                                            |
        |                      |         | Default: 20                                                                                                |
        |                      |         | Max: 1000                                                                                                  |
        +----------------------+---------+------------------------------------------------------------------------------------------------------------+

        Valid combinations of requests are:

        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        | Authorization Provided | Request Fields Present | Data Returned                                                                                 |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        | App Access             | No fields              | All entitlements with benefits owned by your organization.                                    |
        | OAuth Token            |                        |                                                                                               |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        |                        | `user_id`              | All entitlements for a user with benefits owned by your organization.                         |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        |                        | `user_id`, `game_id`   | All entitlements for the game granted to a user. Your organization must own the game.         |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        |                        | `game_id`              | All entitlements for all users for a game. Your organization must own the game.               |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        | User OAuth Token       | No fields              | All entitlements owned by that user with benefits owned by your organization.                 |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        |                        | `user_id`              | Invalid.                                                                                      |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        |                        | `user_id`, `game_id`   | Invalid.                                                                                      |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+
        |                        | `game_id`              | All entitlements owned by a user for the specified game. Your organization must own the game. |
        +------------------------+------------------------+-----------------------------------------------------------------------------------------------+

        # Return Values:
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | Parameter            | Type   | Description                                                                                                                   |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `data`               | array  | Array of entitlements.                                                                                                        |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `id`                 | string | Unique identifier of the entitlement.                                                                                         |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `benefit_id`         | string | Identifier of the benefit.                                                                                                    |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `timestamp`          | string | UTC timestamp in ISO format when this entitlement was granted on Twitch.                                                      |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`            | string | Twitch user ID of the user who was granted the entitlement.                                                                   |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`            | string | Twitch game ID of the game that was being played when this benefit was entitled.                                              |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `fulfillment_status` | string | The fulfillment status of the entitlement as determined by the game developer. Valid values are `"CLAIMED"` or `"FULFILLED"`. |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `updated_at`         | string | UTC timestamp in ISO format for when this entitlement was last updated.                                                       |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`         | object | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results.                  |
        +----------------------+--------+-------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+---------------------------------------------------------------+
        | Code | Meaning                                                       |
        +------+---------------------------------------------------------------+
        | 200  | Entitlements retrieved successfully.                          |
        +------+---------------------------------------------------------------+
        | 400  | A malformed request, invalid user ID, or invalid game ID. |
        +------+---------------------------------------------------------------+
        | 401  | Authorization failed.                                         |
        +------+---------------------------------------------------------------+
        | 500  | Internal server error.                                        |
        +------+---------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after, first=first, fulfillment_status=fulfillment_status, game_id=game_id, id=id_, user_id=user_id
        )
        return await self._request('GET', 'entitlements/drops', params=params)

    async def update_drops_entitlements(self, *, entitlement_ids: List[str] = _empty, fulfillment_status: str = _empty):
        """
        Updates the fulfillment status on a set of Drops entitlements, specified by their entitlement IDs.

        # Authentication:
        - User OAuth Token or App Access Token

        # Authorization:
        The client ID associated with the access token must have ownership of the game:

        - None`Client ID` > `Organization ID` > `Game ID`

        # URL:
        `PATCH https://api.twitch.tv/helix/entitlements/drops`

        # Optional Query Parameters:
        +----------------------+--------+----------------------------------------------------------------------+
        | Parameter            | Type   | Description                                                          |
        +----------------------+--------+----------------------------------------------------------------------+
        | `entitlement_ids`    | array  | An array of unique identifiers of the entitlements to update.        |
        |                      |        |                                                                      |
        |                      |        | Maximum: 100.                                                        |
        +----------------------+--------+----------------------------------------------------------------------+
        | `fulfillment_status` | string | A fulfillment status. Valid values are `"CLAIMED"` or `"FULFILLED"`. |
        +----------------------+--------+----------------------------------------------------------------------+

        Valid combinations of requests are:

        +------------------------+-------------------------------------------------------------------------------+
        | Authorization Provided | Data Returned                                                                 |
        +------------------------+-------------------------------------------------------------------------------+
        | App Access OAuth Token | All entitlements with benefits owned by your organization.                    |
        +------------------------+-------------------------------------------------------------------------------+
        | User OAuth Token       | All entitlements owned by that user with benefits owned by your organization. |
        +------------------------+-------------------------------------------------------------------------------+

        # Return Values:
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                               |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`    | array  | Array of entitlement update statuses.                                                                                                                     |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`  | string | Status code applied to a set of entitlements for the update operation that can be used to indicate partial success. Valid values are:                     |
        |           |        |                                                                                                                                                           |
        |           |        | `SUCCESS`: Entitlement was successfully updated.                                                                                                          |
        |           |        |                                                                                                                                                           |
        |           |        | `INVALID_ID`: Invalid format for entitlement ID.                                                                                                          |
        |           |        |                                                                                                                                                           |
        |           |        | `NOT_FOUND`: Entitlement ID does not exist.                                                                                                               |
        |           |        |                                                                                                                                                           |
        |           |        | `UNAUTHORIZED`: Entitlement is not owned by the organization or the user when called with a user OAuth token.                                             |
        |           |        |                                                                                                                                                           |
        |           |        | `UPDATE_FAILED`: Indicates the entitlement update operation failed. Errors in the this state are expected to be be transient and should be retried later. |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `ids`     | array  | Array of unique identifiers of the entitlements for the specified status.                                                                                 |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+---------------------------------------------------------------+
        | Code | Meaning                                                       |
        +------+---------------------------------------------------------------+
        | 200  | Entitlement updated successfully.                             |
        +------+---------------------------------------------------------------+
        | 400  | A malformed request, invalid user ID, or invalid game ID. |
        +------+---------------------------------------------------------------+
        | 401  | Authorization failed.                                         |
        +------+---------------------------------------------------------------+
        | 500  | Internal server error.                                        |
        +------+---------------------------------------------------------------+
        """
        params = exclude_non_empty(entitlement_ids=entitlement_ids, fulfillment_status=fulfillment_status)
        return await self._request('PATCH', 'entitlements/drops', params=params)

    async def redeem_code(self, *, code: str = _empty, user_id: int = _empty):
        """
        Redeems one or more redemption codes. Redeeming a code credits the user’s account with the entitlement
        associated with the code. For example, a Bits reward earned when playing a game.

        Rate limit: You may send at most one request per second per user.

        # URL:
        `POST https://api.twitch.tv/helix/entitlements/codes`

        # Authentication:
        Requires an App access token. Only client IDs approved by Twitch may redeem codes on behalf of any Twitch user account.

        # Query Parameters:
        +-----------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type    | Description                                                                                                                                                                          |
        +-----------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `code`    | String  | The redemption code to redeem. To redeem multiple codes, include this parameter for each redemption code. For example, `code=1234&code=5678`. You may specify a maximum of 20 codes. |
        +-----------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | Integer | The ID of the user that owns the redemption code to redeem.                                                                                                                          |
        +-----------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +-----------+--------------+----------------------------------------------------------------------------------------------------------------+
        | Parameter | Type         | Description                                                                                                    |
        +-----------+--------------+----------------------------------------------------------------------------------------------------------------+
        | `data`    | Object array | The list of redeemed codes.                                                                                    |
        +-----------+--------------+----------------------------------------------------------------------------------------------------------------+
        | `code`    | String       | The redemption code.                                                                                           |
        +-----------+--------------+----------------------------------------------------------------------------------------------------------------+
        | `status`  | String       | The redemption code’s status. Possible values are:                                                             |
        |           |              | - ALREADY_CLAIMED — The code has already been claimed. All codes are single-use.                               |
        |           |              | - EXPIRED — The code has expired and can no longer be claimed.                                                 |
        |           |              | - INACTIVE — The code has not been activated.                                                                  |
        |           |              | - INCORRECT_FORMAT — The code is not properly formatted.                                                       |
        |           |              | - INTERNAL_ERROR — An internal or unknown error occurred when accessing the code.                              |
        |           |              | - NOT_FOUND — The code was not found.                                                                          |
        |           |              | - SUCCESSFULLY_REDEEMED — Successfully redeemed the code and credited the user's account with the entitlement. |
        |           |              | - UNUSED — The code has not been claimed.                                                                      |
        |           |              | - USER_NOT_ELIGIBLE — The user is not eligible to redeem this code.                                            |
        +-----------+--------------+----------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(code=code, user_id=user_id)
        return await self._request('POST', 'entitlements/codes', params=params)

    async def get_extension_configuration_segment(self, *, broadcaster_id: str, extension_id: str, segment: str):
        """
        NEW Gets the specified configuration segment from the specified extension.

        NOTE: You can retrieve each segment a maximum of 20 times per minute. If you exceed the limit, the request returns HTTP status code 429. To determine when you may resume making requests, see the `Ratelimit-Reset` response header.

        # Authorization:
        A signed JWT created by an Extension Backend Service (EBS). For signing requirements, see Signing the JWT. The signed JWT must include the `exp`, `user_id`, and `role` fields documented in JWT Schema, and `role` must be set to `external`. For example:

            `None`{
            "exp": 1503343947,
            "user_id": "27419011",
            "role": "external"
            }

        # URL:
        `GET https://api.twitch.tv/helix/extensions/configurations`

        # Required Query Parameters:
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                                                                                        |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | The ID of the broadcaster for the configuration returned. This parameter is required if you set the `segment` parameter to broadcaster or developer. Do not specify this parameter if you set `segment` to global. |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `extension_id`   | string | The ID of the extension that contains the configuration segment you want to get.                                                                                                                                   |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment`        | string | The type of configuration segment to get. Valid values are:                                                                                                                                                        |
        |                  |        | - broadcaster                                                                                                                                                                                                      |
        |                  |        | - developer                                                                                                                                                                                                        |
        |                  |        | - globalYou may specify one or more segments. To specify multiple segments, include the `segment` parameter for each segment to get. For example, `segment=broadcaster&segment=developer`.                         |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +------------------+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name             | Type         | Description                                                                                                                                                 |
        +------------------+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`           | object array | An array of Segment objects.                                                                                                                                |
        +------------------+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment`        | string       | The type of segment. Possible values are:                                                                                                                   |
        |                  |              | - broadcaster                                                                                                                                               |
        |                  |              | - developer                                                                                                                                                 |
        |                  |              | - global                                                                                                                                                    |
        +------------------+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string       | The ID of the broadcaster that owns the extension. The object includes this field only if the `segment` query parameter is set to developer or broadcaster. |
        +------------------+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `content`        | string       | The contents of the segment. This string may be a plain string or a string-encoded JSON object.                                                             |
        +------------------+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `version`        | string       | The version that identifies the segment’s definition.                                                                                                       |
        +------------------+--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                                          |
        +------+------------------------------------------------------------------------------------------------------------------+
        | 200  | Successfully retrieved the configuration.                                                                        |
        +------+------------------------------------------------------------------------------------------------------------------+
        | 400  | The request was invalid. Confirm that you correctly specified the required query parameters.                     |
        +------+------------------------------------------------------------------------------------------------------------------+
        | 401  | Authorization failed. Invalid or expired JWT.                                                                    |
        +------+------------------------------------------------------------------------------------------------------------------+
        | 429  | Too many requests. Check the `Ratelimit-Reset` response header to determine when you may resume making requests. |
        +------+------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, extension_id=extension_id, segment=segment)
        return await self._request('GET', 'extensions/configurations', params=params)

    async def set_extension_configuration_segment(
        self,
        *,
        broadcaster_id: str = _empty,
        content: str = _empty,
        extension_id: str,
        segment: str,
        version: str = _empty,
    ):
        """
        NEW Sets a single configuration segment of any type. The segment type is specified as a body parameter.

        Each segment is limited to 5 KB and can be set at most 20 times per minute. Updates to this data are not delivered to Extensions that have already been rendered.

        # Authorization:
        Signed JWT created by an Extension Backend Service (EBS), following the requirements documented in Signing the JWT. A signed JWT must include the `exp`, `user_id`, and `role` fields documented in JWT Schema, and `role` must be set to `"external"`. For example:

            `None`{
            "exp": 1503343947,
            "user_id": "27419011",
            "role": "external"
            }

        # URL:
        `PUT https://api.twitch.tv/helix/extensions/configurations`

        # Pagination Support:
        Not applicable.

        # Required Body Parameters:
        +----------------+--------+-------------------------------------------------------------------------------------+
        | Parameter      | Type   | Description                                                                         |
        +----------------+--------+-------------------------------------------------------------------------------------+
        | `extension_id` | string | ID for the Extension which the configuration is for.                                |
        +----------------+--------+-------------------------------------------------------------------------------------+
        | `segment`      | string | Configuration type. Valid values are `"global"`, `"developer"`, or `"broadcaster"`. |
        +----------------+--------+-------------------------------------------------------------------------------------+

        # Optional Body Parameters:
        +------------------+--------+-----------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                   |
        +------------------+--------+-----------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster. Required if the segment type is `"developer"` or `"broadcaster"`. |
        +------------------+--------+-----------------------------------------------------------------------------------------------+
        | `content`        | string | Configuration in a string-encoded format.                                                     |
        +------------------+--------+-----------------------------------------------------------------------------------------------+
        | `version`        | string | Configuration version with the segment type.                                                  |
        +------------------+--------+-----------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------+
        | Code | Meaning                                       |
        +------+-----------------------------------------------+
        | 204  | The configuration was successfully stored.    |
        +------+-----------------------------------------------+
        | 400  | Request was invalid.                          |
        +------+-----------------------------------------------+
        | 401  | Authorization failed. Invalid or expired JWT. |
        +------+-----------------------------------------------+
        """
        data = exclude_non_empty(
            broadcaster_id=broadcaster_id, content=content, extension_id=extension_id, segment=segment, version=version
        )
        return await self._request('PUT', 'extensions/configurations', data=data)

    async def set_extension_required_configuration(
        self, *, broadcaster_id: str, configuration_version: str, extension_id: str, extension_version: str
    ):
        """
        NEW Enable activation of a specified Extension, after any required broadcaster configuration is correct. The
        Extension is identified by a client ID value assigned to the Extension when it is created. This is for
        Extensions that require broadcaster configuration before activation. Use this if, in Extension Capabilities, you
        select Custom/My Own Service.

        You enforce required broadcaster configuration with a `required_configuration` string in the Extension manifest. The contents of this string can be whatever you want. Once your EBS determines that the Extension is correctly configured on a channel, use this endpoint to provide that same configuration string, which enables activation on the channel. The endpoint URL includes the channel ID of the page where the Extension is iframe embedded.

        If a future version of the Extension requires a different configuration, change the `required_configuration` string in your manifest. When the new version is released, broadcasters will be required to re-configure that new version.

        # Authorization:
        Signed JWT created by an Extension Backend Service (EBS), following the requirements documented in Signing the JWT. A signed JWT must include the `exp`, `user_id`, and `role` fields documented in JWT Schema, and `role` must be set to `"external"`. For example:

            `None`{
            "exp": 1503343947,
            "user_id": "27419011",
            "role": "external"
            }

        # URL:
        `PUT https://api.twitch.tv/helix/extensions/required_configuration`

        # Pagination Support:
        Not applicable.

        # Required Query Parameters:
        +------------------+--------+----------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                            |
        +------------------+--------+----------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster who has activated the specified Extension on their channel. |
        +------------------+--------+----------------------------------------------------------------------------------------+

        # Required Body Parameters:
        +-------------------------+--------+-------------------------------------------------------------+
        | Parameter               | Type   | Description                                                 |
        +-------------------------+--------+-------------------------------------------------------------+
        | `extension_id`          | string | ID for the Extension to activate.                           |
        +-------------------------+--------+-------------------------------------------------------------+
        | `extension_version`     | string | The version fo the Extension to release.                    |
        +-------------------------+--------+-------------------------------------------------------------+
        | `configuration_version` | string | The version of the configuration to use with the Extension. |
        +-------------------------+--------+-------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------+
        | Code | Meaning                                        |
        +------+------------------------------------------------+
        | 204  | Extension activated successfully.              |
        +------+------------------------------------------------+
        | 400  | Request was invalid.                           |
        +------+------------------------------------------------+
        | 401  | Authorization failed. Invalid or expired JWT. |
        +------+------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        data = exclude_non_empty(
            configuration_version=configuration_version, extension_id=extension_id, extension_version=extension_version
        )
        return await self._request('PUT', 'extensions/required_configuration', params=params, data=data)

    async def send_extension_pubsub_message(
        self, *, broadcaster_id: str, is_global_broadcast: bool, message: str, target: List[str]
    ):
        """
        NEW Twitch provides a publish-subscribe system for your EBS to communicate with both the broadcaster and
        viewers. Calling this endpoint forwards your message using the same mechanism as the send JavaScript helper
        function. A message can be sent to either a specified channel or globally (all channels on which your extension
        is active).

        Extension PubSub has a rate limit of 100 requests per minute for a combination of Extension client ID and broadcaster ID.

        # Authorization:
        Signed JWT created by an Extension Backend Service (EBS), following the requirements documented in Signing the JWT. A signed JWT must include the `channel_id` and `pubsub_perms` fields documented in JWT Schema. For example:

            `None`{
            "exp": 1503343947,
            "user_id": "27419011",
            "role": "external",
            "channel_id": "27419011",
            "pubsub_perms": {
            "send":[
            "broadcast"
            ]
            }
            }

        To send globally:

            `None`{
            "exp": 1503343947,
            "user_id": "27419011",
            "role": "external",
            "channel_id": "all",
            "pubsub_perms": {
            "send":[
            "global"
            ]
            }
            }

        # URL:
        `POST https://api.twitch.tv/helix/extensions/pubsub`

        # Pagination Support:
        Not applicable.

        # Required Body Parameters:
        +-----------------------+---------+--------------------------------------------------------------------------------------------------------------+
        | Parameter             | Type    | Description                                                                                                  |
        +-----------------------+---------+--------------------------------------------------------------------------------------------------------------+
        | `target`              | array   | Array of strings for valid PubSub targets. Valid values: `"broadcast"`, `"global"`, `"whisper-<user-id>"`    |
        +-----------------------+---------+--------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`      | string  | ID of the broadcaster receiving the payload. This is not required if `is_global_broadcast` is set to `true`. |
        +-----------------------+---------+--------------------------------------------------------------------------------------------------------------+
        | `is_global_broadcast` | boolean | Indicates if the message should be sent to all channels where your Extension is active.                      |
        |                       |         |                                                                                                              |
        |                       |         | Default: `false`.                                                                                            |
        +-----------------------+---------+--------------------------------------------------------------------------------------------------------------+
        | `message`             | string  | String-encoded JSON message to be sent.                                                                      |
        +-----------------------+---------+--------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------+
        | Code | Meaning                                        |
        +------+------------------------------------------------+
        | 204  | The message was published successfully.        |
        +------+------------------------------------------------+
        | 400  | Request was invalid.                           |
        +------+------------------------------------------------+
        | 401  | Authorization failed. Invalid or expired JWT. |
        +------+------------------------------------------------+
        """
        data = exclude_non_empty(
            broadcaster_id=broadcaster_id, is_global_broadcast=is_global_broadcast, message=message, target=target
        )
        return await self._request('POST', 'extensions/pubsub', data=data)

    async def get_extension_live_channels(self, *, after: str = _empty, extension_id: str, first: int = _empty):
        """
        NEW Returns one page of live channels that have installed or activated a specific Extension, identified by a
        client ID value assigned to the Extension when it is created. A channel that recently went live may take a few
        minutes to appear in this list, and a channel may continue to appear on this list for a few minutes after it
        stops broadcasting.

        # Authorization:
        - User OAuth Token or App Access Token

        # URL:
        `GET https://api.twitch.tv/helix/extensions/live`

        # Pagination Support:
        Forward pagination.

        # Required Query Parameters:
        +----------------+--------+------------------------------------+
        | Parameter      | Type   | Description                        |
        +----------------+--------+------------------------------------+
        | `extension_id` | string | ID of the Extension to search for. |
        +----------------+--------+------------------------------------+

        # Optional Query Parameters:
        +-----------+---------+-------------------------------------------------+
        | Parameter | Type    | Description                                     |
        +-----------+---------+-------------------------------------------------+
        | `first`   | integer | Maximum number of objects to return.            |
        |           |         |                                                 |
        |           |         | Maximum: 100. Default: 20.                      |
        +-----------+---------+-------------------------------------------------+
        | `after`   | string  | The cursor used to fetch the next page of data. |
        +-----------+---------+-------------------------------------------------+

        # Return Values:
        +--------------------+--------+--------------------------------+
        | Parameter          | Type   | Description                    |
        +--------------------+--------+--------------------------------+
        | `title`            | string | Title of the stream.           |
        +--------------------+--------+--------------------------------+
        | `broadcaster_id`   | string | User ID of the broadcaster.    |
        +--------------------+--------+--------------------------------+
        | `broadcaster_name` | string | Broadcaster’s display name.    |
        +--------------------+--------+--------------------------------+
        | `game_name`        | string | Name of the game being played. |
        +--------------------+--------+--------------------------------+
        | `game_id`          | string | ID of the game being played.   |
        +--------------------+--------+--------------------------------+

        # Response Codes:
        +------+----------------------------------------------+
        | Code | Meaning                                      |
        +------+----------------------------------------------+
        | 200  | List of live channels returned successfully. |
        +------+----------------------------------------------+
        | 400  | Request was invalid.                         |
        +------+----------------------------------------------+
        | 401  | Authorization failed.                        |
        +------+----------------------------------------------+
        """
        params = exclude_non_empty(after=after, extension_id=extension_id, first=first)
        return await self._request('GET', 'extensions/live', params=params)

    async def get_extension_secrets(self):
        """
        NEW Retrieves a specified Extension’s secret data consisting of a version and an array of secret objects. Each
        secret object contains a base64-encoded secret, a UTC timestamp when the secret becomes active, and a timestamp
        when the secret expires.

        # Authorization:
        Signed JWT created by an Extension Backend Service (EBS), following the requirements documented in Signing the JWT. A signed JWT must include the `exp`, `user_id`, and `role` fields documented in JWT Schema, and `role` must be set to `"external"`. For example:

            `None`{
            "exp": 1503343947,
            "user_id": "27419011",
            "role": "external"
            }

        # URL:
        `GET https://api.twitch.tv/helix/extensions/jwt/secrets`

        # Pagination Support:
        None.

        # Return Values:
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | Parameter           | Type    | Description                                                                          |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `format_version`    | integer | Indicates the version associated with the Extension secrets in the response.         |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets`           | array   | Array of secret objects.                                                             |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets[].content` | string  | Raw secret that should be used with JWT encoding.                                    |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets[].active`  | string  | The earliest possible time this secret is valid to sign a JWT in RFC 3339 format.    |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets[].expires` | string  | The latest possible time this secret may be used to decode a JWT in RFC 3339 format. |
        +---------------------+---------+--------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------+
        | Code | Meaning                                       |
        +------+-----------------------------------------------+
        | 200  | Extensions secrets returned successfully.     |
        +------+-----------------------------------------------+
        | 400  | Request was invalid.                          |
        +------+-----------------------------------------------+
        | 401  | Authorization failed. Invalid or expired JWT. |
        +------+-----------------------------------------------+
        """
        return await self._request('GET', 'extensions/jwt/secrets')

    async def create_extension_secret(self, *, delay: int = _empty):
        """
        NEW Creates a JWT signing secret for a specific Extension. Also rotates any current secrets out of service, with
        enough time for instances of the Extension to gracefully switch over to the new secret. Use this function only
        when you are ready to install the new secret it returns.

        # Authorization:
        Signed JWT created by an Extension Backend Service (EBS), following the requirements documented in Signing the JWT. A signed JWT must include the `exp`, `user_id`, and `role` fields documented in JWT Schema, and `role` must be set to `"external"`. For example:

            `None`{
            "exp": 1503343947,
            "user_id": "27419011",
            "role": "external"
            }

        # URL:
        `POST https://api.twitch.tv/helix/extensions/jwt/secrets`

        # Pagination Support:
        Not applicable.

        # Optional Query Parameters:
        +-----------+---------+-----------------------------------------------------------------------+
        | Parameter | Type    | Description                                                           |
        +-----------+---------+-----------------------------------------------------------------------+
        | `delay`   | integer | JWT signing activation delay for the newly created secret in seconds. |
        |           |         |                                                                       |
        |           |         | Minimum: 300. Default: 300.                                           |
        +-----------+---------+-----------------------------------------------------------------------+

        # Return Values:
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | Parameter           | Type    | Description                                                                          |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `format_version`    | integer | Indicates the version associated with the Extension secrets in the response.         |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets`           | array   | Array of secret objects.                                                             |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets[].content` | string  | Raw secret that should be used with JWT encoding.                                    |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets[].active`  | string  | The earliest possible time this secret is valid to sign a JWT in RFC 3339 format.    |
        +---------------------+---------+--------------------------------------------------------------------------------------+
        | `secrets[].expires` | string  | The latest possible time this secret may be used to decode a JWT in RFC 3339 format. |
        +---------------------+---------+--------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------+
        | Code | Meaning                                       |
        +------+-----------------------------------------------+
        | 200  | A new secret was created successfully.        |
        +------+-----------------------------------------------+
        | 400  | Request was invalid.                          |
        +------+-----------------------------------------------+
        | 401  | Authorization failed. Invalid or expired JWT. |
        +------+-----------------------------------------------+
        """
        params = exclude_non_empty(delay=delay)
        return await self._request('POST', 'extensions/jwt/secrets', params=params)

    async def send_extension_chat_message(
        self, *, broadcaster_id: str, extension_id: str, extension_version: str, text: str
    ):
        """
        NEW Sends a specified chat message to a specified channel. The message will appear in the channel’s chat as a
        normal message. The “username” of the message is the Extension name.

        There is a limit of 12 messages per minute, per channel. Extension chat messages use the same rate-limiting functionality as the Twitch API (see Rate Limits).

        # Authorization:
        Signed JWT created by an Extension Backend Service (EBS), following the requirements documented in Signing the JWT. A signed JWT must include the `role` and `channel_id` fields documented in JWT Schema. `role` must be set to `"external"` and `channel_id` must match the broadcaster ID in the request URL.

        # URL:
        `POST https://api.twitch.tv/helix/extensions/chat`

        # Pagination Support:
        Not applicable.

        # Required Query Parameters:
        +------------------+--------+-----------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                           |
        +------------------+--------+-----------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster whose channel has the Extension activated. |
        +------------------+--------+-----------------------------------------------------------------------+

        # Required Body Parameters:
        +---------------------+--------+------------------------------------------------+
        | Parameter           | Type   | Description                                    |
        +---------------------+--------+------------------------------------------------+
        | `text`              | string | Message for Twitch chat.                       |
        |                     |        |                                                |
        |                     |        | Maximum: 280 characters.                       |
        +---------------------+--------+------------------------------------------------+
        | `extension_id`      | string | Client ID associated with the Extension.       |
        +---------------------+--------+------------------------------------------------+
        | `extension_version` | string | Version of the Extension sending this message. |
        +---------------------+--------+------------------------------------------------+

        # Response Codes:
        +------+---------------------------------------------------------+
        | Code | Meaning                                                 |
        +------+---------------------------------------------------------+
        | 204  | Chat message was published to the channel successfully. |
        +------+---------------------------------------------------------+
        | 400  | Request was invalid.                                    |
        +------+---------------------------------------------------------+
        | 401  | Authorization failed. Invalid or expired JWT.           |
        +------+---------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        data = exclude_non_empty(extension_id=extension_id, extension_version=extension_version, text=text)
        return await self._request('POST', 'extensions/chat', params=params, data=data)

    async def get_extensions(self, *, extension_id: str, extension_version: str = _empty):
        """
        NEW Gets information about your Extensions; either the current version or a specified version.

        # Authorization:
        Signed JWT created by an Extension Backend Service (EBS), following the requirements documented in Signing the JWT. A signed JWT must include the `role` field documented in JWT Schema, and `role` must be set to `"external"`.

        # URL:
        `GET https://api.twitch.tv/helix/extensions`

        # Pagination Support:
        None.

        # Required Query Parameters:
        +----------------+--------+----------------------+
        | Parameter      | Type   | Description          |
        +----------------+--------+----------------------+
        | `extension_id` | string | ID of the Extension. |
        +----------------+--------+----------------------+

        # Optional Query Parameters:
        +---------------------+--------+----------------------------------------------------------------------------------------------------+
        | Parameter           | Type   | Description                                                                                        |
        +---------------------+--------+----------------------------------------------------------------------------------------------------+
        | `extension_version` | string | The specific version of the Extension to return. If not provided, the current version is returned. |
        +---------------------+--------+----------------------------------------------------------------------------------------------------+

        # Return Values:
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                     | Type    | Description                                                                                                                                                                                  |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `author_name`                 | string  | Name of the individual or organization that owns the Extension.                                                                                                                              |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `bits_enabled`                | boolean | Whether the Extension has features that use Bits.                                                                                                                                            |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `can_install`                 | boolean | Indicates if a user can install the Extension on their channel. They may not be allowed if the Extension is currently in testing mode and the user is not on the allow list.                 |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `configuration_location`      | string  | Whether the Extension configuration is hosted by the EBS or the Extensions Configuration Service.                                                                                            |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `description`                 | string  | The description of the Extension.                                                                                                                                                            |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `eula_tos_url`                | string  | URL to the Extension’s Terms of Service.                                                                                                                                                     |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `has_chat_support`            | boolean | Indicates if the Extension can communicate with the installed channel’s chat.                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `icon_url`                    | string  | The default icon to be displayed in the Extensions directory.                                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `icon_urls`                   | object  | The default icon in a variety of sizes.                                                                                                                                                      |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                          | string  | The autogenerated ID of the Extension.                                                                                                                                                       |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `name`                        | string  | The name of the Extension.                                                                                                                                                                   |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `privacy_policy_url`          | string  | URL to the Extension’s privacy policy.                                                                                                                                                       |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `request_identity_link`       | boolean | Indicates if the Extension wants to explicitly ask viewers to link their Twitch identity.                                                                                                    |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `screenshot_urls`             | array   | Screenshots to be shown in the Extensions marketplace.                                                                                                                                       |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `state`                       | string  | The current state of the Extension. Valid values are `"InTest"`, `"InReview"`, `"Rejected"`, `"Approved"`, `"Released"`, `"Deprecated"`, `"PendingAction"`, `"AssetsUploaded"`, `"Deleted"`. |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `subscriptions_support_level` | string  | Indicates if the Extension can determine a user’s subscription level on the channel the Extension is installed on.                                                                           |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `summary`                     | string  | A brief description of the Extension.                                                                                                                                                        |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `support_email`               | string  | The email users can use to receive Extension support.                                                                                                                                        |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `version`                     | string  | The version of the Extension.                                                                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `viewer_summary`              | string  | A brief description displayed on the channel to explain how the Extension works.                                                                                                             |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `views`                       | object  | All configurations related to views such as: mobile, panel, video_overlay, and component.                                                                                                    |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `allowlisted_config_urls`     | array   | Allow-listed configuration URLs for displaying the Extension.                                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `allowlisted_panel_urls`      | array   | Allow-listed panel URLs for displaying the Extension.                                                                                                                                        |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------+
        | Code | Meaning                                  |
        +------+------------------------------------------+
        | 200  | Extension details returned successfully. |
        +------+------------------------------------------+
        | 400  | Request was invalid.                     |
        +------+------------------------------------------+
        | 401  | Authorization failed.                    |
        +------+------------------------------------------+
        """
        params = exclude_non_empty(extension_id=extension_id, extension_version=extension_version)
        return await self._request('GET', 'extensions', params=params)

    async def get_released_extensions(self, *, extension_id: str, extension_version: str = _empty):
        """
        NEW Gets information about a released Extension; either the current version or a specified version.

        # Authorization:
        - User OAuth Token or App Access Token

        # URL:
        `GET https://api.twitch.tv/helix/extensions/released`

        # Pagination Support:
        None.

        # Required Query Parameters:
        +----------------+--------+----------------------+
        | Parameter      | Type   | Description          |
        +----------------+--------+----------------------+
        | `extension_id` | string | ID of the Extension. |
        +----------------+--------+----------------------+

        # Optional Query Parameters:
        +---------------------+--------+----------------------------------------------------------------------------------------------------+
        | Parameter           | Type   | Description                                                                                        |
        +---------------------+--------+----------------------------------------------------------------------------------------------------+
        | `extension_version` | string | The specific version of the Extension to return. If not provided, the current version is returned. |
        +---------------------+--------+----------------------------------------------------------------------------------------------------+

        # Return Values:
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                     | Type    | Description                                                                                                                                                                                  |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `author_name`                 | string  | Name of the individual or organization that owns the Extension.                                                                                                                              |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `bits_enabled`                | boolean | Whether the Extension has features that use Bits.                                                                                                                                            |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `can_install`                 | boolean | Indicates if a user can install the Extension on their channel. They may not be allowed if the Extension is currently in testing mode and the user is not on the allow list.                 |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `configuration_location`      | string  | Whether the Extension configuration is hosted by the EBS or the Extensions Configuration Service.                                                                                            |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `description`                 | string  | The description of the Extension.                                                                                                                                                            |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `eula_tos_url`                | string  | URL to the Extension’s Terms of Service.                                                                                                                                                     |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `has_chat_support`            | boolean | Indicates if the Extension can communicate with the installed channel’s chat.                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `icon_url`                    | string  | The default icon to be displayed in the Extensions directory.                                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `icon_urls`                   | object  | The default icon in a variety of sizes.                                                                                                                                                      |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                          | string  | The autogenerated ID of the Extension.                                                                                                                                                       |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `name`                        | string  | The name of the Extension.                                                                                                                                                                   |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `privacy_policy_url`          | string  | URL to the Extension’s privacy policy.                                                                                                                                                       |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `request_identity_link`       | boolean | Indicates if the Extension wants to explicitly ask viewers to link their Twitch identity.                                                                                                    |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `screenshot_urls`             | array   | Screenshots to be shown in the Extensions marketplace.                                                                                                                                       |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `state`                       | string  | The current state of the Extension. Valid values are `"InTest"`, `"InReview"`, `"Rejected"`, `"Approved"`, `"Released"`, `"Deprecated"`, `"PendingAction"`, `"AssetsUploaded"`, `"Deleted"`. |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `subscriptions_support_level` | object  | Indicates if the Extension can determine a user’s subscription level on the channel the Extension is installed on.                                                                           |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `summary`                     | string  | A brief description of the Extension.                                                                                                                                                        |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `support_email`               | string  | The email users can use to receive Extension support.                                                                                                                                        |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `version`                     | string  | The version of the Extension.                                                                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `viewer_summary`              | string  | A brief description displayed on the channel to explain how the Extension works.                                                                                                             |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `views`                       | object  | All configurations related to views such as: mobile, panel, video_overlay, and component.                                                                                                    |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `allowlisted_config_urls`     | array   | Allow-listed configuration URLs for displaying the Extension.                                                                                                                                |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `allowlisted_panel_urls`      | array   | Allow-listed panel URLs for displaying the Extension.                                                                                                                                        |
        +-------------------------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------+
        | Code | Meaning                                  |
        +------+------------------------------------------+
        | 200  | Extension details returned successfully. |
        +------+------------------------------------------+
        | 400  | Request was invalid.                     |
        +------+------------------------------------------+
        | 401  | Authorization failed.                    |
        +------+------------------------------------------+
        """
        params = exclude_non_empty(extension_id=extension_id, extension_version=extension_version)
        return await self._request('GET', 'extensions/released', params=params)

    async def get_extension_bits_products(self, *, should_include_all: bool = _empty):
        """
        NEW Gets a list of Bits products that belongs to an Extension.

        # Authorization:
        - App Access Token associated with the Extension client ID

        # URL:
        `GET https://api.twitch.tv/helix/bits/extensions`

        # Pagination Support:
        None.

        # Optional Query Parameters:
        +----------------------+---------+-------------------------------------------------------------------------------------+
        | Parameter            | Type    | Description                                                                         |
        +----------------------+---------+-------------------------------------------------------------------------------------+
        | `should_include_all` | boolean | Whether Bits products that are disabled/expired should be included in the response. |
        |                      |         |                                                                                     |
        |                      |         | Default: `false`.                                                                   |
        +----------------------+---------+-------------------------------------------------------------------------------------+

        # Return Values:
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type    | Description                                                                                                                                            |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `sku`            | string  | SKU of the Bits product. This is unique across all products that belong to an Extension.                                                               |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`           | object  | Object containing cost information.                                                                                                                    |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost.amount`    | integer | Number of Bits for which the product will be exchanged.                                                                                                |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost.type`      | string  | Cost type. The one valid value is `"bits"`.                                                                                                            |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `in_development` | boolean | Indicates if the product is in development and not yet released for public use.                                                                        |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `display_name`   | string  | Name of the product to be displayed in the Extension.                                                                                                  |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `expiration`     | string  | Expiration time for the product in RFC3339 format.                                                                                                     |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_broadcast`   | boolean | Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback. |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+----------------------------------------------+
        | Code | Meaning                                      |
        +------+----------------------------------------------+
        | 200  | List of Bits products returned successfully. |
        +------+----------------------------------------------+
        | 400  | Request was invalid.                         |
        +------+----------------------------------------------+
        | 401  | Authorization failed.                        |
        +------+----------------------------------------------+
        """
        params = exclude_non_empty(should_include_all=should_include_all)
        return await self._request('GET', 'bits/extensions', params=params)

    async def update_extension_bits_product(
        self,
        *,
        cost_amount: int,
        cost_type: str,
        display_name: str,
        expiration: str = _empty,
        in_development: bool = _empty,
        is_broadcast: bool = _empty,
        sku: str,
    ):
        """
        NEW Add or update a Bits products that belongs to an Extension.

        # Authorization:
        - App Access Token associated with the Extension client ID

        # URL:
        `PUT https://api.twitch.tv/helix/bits/extensions`

        # Pagination Support:
        Not applicable.

        # Required Body Parameters:
        +----------------+---------+---------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Type    | Description                                                                                                                           |
        +----------------+---------+---------------------------------------------------------------------------------------------------------------------------------------+
        | `sku`          | string  | SKU of the Bits product. This must be unique across all products that belong to an Extension. The SKU cannot be changed after saving. |
        |                |         |                                                                                                                                       |
        |                |         | Maximum: 255 characters, no white spaces.                                                                                             |
        +----------------+---------+---------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`         | object  | Object containing cost information.                                                                                                   |
        +----------------+---------+---------------------------------------------------------------------------------------------------------------------------------------+
        | `cost.amount`  | integer | Number of Bits for which the product will be exchanged.                                                                               |
        |                |         |                                                                                                                                       |
        |                |         | Minimum: 1, Maximum: 10000.                                                                                                           |
        +----------------+---------+---------------------------------------------------------------------------------------------------------------------------------------+
        | `cost.type`    | string  | Cost type. The one valid value is `"bits"`.                                                                                           |
        +----------------+---------+---------------------------------------------------------------------------------------------------------------------------------------+
        | `display_name` | string  | Name of the product to be displayed in the Extension.                                                                                 |
        |                |         |                                                                                                                                       |
        |                |         | Maximum: 255 characters.                                                                                                              |
        +----------------+---------+---------------------------------------------------------------------------------------------------------------------------------------+

        # Optional Body Parameters:
        +------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type    | Description                                                                                                                                                                        |
        +------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `in_development` | boolean | Set to `true` if the product is in development and not yet released for public use.                                                                                                |
        |                  |         |                                                                                                                                                                                    |
        |                  |         | Default: `false`.                                                                                                                                                                  |
        +------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `expiration`     | string  | Expiration time for the product in RFC3339 format. If not provided, the Bits product will not have an expiration date. Setting an expiration in the past will disable the product. |
        +------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_broadcast`   | boolean | Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback.                             |
        |                  |         |                                                                                                                                                                                    |
        |                  |         | Default: `false`.                                                                                                                                                                  |
        +------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type    | Description                                                                                                                                            |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `sku`            | string  | SKU of the Bits product. This is unique across all products that belong to an Extension.                                                               |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`           | object  | Object containing cost information.                                                                                                                    |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost.amount`    | integer | Number of Bits for which the product will be exchanged.                                                                                                |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost.type`      | string  | Cost type. The one valid value is `"bits"`.                                                                                                            |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `in_development` | boolean | Indicates if the product is in development and not yet released for public use.                                                                        |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `display_name`   | string  | Name of the product to be displayed in the Extension.                                                                                                  |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `expiration`     | string  | Expiration time for the product in RFC3339 format.                                                                                                     |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_broadcast`   | boolean | Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback. |
        +------------------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+---------------------------------------------+
        | Code | Meaning                                     |
        +------+---------------------------------------------+
        | 200  | Bits product added or updated successfully. |
        +------+---------------------------------------------+
        | 400  | Request was invalid.                        |
        +------+---------------------------------------------+
        | 401  | Authorization failed.                       |
        +------+---------------------------------------------+
        """
        _cost = exclude_non_empty(amount=cost_amount, type=cost_type)
        data = exclude_non_empty(
            cost=_cost or _empty,
            display_name=display_name,
            expiration=expiration,
            in_development=in_development,
            is_broadcast=is_broadcast,
            sku=sku,
        )
        return await self._request('PUT', 'bits/extensions', data=data)

    async def create_eventsub_subscription(
        self, *, condition: Dict[str, Any], transport: Dict[str, Any], type_: str, version: str
    ):
        """
        Creates an EventSub subscription.

        # Authentication:
        Requires an app access token.

        To create a subscription, you must use an app access token; however, if the subscription type requires user authorization, the user must have granted your app permissions to receive those events before you subscribe to them. For example, to subscribe to channel.subscribe events, the user must have granted your app permission which adds the `channel:read:subscriptions` scope to your app’s client ID.

        # URL:
        `POST https://api.twitch.tv/helix/eventsub/subscriptions`

        # Required Query Parameters:
        None

        # Required Body Parameters:
        +-------------+-----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter   | Type      | Description                                                                                                                                                                         |
        +-------------+-----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`      | string    | The type of subscription to create. For a list of subscriptions you can create, see Subscription Types. Set `type` to the value in the Name column of the Subscription Types table. |
        +-------------+-----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `version`   | string    | The version of the subscription type used in this request. A subscription type could define one or more object definitions, so you need to specify which definition you’re using.   |
        +-------------+-----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `condition` | condition | The parameter values that are specific to the specified subscription type.                                                                                                          |
        +-------------+-----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `transport` | transport | The transport details, such as the transport method and callback URL, that you want Twitch to use when sending you notifications.                                                   |
        +-------------+-----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field            | Type         | Description                                                                                                                                                                                                                                                     |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`           | object array | An array of subscription objects. The array will contain only one element.                                                                                                                                                                                      |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`             | string       | An ID that identifies the subscription.                                                                                                                                                                                                                         |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`         | string       | The status of the create subscription request. Possible values are:                                                                                                                                                                                             |
        |                  |              | - enabled — The subscription is enabled.                                                                                                                                                                                                                        |
        |                  |              | - webhook_callback_verification_pending — The subscription is pending verification of the specified callback URL. To determine if the subscription moved from pending to another state, send a GET request and use the ID to find the subscription in the list. |
        |                  |              | - webhook_callback_verification_failed — The specified callback URL failed verification.                                                                                                                                                                        |
        |                  |              | - notification_failures_exceeded — The notification delivery failure rate was too high.                                                                                                                                                                         |
        |                  |              | - authorization_revoked — The authorization was revoked for one or more users specified in the Condition object.                                                                                                                                                |
        |                  |              | - user_removed — One of the users specified in the Condition object was removed.                                                                                                                                                                                |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`           | string       | The type of subscription.                                                                                                                                                                                                                                       |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `version`        | string       | The version of the subscription type.                                                                                                                                                                                                                           |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `condition`      | condition    | The parameter values for the subscription type.                                                                                                                                                                                                                 |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`     | string       | The RFC 3339 timestamp indicating when the subscription was created.                                                                                                                                                                                            |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `transport`      | transport    | The transport details used to send you notifications.                                                                                                                                                                                                           |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`           | integer      | The amount that the subscription counts against your limit. Learn More                                                                                                                                                                                          |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total`          | integer      | The total number of subscriptions you’ve created.                                                                                                                                                                                                               |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total_cost`     | integer      | The sum of all of your subscription costs. Learn More                                                                                                                                                                                                           |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_total_cost` | integer      | The maximum total cost that you may incur for all subscriptions you create.                                                                                                                                                                                     |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                  |
        +------+------------------------------------------------------------------------------------------+
        | 201  | Successfully created the subscription.                                                   |
        +------+------------------------------------------------------------------------------------------+
        | 400  | The request was invalid.                                                                 |
        +------+------------------------------------------------------------------------------------------+
        | 401  | The caller failed authentication. Verify that your access token and client ID are valid. |
        +------+------------------------------------------------------------------------------------------+
        | 403  | The caller is not authorized to subscribe to the event.                                  |
        +------+------------------------------------------------------------------------------------------+
        | 409  | The subscription already exists.                                                         |
        +------+------------------------------------------------------------------------------------------+
        """
        data = exclude_non_empty(condition=condition, transport=transport, type=type_, version=version)
        return await self._request('POST', 'eventsub/subscriptions', data=data)

    async def delete_eventsub_subscription(self, *, id_: str):
        """
        Deletes an EventSub subscription.

        # Authentication:
        Requires an application OAuth access token.

        # URL:
        `DELETE https://api.twitch.tv/helix/eventsub/subscriptions`

        # Required Query Parameters:
        +------+--------+-------------------------------------------------------------------------------------------------+
        | Name | Type   | Description                                                                                     |
        +------+--------+-------------------------------------------------------------------------------------------------+
        | `id` | string | The ID of the subscription to delete. This is the ID that Create Eventsub Subscription returns. |
        +------+--------+-------------------------------------------------------------------------------------------------+

        # Response Fields:
        None

        # Response Codes:
        +------+------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                  |
        +------+------------------------------------------------------------------------------------------+
        | 204  | Successfully deleted the subscription.                                                   |
        +------+------------------------------------------------------------------------------------------+
        | 404  | The subscription was not found.                                                          |
        +------+------------------------------------------------------------------------------------------+
        | 401  | The caller failed authentication. Verify that your access token and client ID are valid. |
        +------+------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(id=id_)
        return await self._request('DELETE', 'eventsub/subscriptions', params=params)

    async def get_eventsub_subscriptions(self, *, after: str = _empty, status: str = _empty, type_: str = _empty):
        """
        Gets a list of your EventSub subscriptions. The list is paginated and ordered by the oldest subscription first.

        # Authentication:
        Requires an application OAuth access token.

        # URL:
        `GET https://api.twitch.tv/helix/eventsub/subscriptions`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        Use the `status` and `type` query parameters to filter the list of subscriptions that are returned. You may specify only one filter query parameter (i.e., specify either the `status` or `type` parameter, but not both). The request fails if you specify both filter parameters.

        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                   |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `status`  | string | Filter subscriptions by its status. You may specify only one status value. Valid values are:                                  |
        |           |        | - enabled — The subscription is enabled.                                                                                      |
        |           |        | - webhook_callback_verification_pending — The subscription is pending verification of the specified callback URL.             |
        |           |        | - webhook_callback_verification_failed — The specified callback URL failed verification.                                      |
        |           |        | - notification_failures_exceeded — The notification delivery failure rate was too high.                                       |
        |           |        | - authorization_revoked — The authorization was revoked for one or more users specified in the Condition object.              |
        |           |        | - user_removed — One of the users specified in the Condition object was removed.                                              |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `type`    | string | Filter subscriptions by subscription type (e.g., `channel.update`). For a list of subscription types, see Subscription Types. |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | The cursor used to get the next page of results. The `pagination` object in the response contains the cursor’s value.         |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field            | Type         | Description                                                                                                                                                                                                                                         |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`           | object array | An array of subscription objects. The list is empty if you don’t have any subscriptions.                                                                                                                                                            |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`             | string       | An ID that identifies the subscription.                                                                                                                                                                                                             |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`         | string       | The subscription’s status. Possible values are:                                                                                                                                                                                                     |
        |                  |              | - enabled — The subscription is enabled.                                                                                                                                                                                                            |
        |                  |              | - webhook_callback_verification_pending — The subscription is pending verification of the specified callback URL.                                                                                                                                   |
        |                  |              | - webhook_callback_verification_failed — The specified callback URL failed verification.                                                                                                                                                            |
        |                  |              | - notification_failures_exceeded — The notification delivery failure rate was too high.                                                                                                                                                             |
        |                  |              | - authorization_revoked — The authorization was revoked for one or more users specified in the Condition object.                                                                                                                                    |
        |                  |              | - user_removed — One of the users specified in the Condition object was removed.                                                                                                                                                                    |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`           | string       | The subscription’s type.                                                                                                                                                                                                                            |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `version`        | string       | The version of the subscription type.                                                                                                                                                                                                               |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `condition`      | condition    | The subscription’s parameter values.                                                                                                                                                                                                                |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`     | string       | The RFC 3339 timestamp indicating when the subscription was created.                                                                                                                                                                                |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `transport`      | transport    | The transport details used to send you notifications.                                                                                                                                                                                               |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cost`           | integer      | The amount that the subscription counts against your limit. Learn More                                                                                                                                                                              |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total`          | integer      | The total number of subscriptions you’ve created.                                                                                                                                                                                                   |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total_cost`     | integer      | The sum of all of your subscription costs. Learn More                                                                                                                                                                                               |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `max_total_cost` | integer      | The maximum total cost that you’re allowed to incur for all subscriptions you create.                                                                                                                                                               |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`     | object       | An object that contains the cursor used to get the next page of subscriptions. The object is empty if the list of subscriptions fits on one page or there are no more pages to get. The number of subscriptions returned per page is undetermined. |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cursor`         | string       | The cursor value that you set the `after` query parameter to.                                                                                                                                                                                       |
        +------------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                  |
        +------+------------------------------------------------------------------------------------------+
        | 200  | Successfully retrieved the subscriptions.                                                |
        +------+------------------------------------------------------------------------------------------+
        | 400  | The request was invalid.                                                                 |
        +------+------------------------------------------------------------------------------------------+
        | 401  | The caller failed authentication. Verify that your access token and client ID are valid. |
        +------+------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, status=status, type=type_)
        return await self._request('GET', 'eventsub/subscriptions', params=params)

    async def get_top_games(self, *, after: str = _empty, before: str = _empty, first: int = _empty):
        """
        Gets games sorted by number of current viewers on Twitch, most popular first.

        The response has a JSON payload with a `data` field containing an array of games information elements and a `pagination` field containing information required to query for more streams.

        # Authentication:
        OAuth or App Access Token required.

        # URL:
        `GET https://api.twitch.tv/helix/games/top`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name     | Type    | Description                                                                                                                                                                                                           |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`  | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.  |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `before` | string  | Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`  | integer | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                       |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +---------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | Field         | Type                       | Description                                                                                                  |
        +---------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `box_art_url` | object                     | Template URL for a game’s box art.                                                                           |
        +---------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `id`          | string                     | Game ID.                                                                                                     |
        +---------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `name`        | string                     | Game name.                                                                                                   |
        +---------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `pagination`  | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results. |
        +---------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, before=before, first=first)
        return await self._request('GET', 'games/top', params=params)

    async def get_games(self, *, id_: str, name: str):
        """
        Gets game information by game ID or name.

        The response has a JSON payload with a `data` field containing an array of games elements.

        # Authentication:
        OAuth or App Access Token required.

        # URL:
        `GET https://api.twitch.tv/helix/games`

        # Required Query Parameters:
        +--------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name   | Type   | Description                                                                                                                                                                                                                    |
        +--------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`   | string | Game ID. At most 100 `id` values can be specified.                                                                                                                                                                             |
        +--------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `name` | string | Game name. The name must be an exact match. For example, “Pokemon” will not return a list of Pokemon games; instead, query any specific Pokemon games in which you are interested. At most 100 `name` values can be specified. |
        +--------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        For a query to be valid, `name` and/or `id` must be specified.

        # Optional Query Parameters:
        None

        # Response Fields:
        +---------------+--------+--------------------------------------+
        | Fields        | Type   | Description                          |
        +---------------+--------+--------------------------------------+
        | `box_art_url` | object | Template URL for the game’s box art. |
        +---------------+--------+--------------------------------------+
        | `id`          | string | Game ID.                             |
        +---------------+--------+--------------------------------------+
        | `name`        | string | Game name.                           |
        +---------------+--------+--------------------------------------+
        """
        params = exclude_non_empty(id=id_, name=name)
        return await self._request('GET', 'games', params=params)

    async def get_creator_goals(self, *, broadcaster_id: str):
        """
        NEW Gets the broadcaster’s list of active goals. Use this to get the current progress of each goal.

        Alternatively, you can subscribe to receive notifications when a goal makes progress using the channel.goal.progress subscription type. Read more

        # Authorization:
        Requires a user OAuth access token with scope set to channel:read:goals. The ID in the `broadcaster_id` query parameter must match the user ID associated with the user OAuth token. In other words, only the broadcaster can see their goals.

        # URL:
        `GET https://api.twitch.tv/helix/goals`

        # Required Query Parameters:
        +------------------+--------+---------------------------------------------------+
        | Parameter        | Type   | Description                                       |
        +------------------+--------+---------------------------------------------------+
        | `broadcaster_id` | string | The ID of the broadcaster that created the goals. |
        +------------------+--------+---------------------------------------------------+

        # Response Fields:
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field               | Type         | Description                                                                                                                                                                                                                                  |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`              | object array | An array of creator goals. The array will contain at most one goal. The array is empty if the broadcaster hasn’t created goals.                                                                                                              |
        |                     |              |                                                                                                                                                                                                                                              |
        |                     |              | NOTE: Although the API currently supports only one goal, you should write your application to support one or more goals.                                                                                                                     |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                | string       | An ID that uniquely identifies this goal.                                                                                                                                                                                                    |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`    | string       | An ID that uniquely identifies the broadcaster.                                                                                                                                                                                              |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`  | string       | The broadcaster’s display name.                                                                                                                                                                                                              |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login` | string       | The broadcaster’s user handle.                                                                                                                                                                                                               |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`              | string       | The type of goal. Possible values are:                                                                                                                                                                                                       |
        |                     |              | - follower — The goal is to increase followers.                                                                                                                                                                                              |
        |                     |              | - subscription — The goal is to increase subscriptions. This type shows the net increase or decrease in subscriptions.                                                                                                                       |
        |                     |              | - new_subscription — The goal is to increase subscriptions. This type shows only the net increase in subscriptions (it does not account for users that stopped subscribing since the goal's inception).                                      |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `description`       | string       | A description of the goal, if specified. The description may contain a maximum of 40 characters.                                                                                                                                             |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `current_amount`    | integer      | The current value.                                                                                                                                                                                                                           |
        |                     |              |                                                                                                                                                                                                                                              |
        |                     |              | If the goal is to increase followers, this field is set to the current number of followers. This number increases with new followers and decreases if users unfollow the channel.                                                            |
        |                     |              |                                                                                                                                                                                                                                              |
        |                     |              | For subscriptions, `current_amount` is increased and decreased by the points value associated with the subscription tier. For example, if a tier-two subscription is worth 2 points, `current_amount` is increased or decreased by 2, not 1. |
        |                     |              |                                                                                                                                                                                                                                              |
        |                     |              | For new_subscriptions, `current_amount` is increased by the points value associated with the subscription tier. For example, if a tier-two subscription is worth 2 points, `current_amount` is increased by 2, not 1.                        |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `target_amount`     | integer      | The goal’s target value. For example, if the broadcaster has 200 followers before creating the goal, and their goal is to double that number, this field is set to 400.                                                                      |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`        | string       | The UTC timestamp in RFC 3339 format, which indicates when the broadcaster created the goal.                                                                                                                                                 |
        +---------------------+--------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                                                                                                                |
        +------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 200  | Successfully retrieved the broadcaster’s goals.                                                                                                                                        |
        +------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 400  | The request was invalid. Make sure the broadcaster’s ID you specified in `broadcaster_id` is correct.                                                                                  |
        +------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | 401  | The caller failed authentication. Returned if the user is valid but missing the correct scopes, or if the user is valid but the broadcaster ID doesn't match the user ID in the token. |
        +------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'goals', params=params)

    async def get_hype_train_events(
        self, *, broadcaster_id: str, cursor: str = _empty, first: int = _empty, id_: str = _empty
    ):
        """
        # Description: Gets the information of the most recent Hype Train of the given channel ID. When there is
        currently an active Hype Train, it returns information about that Hype Train. When there is currently no active
        Hype Train, it returns information about the most recent Hype Train. After 5 days, if no Hype Train has been
        active, the endpoint will return an empty response.

        # Authentication:
        - User OAuth Token

        - Required scope: `channel:read:hype_train`

        # URL:
        `GET https://api.twitch.tv/helix/hypetrain/events`

        # Required Query Parameter:
        +------------------+--------+-----------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                   |
        +------------------+--------+-----------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster. Must match the User ID in the Bearer token if User Token is used. |
        +------------------+--------+-----------------------------------------------------------------------------------------------+

        # Optional Query Parameters:
        +-----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type    | Description                                                                                                                                                                                                                                                                                                                     |
        +-----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | integer | Maximum number of objects to return. Maximum: 100. Default: 1.                                                                                                                                                                                                                                                                  |
        +-----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`      | string  | The id of the wanted event, if known                                                                                                                                                                                                                                                                                            |
        +-----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cursor`  | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without id. If an ID is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the pagination response field of a prior query. |
        +-----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Type    | Description                                                                                                                                                                                                                                                                                                                                                |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                | string  | The distinct ID of the event                                                                                                                                                                                                                                                                                                                               |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `event_type`        | string  | Displays hypetrain.{event_name}, currently only hypetrain.progression                                                                                                                                                                                                                                                                                      |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `event_timestamp`   | string  | RFC3339 formatted timestamp of event                                                                                                                                                                                                                                                                                                                       |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `version`           | string  | Returns the version of the endpoint                                                                                                                                                                                                                                                                                                                        |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `event_data`        | object  | (See below for the schema)                                                                                                                                                                                                                                                                                                                                 |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                | string  | The distinct ID of this Hype Train                                                                                                                                                                                                                                                                                                                         |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`    | string  | Channel ID of which Hype Train events the clients are interested in                                                                                                                                                                                                                                                                                        |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at`        | string  | RFC3339 formatted timestamp of when this Hype Train started                                                                                                                                                                                                                                                                                                |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `expires_at`        | string  | RFC3339 formatted timestamp of the expiration time of this Hype Train                                                                                                                                                                                                                                                                                      |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cooldown_end_time` | string  | RFC3339 formatted timestamp of when another Hype Train can be started again                                                                                                                                                                                                                                                                                |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `level`             | integer | The highest level (in the scale of 1-5) reached of the Hype Train                                                                                                                                                                                                                                                                                          |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `goal`              | integer | The goal value of the level above                                                                                                                                                                                                                                                                                                                          |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total`             | integer | The total score so far towards completing the level goal above                                                                                                                                                                                                                                                                                             |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `top_contributions` | object  | An array of top contribution objects, one object for each type. For example, one object would represent top contributor of `BITS`, by aggregate, and one would represent top contributor of `SUBS` by count.                                                                                                                                               |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total`             | integer | Total aggregated amount of all contributions by the top contributor. If type is `BITS`, total represents aggregate amount of bits used. If type is `SUBS`, aggregate total where 500, 1000, or 2500 represent tier 1, 2, or 3 subscriptions respectively. For example, if top contributor has gifted a tier 1, 2, and 3 subscription, total would be 4000. |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`              | string  | Identifies the contribution method, either `BITS `or `SUBS`                                                                                                                                                                                                                                                                                                |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user`              | string  | ID of the contributing user                                                                                                                                                                                                                                                                                                                                |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `last_contribution` | object  | An object that represents the most recent contribution                                                                                                                                                                                                                                                                                                     |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total`             | integer | Total amount contributed. If type is `BITS`, total represents amounts of bits used. If type is `SUBS`, total is 500, 1000, or 2500 to represent tier 1, 2, or 3 subscriptions respectively                                                                                                                                                                 |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`              | string  | Identifies the contribution method, either `BITS `or `SUBS`                                                                                                                                                                                                                                                                                                |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user`              | string  | ID of the contributing user                                                                                                                                                                                                                                                                                                                                |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`        | string  | A cursor value, to be used in a subsequent requests to specify the starting point of the next set of results                                                                                                                                                                                                                                               |
        +---------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, cursor=cursor, first=first, id=id_)
        return await self._request('GET', 'hypetrain/events', params=params)

    async def check_automod_status(self, *, broadcaster_id: str, msg_id: str, msg_text: str, user_id: str):
        """
        Determines whether a string message meets the channel’s AutoMod requirements.

        AutoMod is a moderation tool that blocks inappropriate or harassing chat with powerful moderator control. AutoMod detects misspellings and evasive language automatically. AutoMod uses machine learning and natural language processing algorithms to hold risky messages from chat so they can be reviewed by a channel moderator before appearing to other viewers in the chat. Moderators can approve or deny any message caught by AutoMod.

        For more information about AutoMod, see How to Use AutoMod.

        # Authorization:
        - OAuth token required

        - Required Scope: `moderation:read`

        # URL:
        `POST https://api.twitch.tv/helix/moderation/enforcements/status`

        # Pagination Support:
        None.

        # Query Parameter:
        +------------------+----------+--------+-----------------------------------------------------------------------+
        | Parameter        | Required | Type   | Description                                                           |
        +------------------+----------+--------+-----------------------------------------------------------------------+
        | `broadcaster_id` | yes      | string | Provided `broadcaster_id` must match the `user_id` in the auth token. |
        +------------------+----------+--------+-----------------------------------------------------------------------+

        # Body Parameters:
        +------------+----------+--------+-----------------------------------------------------------------+
        | Parameter  | Required | Type   | Description                                                     |
        +------------+----------+--------+-----------------------------------------------------------------+
        | `msg_id`   | yes      | string | Developer-generated identifier for mapping messages to results. |
        +------------+----------+--------+-----------------------------------------------------------------+
        | `msg_text` | yes      | string | Message text.                                                   |
        +------------+----------+--------+-----------------------------------------------------------------+
        | `user_id`  | yes      | string | User ID of the sender.                                          |
        +------------+----------+--------+-----------------------------------------------------------------+

        # Return Values:
        +----------------+---------+-----------------------------------------------------------------------------------------+
        | Parameter      | Type    | Description                                                                             |
        +----------------+---------+-----------------------------------------------------------------------------------------+
        | `msg_id`       | string  | The `msg_id` passed in the body of the `POST` message. Maps each message to its status. |
        +----------------+---------+-----------------------------------------------------------------------------------------+
        | `is_permitted` | Boolean | Indicates if this message meets AutoMod requirements.                                   |
        +----------------+---------+-----------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        data = exclude_non_empty(msg_id=msg_id, msg_text=msg_text, user_id=user_id)
        return await self._request('POST', 'moderation/enforcements/status', params=params, data=data)

    async def manage_held_automod_messages(self, *, action: str, msg_id: str, user_id: str):
        """
        Allow or deny a message that was held for review by AutoMod.

        In order to retrieve messages held for review, use the `chat_moderator_actions` topic via PubSub. For more information about AutoMod, see How to Use AutoMod.

        # Authorization:
        - User OAuth token required

        - Required Scope: `moderator:manage:automod`

        Note that the scope allows this endpoint to be used for any channel that the authenticated user is a moderator, including their own channel.

        # URL:
        `POST https://api.twitch.tv/helix/moderation/automod/message`

        # Required Body Parameters:
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                     |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | The moderator who is approving or rejecting the held message. Must match the `user_id` in the user OAuth token.                                 |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `msg_id`  | string | ID of the message to be allowed or denied. These message IDs are retrieved from PubSub as mentioned above. Only one message ID can be provided. |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `action`  | string | The action to take for the message. Must be `"ALLOW"` or `"DENY"`.                                                                              |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-------------------------------------------------------------------------+
        | Code | Meaning                                                                 |
        +------+-------------------------------------------------------------------------+
        | 204  | Message was approved or denied successfully.                            |
        +------+-------------------------------------------------------------------------+
        | 400  | Message was already processed or an invalid action was provided.        |
        +------+-------------------------------------------------------------------------+
        | 401  | Authentication failure.                                                 |
        +------+-------------------------------------------------------------------------+
        | 403  | Requesting user is not authorized to process messages for this channel. |
        +------+-------------------------------------------------------------------------+
        | 404  | Message not found or invalid `msg_id`.                                  |
        +------+-------------------------------------------------------------------------+
        """
        data = exclude_non_empty(action=action, msg_id=msg_id, user_id=user_id)
        return await self._request('POST', 'moderation/automod/message', data=data)

    async def get_automod_settings(self, *, broadcaster_id: str, moderator_id: str):
        """
        NEW Gets the broadcaster’s AutoMod settings, which are used to automatically block inappropriate or harassing
        messages from appearing in the broadcaster’s chat room.

        # Authorization:
        Requires a User access token with scope set to `moderator:read:automod_settings`.

        # URL:
        `GET https://api.twitch.tv/helix/moderation/automod/settings`

        # Query Parameters:
        +----------------+----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                          |
        +----------------+----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster whose AutoMod settings you want to get.                                                                                    |
        +----------------+----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.   |
        |                |          |        |                                                                                                                                                      |
        |                |          |        | If the broadcaster wants to get their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too. |
        +----------------+----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | Field                      | Type     | Description                                                                                                                          |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | data                       | object[] | The list of AutoMod settings. The list contains a single object that contains all the AutoMod settings.                              |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | aggression                 | Integer  | The Automod level for hostility involving aggression.                                                                                |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id             | String   | The broadcaster’s ID.                                                                                                                |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | bullying                   | Integer  | The Automod level for hostility involving name calling or insults.                                                                   |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | disability                 | Integer  | The Automod level for discrimination against disability.                                                                             |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | misogyny                   | Integer  | The Automod level for discrimination against women.                                                                                  |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id               | String   | The moderator’s ID.                                                                                                                  |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | overall_level              | Integer  | The default AutoMod level for the broadcaster. This field is null if the broadcaster has set one or more of the individual settings. |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | race_ethnicity_or_religion | Integer  | The Automod level for racial discrimination.                                                                                         |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | sex_based_terms            | Integer  | The Automod level for sexual content.                                                                                                |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | sexuality_sex_or_gender    | Integer  | The AutoMod level for discrimination based on sexuality, sex, or gender.                                                             |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | swearing                   | Integer  | The Automod level for profanity.                                                                                                     |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-------------------------+
        | Code | Meaning                 |
        +------+-------------------------+
        | 200  | Success.                |
        +------+-------------------------+
        | 400  | Malformed request.      |
        +------+-------------------------+
        | 401  | Authentication failure. |
        +------+-------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        return await self._request('GET', 'moderation/automod/settings', params=params)

    async def update_automod_settings(
        self,
        *,
        broadcaster_id: str,
        moderator_id: str,
        aggression: int = _empty,
        bullying: int = _empty,
        disability: int = _empty,
        misogyny: int = _empty,
        overall_level: int = _empty,
        race_ethnicity_or_religion: int = _empty,
        sex_based_terms: int = _empty,
        sexuality_sex_or_gender: int = _empty,
        swearing: int = _empty,
    ):
        """
        NEW Updates the broadcaster’s AutoMod settings, which are used to automatically block inappropriate or harassing
        messages from appearing in the broadcaster’s chat room.

        # Authorization:
        Requires a User access token with scope set to `moderator:manage:automod_settings`.

        # URL:
        `PUT https://api.twitch.tv/helix/moderation/automod/settings`

        # Query Parameters:
        +----------------+----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                             |
        +----------------+----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster whose AutoMod settings you want to update.                                                                                    |
        +----------------+----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.      |
        |                |          |        |                                                                                                                                                         |
        |                |          |        | If the broadcaster wants to update their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too. |
        +----------------+----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Request Body:
        Because PUT is an overwrite operation, you must include all the fields you want set after the operation completes. Typically, you’ll send a GET request, update the fields you want to change, and pass that object in the PUT request.

        You can set either `overall_level` or the individual settings like `aggression`, but not both.

        Setting `overall_level` applies default values to the individual settings. However, setting `overall_level` to 4 does not mean that it applies 4 to all the individual settings. Instead, it applies a set of recommended defaults to the rest of the settings. For example, if you set `overall_level` to 2, Twitch provides some filtering on discrimination and sexual content, but more filtering on hostility (see the first example response).

        If `overall_level` is currently set and you update `swearing` to 3,  `overall_level` will be set to null and all settings other than `swearing` will be set to 0. The same is true if individual settings are set and you update `overall_level` to 3 — all the individual settings are updated to reflect the default level.

        Note that if you set all the individual settings to values that match what `overall_level` would have set them to, Twitch changes AutoMod to use the default AutoMod level instead of using the individual settings.

        Valid values for all levels are from 0 (no filtering) through 4 (most aggressive filtering). These levels affect how aggressively AutoMod holds back messages for moderators to review before they appear in chat or are denied (not shown).

        +----------------------------+---------+--------------------------------------------------------------------------+
        | Field                      | Type    | Description                                                              |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | aggression                 | Integer | The Automod level for hostility involving aggression.                    |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | bullying                   | Integer | The Automod level for hostility involving name calling or insults.       |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | disability                 | Integer | The Automod level for discrimination against disability.                 |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | misogyny                   | Integer | The Automod level for discrimination against women.                      |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | overall_level              | Integer | The default AutoMod level for the broadcaster.                           |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | race_ethnicity_or_religion | Integer | The Automod level for racial discrimination.                             |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | sex_based_terms            | Integer | The Automod level for sexual content.                                    |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | sexuality_sex_or_gender    | Integer | The AutoMod level for discrimination based on sexuality, sex, or gender. |
        +----------------------------+---------+--------------------------------------------------------------------------+
        | swearing                   | Integer | The Automod level for profanity.                                         |
        +----------------------------+---------+--------------------------------------------------------------------------+

        # Response Body:
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | Field                      | Type     | Description                                                                                                                          |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | data                       | object[] | The list of AutoMod settings. The list contains a single object that contains all the AutoMod settings.                              |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | aggression                 | Integer  | The Automod level for hostility involving aggression.                                                                                |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id             | String   | The broadcaster’s ID.                                                                                                                |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | bullying                   | Integer  | The Automod level for hostility involving name calling or insults.                                                                   |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | disability                 | Integer  | The Automod level for discrimination against disability.                                                                             |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | misogyny                   | Integer  | The Automod level for discrimination against women.                                                                                  |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id               | String   | The moderator’s ID.                                                                                                                  |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | overall_level              | Integer  | The default AutoMod level for the broadcaster. This field is null if the broadcaster has set one or more of the individual settings. |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | race_ethnicity_or_religion | Integer  | The Automod level for racial discrimination.                                                                                         |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | sex_based_terms            | Integer  | The Automod level for sexual content.                                                                                                |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | sexuality_sex_or_gender    | Integer  | The AutoMod level for discrimination based on sexuality, sex, or gender.                                                             |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+
        | swearing                   | Integer  | The Automod level for profanity.                                                                                                     |
        +----------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-------------------------+
        | Code | Meaning                 |
        +------+-------------------------+
        | 200  | Success.                |
        +------+-------------------------+
        | 400  | Malformed request.      |
        +------+-------------------------+
        | 401  | Authentication failure. |
        +------+-------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        data = exclude_non_empty(
            aggression=aggression,
            bullying=bullying,
            disability=disability,
            misogyny=misogyny,
            overall_level=overall_level,
            race_ethnicity_or_religion=race_ethnicity_or_religion,
            sex_based_terms=sex_based_terms,
            sexuality_sex_or_gender=sexuality_sex_or_gender,
            swearing=swearing,
        )
        return await self._request('PUT', 'moderation/automod/settings', params=params, data=data)

    async def get_banned_events(
        self, *, after: str = _empty, broadcaster_id: str, first: str = _empty, user_id: Union[str, List[str]] = _empty
    ):
        """
        Returns all user ban and un-ban events for a channel.

        # Authorization:
        - OAuth token required

        - Required Scope: `moderation:read`

        # URL:
        `GET https://api.twitch.tv/helix/moderation/banned/events`

        # Pagination Support:
        Forward pagination.

        # Required Query Parameter:
        +------------------+--------+------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                            |
        +------------------+--------+------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the OAuth token. |
        +------------------+--------+------------------------------------------------------------------------+

        # Optional Query Parameters:
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                                                                                                                                                                                                                    |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | Filters the results to only include users being banned or un-banned in the specified channel based on their user ID.                                                                                                                                                                                                                           |
        |           |        |                                                                                                                                                                                                                                                                                                                                                |
        |           |        | Multiple user IDs can be provided, e.g. `/moderation/banned/events?broadcaster_id=1&user_id=2&user_id=3`                                                                                                                                                                                                                                       |
        |           |        |                                                                                                                                                                                                                                                                                                                                                |
        |           |        | Maximum: 100.                                                                                                                                                                                                                                                                                                                                  |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | string | Maximum number of objects to return.                                                                                                                                                                                                                                                                                                           |
        |           |        |                                                                                                                                                                                                                                                                                                                                                |
        |           |        | Maximum: 100.                                                                                                                                                                                                                                                                                                                                  |
        |           |        | Default: 20.                                                                                                                                                                                                                                                                                                                                   |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | Parameter                      | Type                       | Description                                                                                                  |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `id`                           | string                     | Event ID.                                                                                                    |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_type`                   | string                     | Type of ban event, either `moderation.user.ban` or `moderation.user.unban`.                                  |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_timestamp`              | string                     | RFC3339 formatted timestamp for events.                                                                      |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `version`                      | string                     | Version of the endpoint.                                                                                     |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data`                   | object                     | Information about the ban event.                                                                             |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data.broadcaster_id`    | string                     | User ID of the broadcaster.                                                                                  |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data.broadcaster_login` | string                     | Login of the broadcaster.                                                                                    |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data.broadcaster_name`  | string                     | Display name of the broadcaster.                                                                             |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data.user_id`           | string                     | User ID of the banned user.                                                                                  |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data.user_login`        | string                     | Login of the banned user.                                                                                    |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data.user_name`         | string                     | Display name of the banned user.                                                                             |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `event_data.expires_at`        | string                     | Timestamp of the ban expiration. Set to empty string if the ban is permanent.                                |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `reason`                       | string                     | The reason for the ban if provided by the moderator.                                                         |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `moderator_id`                 | string                     | User ID of the moderator who initiated the ban.                                                              |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `moderator_login`              | string                     | Login of the moderator who initiated the ban.                                                                |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `moderator_name`               | string                     | Display name of the moderator who initiated the ban.                                                         |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `pagination`                   | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results. |
        +--------------------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first, user_id=user_id)
        return await self._request('GET', 'moderation/banned/events', params=params)

    async def get_banned_users(
        self,
        *,
        after: str = _empty,
        before: str = _empty,
        broadcaster_id: str,
        first: str = _empty,
        user_id: Union[str, List[str]] = _empty,
    ):
        """
        Returns all banned and timed-out users for a channel.

        # Authentication:
        - OAuth token required

        - Required scope: `moderation:read`

        # URL:
        `GET https://api.twitch.tv/helix/moderation/banned`

        # Pagination Support:
        Forward and reverse pagination.

        # Required Query Parameter:
        +------------------+--------+------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                            |
        +------------------+--------+------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the OAuth token. |
        +------------------+--------+------------------------------------------------------------------------+

        # Optional Query Parameters:
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                                                                                                                                                                                                                      |
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | Filters the results and only returns a status object for users who are banned in the channel and have a matching user_id.                                                                                                                                                                                                                        |
        |           |        |                                                                                                                                                                                                                                                                                                                                                  |
        |           |        | Multiple user IDs can be provided, e.g. `/moderation/banned/events?broadcaster_id=1&user_id=2&user_id=3`                                                                                                                                                                                                                                         |
        |           |        |                                                                                                                                                                                                                                                                                                                                                  |
        |           |        | Maximum: 100.                                                                                                                                                                                                                                                                                                                                    |
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | string | Maximum number of objects to return.                                                                                                                                                                                                                                                                                                             |
        |           |        |                                                                                                                                                                                                                                                                                                                                                  |
        |           |        | Maximum: 100.                                                                                                                                                                                                                                                                                                                                    |
        |           |        | Default: 1.                                                                                                                                                                                                                                                                                                                                      |
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query.   |
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `before`  | string | Cursor for backward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset. combinations. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+--------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | Parameter         | Type                       | Description                                                                                                  |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `user_id`         | string                     | User ID of the banned user.                                                                                  |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `user_login`      | string                     | Login of the banned user.                                                                                    |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `user_name`       | string                     | Display name of the banned user.                                                                             |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `expires_at`      | string                     | Timestamp of the ban expiration. Set to empty string if the ban is permanent.                                |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `reason`          | string                     | The reason for the ban if provided by the moderator.                                                         |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `moderator_id`    | string                     | User ID of the moderator who initiated the ban.                                                              |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `moderator_login` | string                     | Login of the moderator who initiated the ban.                                                                |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `moderator_name`  | string                     | Display name of the moderator who initiated the ban.                                                         |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        | `pagination`      | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results. |
        +-------------------+----------------------------+--------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after, before=before, broadcaster_id=broadcaster_id, first=first, user_id=user_id
        )
        return await self._request('GET', 'moderation/banned', params=params)

    async def ban_user(
        self, *, broadcaster_id: str, moderator_id: str, duration: int = _empty, reason: str, user_id: str
    ):
        """
        NEW Bans a user from participating in a broadcaster’s chat room, or puts them in a timeout. For more information
        about banning or putting users in a timeout, see Ban a User and Timeout a User.

        If the user is currently in a timeout, you can call this endpoint to change the duration of the timeout or ban them altogether. If the user is currently banned, you cannot call this method to put them in a timeout instead.

        To remove a ban or end a timeout, see Unban user.

        # Authentication:
        Requires a User access token with scope set to `moderator:manage:banned_users`.

        # URL:
        `POST https://api.twitch.tv/helix/moderation/bans`

        # Query Parameters:
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                        |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster whose chat room the user is being banned from.                                                                           |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token. |
        |                |          |        |                                                                                                                                                    |
        |                |          |        | If the broadcaster wants to ban the user (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.                 |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+

        # Request Body:
        +----------+----------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | Field    | Required | Type    | Description                                                                                                                   |
        +----------+----------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | data     | Yes      | Object  | The user to ban or put in a timeout.                                                                                          |
        +----------+----------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | duration | No       | Integer | To ban a user indefinitely, don’t include this field.                                                                         |
        |          |          |         |                                                                                                                               |
        |          |          |         | To put a user in a timeout, include this field and specify the timeout period, in seconds.                                    |
        |          |          |         |                                                                                                                               |
        |          |          |         | The minimum timeout is 1 second and the maximum is 1,209,600 seconds (2 weeks).                                               |
        |          |          |         |                                                                                                                               |
        |          |          |         | To end a user’s timeout early, set this field to 1, or send an Unban user request.                                            |
        +----------+----------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | reason   | Yes      | String  | The reason the user is being banned or put in a timeout. The text is user defined and limited to a maximum of 500 characters. |
        +----------+----------+---------+-------------------------------------------------------------------------------------------------------------------------------+
        | user_id  | Yes      | String  | The ID of the user to ban or put in a timeout.                                                                                |
        +----------+----------+---------+-------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        +----------------+--------------+----------------------------------------------------------------------------------------------------------------------------------+
        | Field          | Type         | Description                                                                                                                      |
        +----------------+--------------+----------------------------------------------------------------------------------------------------------------------------------+
        | data           | Object array | A list that contains the user you successfully banned or put in a timeout.                                                       |
        +----------------+--------------+----------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | String       | The broadcaster whose chat room the user was banned from chatting in.                                                            |
        +----------------+--------------+----------------------------------------------------------------------------------------------------------------------------------+
        | end_time       | String       | The UTC date and time (in RFC3339 format) that the timeout will end. Is null if the user was banned instead of put in a timeout. |
        +----------------+--------------+----------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | String       | The moderator that banned or put the user in the timeout.                                                                        |
        +----------------+--------------+----------------------------------------------------------------------------------------------------------------------------------+
        | user_id        | String       | The user that was banned or was put in a timeout.                                                                                |
        +----------------+--------------+----------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                                         |
        +------+-----------------------------------------------------------------------------------------------------------------+
        | 200  | Success                                                                                                         |
        +------+-----------------------------------------------------------------------------------------------------------------+
        | 400  | Bad Request                                                                                                     |
        +------+-----------------------------------------------------------------------------------------------------------------+
        | 401  | Unauthorized                                                                                                    |
        +------+-----------------------------------------------------------------------------------------------------------------+
        | 403  | Forbidden                                                                                                       |
        +------+-----------------------------------------------------------------------------------------------------------------+
        | 429  | Too Many Requests. It is possible for too many ban requests to occur even within normal Twitch API rate limits. |
        +------+-----------------------------------------------------------------------------------------------------------------+
        | 500  | Internal Server Error                                                                                           |
        +------+-----------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        _data_ = exclude_non_empty(duration=duration, reason=reason, user_id=user_id)
        data = exclude_non_empty(data=_data_ or _empty)
        return await self._request('POST', 'moderation/bans', params=params, data=data)

    async def unban_user(self, *, broadcaster_id: str, moderator_id: str, user_id: str):
        """
        NEW Removes the ban or timeout that was placed on the specified user (see Ban user).

        # Authentication:
        Requires a User access token with scope set to `moderator:manage:banned_users`.

        # URL:
        `DELETE https://api.twitch.tv/helix/moderation/bans`

        # Query Parameters:
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                        |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster whose chat room the user is banned from chatting in.                                                                     |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token. |
        |                |          |        |                                                                                                                                                    |
        |                |          |        | If the broadcaster wants to remove the ban (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.               |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | user_id        | Yes      | String | The ID of the user to remove the ban or timeout from.                                                                                              |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        If the request succeeds, the status code is 204 No Content.

        # Response Codes:
        +------+-------------------------------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                                           |
        +------+-------------------------------------------------------------------------------------------------------------------+
        | 204  | No Content                                                                                                        |
        +------+-------------------------------------------------------------------------------------------------------------------+
        | 400  | Bad Request                                                                                                       |
        +------+-------------------------------------------------------------------------------------------------------------------+
        | 401  | Unauthorized                                                                                                      |
        +------+-------------------------------------------------------------------------------------------------------------------+
        | 403  | Forbidden                                                                                                         |
        +------+-------------------------------------------------------------------------------------------------------------------+
        | 429  | Too Many Requests. It is possible for too many unban requests to occur even within normal Twitch API rate limits. |
        +------+-------------------------------------------------------------------------------------------------------------------+
        | 500  | Internal Server Error                                                                                             |
        +------+-------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, moderator_id=moderator_id, user_id=user_id)
        return await self._request('DELETE', 'moderation/bans', params=params)

    async def get_blocked_terms(
        self, *, after: str = _empty, broadcaster_id: str, first: int = _empty, moderator_id: str
    ):
        """
        NEW Gets the broadcaster’s list of non-private, blocked words or phrases. These are the terms that the
        broadcaster or moderator added manually, or that were denied by AutoMod.

        # Authorization:
        Requires a User access token with scope set to `moderator:read:blocked_terms`.

        # URL:
        `GET https://api.twitch.tv/helix/moderation/blocked_terms`

        # Query Parameters:
        +----------------+----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type    | Description                                                                                                                                                         |
        +----------------+----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | after          | No       | String  | The cursor used to get the next page of results. The Pagination object in the response contains the cursor’s value.                                                 |
        +----------------+----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String  | The ID of the broadcaster whose blocked terms you’re getting.                                                                                                       |
        +----------------+----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | first          | No       | Integer | The maximum number of blocked terms to return per page in the response. The minimum page size is 1 blocked term per page and the maximum is 100. The default is 20. |
        +----------------+----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String  | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.                  |
        |                |          |         |                                                                                                                                                                     |
        |                |          |         | If the broadcaster wants to get their own block terms (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.                     |
        +----------------+----------+---------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field          | Type         | Description                                                                                                                                                                       |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | data           | object array | The list of blocked terms. The list is in descending order of when they were created (see the `created_at` timestamp).                                                            |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | String       | The broadcaster that owns the list of blocked terms.                                                                                                                              |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | created_at     | String       | The UTC date and time (in RFC3339 format) of when the term was blocked.                                                                                                           |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | expires_at     | String       | The UTC date and time (in RFC3339 format) of when the blocked term is set to expire. After the block expires, user’s will be able to use the term in the broadcaster’s chat room. |
        |                |              |                                                                                                                                                                                   |
        |                |              | This field is null if the term was added manually or was permanently blocked by AutoMod.                                                                                          |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | id             | String       | An ID that uniquely identifies this blocked term.                                                                                                                                 |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | String       | The moderator that blocked the word or phrase from being used in the broadcaster’s chat room.                                                                                     |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | text           | String       | The blocked word or phrase.                                                                                                                                                       |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | updated_at     | String       | The UTC date and time (in RFC3339 format) of when the term was updated.                                                                                                           |
        |                |              |                                                                                                                                                                                   |
        |                |              | When the term is added, this timestamp is the same as created_at. The timestamp changes as AutoMod continues to deny the term.                                                    |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | pagination     | object       | The information used to paginate the response data.                                                                                                                               |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | cursor         | String       | The cursor used to page results. Used to set the request’s after query parameter.                                                                                                 |
        +----------------+--------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-------------------------+
        | Code | Meaning                 |
        +------+-------------------------+
        | 200  | Success.                |
        +------+-------------------------+
        | 400  | Malformed request.      |
        +------+-------------------------+
        | 401  | Authentication failure. |
        +------+-------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first, moderator_id=moderator_id)
        return await self._request('GET', 'moderation/blocked_terms', params=params)

    async def add_blocked_term(self, *, broadcaster_id: str, moderator_id: str, text: str):
        """
        NEW Adds a word or phrase to the broadcaster’s list of blocked terms. These are the terms that broadcasters
        don’t want used in their chat room.

        # Authentication:
        Requires a User access token with scope set to `moderator:manage:blocked_terms`.

        # URL:
        `POST https://api.twitch.tv/helix/moderation/blocked_terms`

        # Query Parameters:
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                        |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster that owns the list of blocked terms.                                                                                     |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token. |
        |                |          |        |                                                                                                                                                    |
        |                |          |        | If the broadcaster wants to add the blocked term (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.         |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+

        # Request Body:
        +-------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field | Required | Type   | Description                                                                                                                                                    |
        +-------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | text  | Yes      | String | The word or phrase to block from being used in the broadcaster’s chat room.                                                                                    |
        |       |          |        |                                                                                                                                                                |
        |       |          |        | The term must contain a minimum of 2 characters and may contain up to a maximum of 500 characters.                                                             |
        |       |          |        |                                                                                                                                                                |
        |       |          |        | Terms can use a wildcard character (*). The wildcard character must appear at the beginning or end of a word, or set of characters. For example, *foo or foo*. |
        +-------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | Field          | Type         | Description                                                                                                       |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | data           | object array | The list of blocked terms. The list will contain the single blocked term that the broadcaster added.              |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | String       | The broadcaster that owns the list of blocked terms.                                                              |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | created_at     | String       | The UTC date and time (in RFC3339 format) of when the term was blocked.                                           |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | expires_at     | String       | Is set to null.                                                                                                   |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | id             | String       | An ID that uniquely identifies this blocked term.                                                                 |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | String       | The moderator that blocked the word or phrase from being used in the broadcaster’s chat room.                     |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | text           | String       | The blocked word or phrase.                                                                                       |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        | updated_at     | String       | The UTC date and time (in RFC3339 format) of when the term was updated. This timestamp is the same as created_at. |
        +----------------+--------------+-------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        data = exclude_non_empty(text=text)
        return await self._request('POST', 'moderation/blocked_terms', params=params, data=data)

    async def remove_blocked_term(self, *, broadcaster_id: str, id_: str, moderator_id: str):
        """
        NEW Removes the word or phrase that the broadcaster is blocking users from using in their chat room.

        # Authentication:
        Requires a User access token with scope set to `moderator:manage:blocked_terms`.

        # URL:
        `DELETE https://api.twitch.tv/helix/moderation/blocked_terms`

        # Query Parameters:
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                                                                                                        |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster that owns the list of blocked terms.                                                                                     |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | id             | Yes      | String | The ID of the blocked term you want to delete.                                                                                                     |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+
        | moderator_id   | Yes      | String | The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token. |
        |                |          |        |                                                                                                                                                    |
        |                |          |        | If the broadcaster wants to delete the blocked term (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.      |
        +----------------+----------+--------+----------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Body:
        If the request succeeds, the status code is 204 No Content.
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, id=id_, moderator_id=moderator_id)
        return await self._request('DELETE', 'moderation/blocked_terms', params=params)

    async def get_moderators(
        self, *, after: str = _empty, broadcaster_id: str, first: str = _empty, user_id: Union[str, List[str]] = _empty
    ):
        """
        Returns all moderators in a channel. Note: This endpoint does not return the broadcaster in the response, as
        broadcasters are channel owners and have all permissions of moderators implicitly.

        # Authorization:
        - OAuth token required

        - Required scope: `moderation:read`

        # URL:
        `GET https://api.twitch.tv/helix/moderation/moderators`

        # Pagination Support:
        Forward pagination only.

        # Required Query Parameter:
        +------------------+--------+----------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                      |
        +------------------+--------+----------------------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the auth token. Maximum: 1 |
        +------------------+--------+----------------------------------------------------------------------------------+

        # Optional Query Parameters:
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                                                                                                                                                                                                                    |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id.                                                                                                                                                                                                                 |
        |           |        |                                                                                                                                                                                                                                                                                                                                                |
        |           |        | Format: Repeated Query Parameter, eg. `/moderation/moderators?broadcaster_id=1&user_id=2&user_id=3`                                                                                                                                                                                                                                            |
        |           |        |                                                                                                                                                                                                                                                                                                                                                |
        |           |        | Maximum: 100                                                                                                                                                                                                                                                                                                                                   |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | string | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                                                                                                                                                |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +--------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | Parameter    | Type                       | Description                                                                                                 |
        +--------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `user_id`    | string                     | User ID of a moderator in the channel.                                                                      |
        +--------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `user_login` | string                     | Login of a moderator in the channel.                                                                        |
        +--------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `user_name`  | string                     | Display name of a moderator in the channel.                                                                 |
        +--------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `pagination` | object containing a string | A cursor value, to be used in subsequent requests to specify the starting point of the next set of results. |
        +--------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first, user_id=user_id)
        return await self._request('GET', 'moderation/moderators', params=params)

    async def get_moderator_events(
        self, *, after: str = _empty, broadcaster_id: str, first: str = _empty, user_id: Union[str, List[str]] = _empty
    ):
        """
        Returns a list of moderators or users added and removed as moderators from a channel.

        # Authorization:
        - OAuth token required

        - Required scope: `moderation:read`

        # URL:
        `GET https://api.twitch.tv/helix/moderation/moderators/events`

        # Pagination Support:
        Forward pagination only.

        # Required Query Parameter:
        +------------------+--------+-----------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                           |
        +------------------+--------+-----------------------------------------------------------------------+
        | `broadcaster_id` | string | Provided `broadcaster_id` must match the `user_id` in the auth token. |
        |                  |        |                                                                       |
        |                  |        | Maximum: 1                                                            |
        +------------------+--------+-----------------------------------------------------------------------+

        # Optional Query Parameter:
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                                                                                                                                                                                                                    |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | Filters the results and only returns a status object for users who have been added or removed as moderators in this channel and have a matching `user_id`.                                                                                                                                                                                     |
        |           |        |                                                                                                                                                                                                                                                                                                                                                |
        |           |        | Format: Repeated Query Parameter, e.g. `/moderation/moderators/events?broadcaster_id=1&user_id=2&user_id=3`                                                                                                                                                                                                                                    |
        |           |        |                                                                                                                                                                                                                                                                                                                                                |
        |           |        | Maximum: 100                                                                                                                                                                                                                                                                                                                                   |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | string | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                                                                                                                                                |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | Parameter           | Type                       | Description                                                                                                 |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `id`                | string                     | User ID of the moderator.                                                                                   |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `event_type`        | string                     | Displays `moderation.moderator.add` or `moderation.moderator.remove`                                        |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `event_timestamp`   | string                     | RFC3339 formatted timestamp for events.                                                                     |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `pagination`        | object containing a string | A cursor value to be used in a subsequent request to specify the starting point of the next set of results. |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `version`           | string                     | Returns the version of the endpoint.                                                                        |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`    | string                     | ID of the broadcaster adding or removing moderators.                                                        |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login` | string                     | Login of the broadcaster.                                                                                   |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`  | string                     | Name of the broadcaster.                                                                                    |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `user_id`           | string                     | ID of the user being added or removed as moderator.                                                         |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `user_login`        | string                     | Login of the user.                                                                                          |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        | `user_name`         | string                     | Name of the user.                                                                                           |
        +---------------------+----------------------------+-------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first, user_id=user_id)
        return await self._request('GET', 'moderation/moderators/events', params=params)

    async def get_polls(
        self, *, after: str = _empty, broadcaster_id: str, first: str = _empty, id_: Union[str, List[str]] = _empty
    ):
        """
        Get information about all polls or specific polls for a Twitch channel. Poll information is available for 90
        days.

        # Authorization:
        - User OAuth token

        - Required scope: `channel:read:polls`

        # URL:
        `GET https://api.twitch.tv/helix/polls`

        # Pagination Support:
        Forward pagination.

        # Required Query Parameter:
        +------------------+--------+------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                |
        +------------------+--------+------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | The broadcaster running polls. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                            |
        |                  |        | Maximum: 1                                                                                                 |
        +------------------+--------+------------------------------------------------------------------------------------------------------------+

        # Optional Query Parameter:
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                                                                                         |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`      | string | ID of a poll. Filters results to one or more specific polls. Not providing one or more IDs will return the full list of polls for the authenticated channel.                                                        |
        |           |        |                                                                                                                                                                                                                     |
        |           |        | Maximum: 100                                                                                                                                                                                                        |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | string | Maximum number of objects to return.                                                                                                                                                                                |
        |           |        |                                                                                                                                                                                                                     |
        |           |        | Maximum: 20. Default: 20.                                                                                                                                                                                           |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | Parameter                       | Type     | Description                                                                 |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `id`                            | string   | ID of the poll.                                                             |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_id`                | string   | ID of the broadcaster.                                                      |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_name`              | string   | Name of the broadcaster.                                                    |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_login`             | string   | Login of the broadcaster.                                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `title`                         | string   | Question displayed for the poll.                                            |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choices`                       | object[] | Array of the poll choices.                                                  |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.id`                     | string   | ID for the choice.                                                          |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.title`                  | string   | Text displayed for the choice.                                              |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.votes`                  | integer  | Total number of votes received for the choice across all methods of voting. |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.channel_points_votes`   | integer  | Number of votes received via Channel Points.                                |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.bits_votes`             | integer  | Number of votes received via Bits.                                          |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `bits_voting_enabled`           | boolean  | Indicates if Bits can be used for voting.                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `bits_per_vote`                 | integer  | Number of Bits required to vote once with Bits.                             |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `channel_points_voting_enabled` | boolean  | Indicates if Channel Points can be used for voting.                         |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `channel_points_per_vote`       | integer  | Number of Channel Points required to vote once with Channel Points.         |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `status`                        | string   | Poll status. Valid values are:                                              |
        |                                 |          |                                                                             |
        |                                 |          | `ACTIVE`: Poll is currently in progress.                                    |
        |                                 |          |                                                                             |
        |                                 |          | `COMPLETED`: Poll has reached its `ended_at` time.                          |
        |                                 |          |                                                                             |
        |                                 |          | `TERMINATED`: Poll has been manually terminated before its `ended_at` time. |
        |                                 |          |                                                                             |
        |                                 |          | `ARCHIVED`: Poll is no longer visible on the channel.                       |
        |                                 |          |                                                                             |
        |                                 |          | `MODERATED`: Poll is no longer visible to any user on Twitch.               |
        |                                 |          |                                                                             |
        |                                 |          | `INVALID`: Something went wrong determining the state.                      |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `duration`                      | integer  | Total duration for the poll (in seconds).                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `started_at`                    | string   | UTC timestamp for the poll’s start time.                                    |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `ended_at`                      | string   | UTC timestamp for the poll’s end time. Set to `null` if the poll is active. |
        +---------------------------------+----------+-----------------------------------------------------------------------------+

        # Response Codes:
        +------+-------------------------------------+
        | Code | Meaning                             |
        +------+-------------------------------------+
        | 200  | Poll details returned successfully. |
        +------+-------------------------------------+
        | 400  | Request was invalid.                |
        +------+-------------------------------------+
        | 401  | Authorization failed.               |
        +------+-------------------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first, id=id_)
        return await self._request('GET', 'polls', params=params)

    async def create_poll(
        self,
        *,
        bits_per_vote: int = _empty,
        bits_voting_enabled: bool = _empty,
        broadcaster_id: str,
        channel_points_per_vote: int = _empty,
        channel_points_voting_enabled: bool = _empty,
        choice_title: List[str],
        duration: int,
        title: str,
    ):
        """
        Create a poll for a specific Twitch channel.

        # Authorization:
        - User OAuth token

        - Required scope: `channel:manage:polls`

        # URL:
        `POST https://api.twitch.tv/helix/polls`

        # Required Body Parameter:
        +------------------+----------+------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type     | Description                                                                                                |
        +------------------+----------+------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string   | The broadcaster running polls. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |          |                                                                                                            |
        |                  |          | Maximum: 1                                                                                                 |
        +------------------+----------+------------------------------------------------------------------------------------------------------------+
        | `title`          | string   | Question displayed for the poll.                                                                           |
        |                  |          |                                                                                                            |
        |                  |          | Maximum: 60 characters.                                                                                    |
        +------------------+----------+------------------------------------------------------------------------------------------------------------+
        | `choices`        | object[] | Array of the poll choices.                                                                                 |
        |                  |          |                                                                                                            |
        |                  |          | Minimum: 2 choices. Maximum: 5 choices.                                                                    |
        +------------------+----------+------------------------------------------------------------------------------------------------------------+
        | `choice.title`   | string   | Text displayed for the choice.                                                                             |
        |                  |          |                                                                                                            |
        |                  |          | Maximum: 25 characters.                                                                                    |
        +------------------+----------+------------------------------------------------------------------------------------------------------------+
        | `duration`       | integer  | Total duration for the poll (in seconds).                                                                  |
        |                  |          |                                                                                                            |
        |                  |          | Minimum: 15. Maximum: 1800.                                                                                |
        +------------------+----------+------------------------------------------------------------------------------------------------------------+

        # Optional Body Parameter:
        +---------------------------------+---------+---------------------------------------------------------------------+
        | Parameter                       | Type    | Description                                                         |
        +---------------------------------+---------+---------------------------------------------------------------------+
        | `bits_voting_enabled`           | boolean | Indicates if Bits can be used for voting.                           |
        |                                 |         |                                                                     |
        |                                 |         | Default: `false`                                                    |
        +---------------------------------+---------+---------------------------------------------------------------------+
        | `bits_per_vote`                 | integer | Number of Bits required to vote once with Bits.                     |
        |                                 |         |                                                                     |
        |                                 |         | Minimum: 0. Maximum: 10000.                                         |
        +---------------------------------+---------+---------------------------------------------------------------------+
        | `channel_points_voting_enabled` | boolean | Indicates if Channel Points can be used for voting.                 |
        |                                 |         |                                                                     |
        |                                 |         | Default: `false`                                                    |
        +---------------------------------+---------+---------------------------------------------------------------------+
        | `channel_points_per_vote`       | integer | Number of Channel Points required to vote once with Channel Points. |
        |                                 |         |                                                                     |
        |                                 |         | Minimum: 0. Maximum: 1000000.                                       |
        +---------------------------------+---------+---------------------------------------------------------------------+

        # Return Values:
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | Parameter                       | Type     | Description                                                                 |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `id`                            | string   | ID of the poll.                                                             |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_id`                | string   | ID of the broadcaster.                                                      |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_name`              | string   | Name of the broadcaster.                                                    |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_login`             | string   | Login of the broadcaster.                                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `title`                         | string   | Question displayed for the poll.                                            |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choices`                       | object[] | Array of the poll choices.                                                  |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.id`                     | string   | ID for the choice.                                                          |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.title`                  | string   | Text displayed for the choice.                                              |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.votes`                  | integer  | Total number of votes received for the choice.                              |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.channel_points_votes`   | integer  | Number of votes received via Channel Points.                                |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.bits_votes`             | integer  | Number of votes received via Bits.                                          |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `bits_voting_enabled`           | boolean  | Indicates if Bits can be used for voting.                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `bits_per_vote`                 | integer  | Number of Bits required to vote once with Bits.                             |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `channel_points_voting_enabled` | boolean  | Indicates if Channel Points can be used for voting.                         |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `channel_points_per_vote`       | integer  | Number of Channel Points required to vote once with Channel Points.         |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `status`                        | string   | Poll status. Valid values are:                                              |
        |                                 |          |                                                                             |
        |                                 |          | `ACTIVE`: Poll is currently in progress.                                    |
        |                                 |          |                                                                             |
        |                                 |          | `COMPLETED`: Poll has reached its `ended_at` time.                          |
        |                                 |          |                                                                             |
        |                                 |          | `TERMINATED`: Poll has been manually terminated before its `ended_at` time. |
        |                                 |          |                                                                             |
        |                                 |          | `ARCHIVED`: Poll is no longer visible on the channel.                       |
        |                                 |          |                                                                             |
        |                                 |          | `MODERATED`: Poll is no longer visible to any user on Twitch.               |
        |                                 |          |                                                                             |
        |                                 |          | `INVALID`: Something went wrong determining the state.                      |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `duration`                      | integer  | Total duration for the poll (in seconds).                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `started_at`                    | string   | UTC timestamp for the poll’s start time.                                    |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `ended_at`                      | string   | UTC timestamp for the poll’s end time. Set to `null` if the poll is active. |
        +---------------------------------+----------+-----------------------------------------------------------------------------+

        # Response Codes:
        +------+----------------------------+
        | Code | Meaning                    |
        +------+----------------------------+
        | 200  | Poll created successfully. |
        +------+----------------------------+
        | 400  | Request was invalid.       |
        +------+----------------------------+
        | 401  | Authorization failed.      |
        +------+----------------------------+
        """
        _choices = [exclude_non_empty(title=_title_part) for _title_part in choice_title]
        data = exclude_non_empty(
            bits_per_vote=bits_per_vote,
            bits_voting_enabled=bits_voting_enabled,
            broadcaster_id=broadcaster_id,
            channel_points_per_vote=channel_points_per_vote,
            channel_points_voting_enabled=channel_points_voting_enabled,
            choices=_choices or _empty,
            duration=duration,
            title=title,
        )
        return await self._request('POST', 'polls', data=data)

    async def end_poll(self, *, broadcaster_id: str, id_: str, status: str):
        """
        End a poll that is currently active.

        # Authorization:
        - User OAuth token

        - Required scope: `channel:manage:polls`

        # URL:
        `PATCH https://api.twitch.tv/helix/polls`

        # Required Body Parameter:
        +------------------+--------+------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                |
        +------------------+--------+------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | The broadcaster running polls. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                            |
        |                  |        | Maximum: 1                                                                                                 |
        +------------------+--------+------------------------------------------------------------------------------------------------------------+
        | `id`             | string | ID of the poll.                                                                                            |
        +------------------+--------+------------------------------------------------------------------------------------------------------------+
        | `status`         | string | The poll status to be set. Valid values:                                                                   |
        |                  |        |                                                                                                            |
        |                  |        | `TERMINATED`: End the poll manually, but allow it to be viewed publicly.                                   |
        |                  |        |                                                                                                            |
        |                  |        | `ARCHIVED`: End the poll manually and do not allow it to be viewed publicly.                               |
        +------------------+--------+------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | Parameter                       | Type     | Description                                                                 |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `id`                            | string   | ID of the poll.                                                             |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_id`                | string   | ID of the broadcaster.                                                      |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_name`              | string   | Name of the broadcaster.                                                    |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `broadcaster_login`             | string   | Login of the broadcaster.                                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `title`                         | string   | Question displayed for the poll.                                            |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choices`                       | object[] | Array of the poll choices.                                                  |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.id`                     | string   | ID for the choice.                                                          |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.title`                  | string   | Text displayed for the choice.                                              |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.votes`                  | integer  | Total number of votes received for the choice.                              |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.channel_points_votes`   | integer  | Number of votes received via Channel Points.                                |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `choice.bits_votes`             | integer  | Number of votes received via Bits.                                          |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `bits_voting_enabled`           | boolean  | Indicates if Bits can be used for voting.                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `bits_per_vote`                 | integer  | Number of Bits required to vote once with Bits.                             |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `channel_points_voting_enabled` | boolean  | Indicates if Channel Points can be used for voting.                         |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `channel_points_per_vote`       | integer  | Number of Channel Points required to vote once with Channel Points.         |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `status`                        | string   | Poll Status. Valid values are:                                              |
        |                                 |          |                                                                             |
        |                                 |          | `ACTIVE`: Poll is currently in progress.                                    |
        |                                 |          |                                                                             |
        |                                 |          | `COMPLETED`: Poll has reached its `ended_at` time.                          |
        |                                 |          |                                                                             |
        |                                 |          | `TERMINATED`: Poll has been manually terminated before its `ended_at` time. |
        |                                 |          |                                                                             |
        |                                 |          | `ARCHIVED`: Poll is no longer visible on the channel.                       |
        |                                 |          |                                                                             |
        |                                 |          | `MODERATED`: Poll is no longer visible to any user on Twitch.               |
        |                                 |          |                                                                             |
        |                                 |          | `INVALID`: Something went wrong determining the state.                      |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `duration`                      | integer  | Total duration for the poll (in seconds).                                   |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `started_at`                    | string   | UTC timestamp for the poll’s start time.                                    |
        +---------------------------------+----------+-----------------------------------------------------------------------------+
        | `ended_at`                      | string   | UTC timestamp for the poll’s end time.                                      |
        +---------------------------------+----------+-----------------------------------------------------------------------------+

        # Response Codes:
        +------+--------------------------+
        | Code | Meaning                  |
        +------+--------------------------+
        | 200  | Poll ended successfully. |
        +------+--------------------------+
        | 400  | Request was invalid.     |
        +------+--------------------------+
        | 401  | Authorization failed.    |
        +------+--------------------------+
        """
        data = exclude_non_empty(broadcaster_id=broadcaster_id, id=id_, status=status)
        return await self._request('PATCH', 'polls', data=data)

    async def get_predictions(
        self, *, after: str = _empty, broadcaster_id: str, first: str = _empty, id_: Union[str, List[str]] = _empty
    ):
        """
        Get information about all Channel Points Predictions or specific Channel Points Predictions for a Twitch
        channel. Results are ordered by most recent, so it can be assumed that the currently active or locked Prediction
        will be the first item.

        # Authorization:
        - User OAuth token

        - Required scope: `channel:read:predictions`

        # URL:
        `GET https://api.twitch.tv/helix/predictions`

        # Pagination Support:
        Forward pagination.

        # Required Query Parameter:
        +------------------+--------+------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                      |
        +------------------+--------+------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | The broadcaster running Predictions. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                                  |
        |                  |        | Maximum: 1                                                                                                       |
        +------------------+--------+------------------------------------------------------------------------------------------------------------------+

        # Optional Query Parameter:
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                                                                                         |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`      | string | ID of a Prediction. Filters results to one or more specific Predictions. Not providing one or more IDs will return the full list of Predictions for the authenticated channel.                                      |
        |           |        |                                                                                                                                                                                                                     |
        |           |        | Maximum: 100                                                                                                                                                                                                        |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | string | Maximum number of objects to return.                                                                                                                                                                                |
        |           |        |                                                                                                                                                                                                                     |
        |           |        | Maximum: 20. Default: 20.                                                                                                                                                                                           |
        +-----------+--------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                                         | Type     | Description                                                                                                                              |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                                              | string   | ID of the Prediction.                                                                                                                    |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`                                  | string   | ID of the broadcaster.                                                                                                                   |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`                                | string   | Name of the broadcaster.                                                                                                                 |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`                               | string   | Login of the broadcaster.                                                                                                                |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                                           | string   | Title for the Prediction.                                                                                                                |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `winning_outcome_id`                              | string   | ID of the winning outcome. If the status is `ACTIVE`, this is set to `null`.                                                             |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcomes`                                        | object[] | Array of possible outcomes for the Prediction.                                                                                           |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.id`                                      | string   | ID for the outcome.                                                                                                                      |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.title`                                   | string   | Text displayed for outcome.                                                                                                              |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.users`                                   | integer  | Number of unique users that chose the outcome.                                                                                           |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.channel_points`                          | integer  | Number of Channel Points used for the outcome.                                                                                           |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors`                          | object[] | Array of users who were the top predictors. `null` if none.                                                                              |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.id`                  | string   | ID of the user.                                                                                                                          |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.name`                | string   | Display name of the user.                                                                                                                |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.login`               | string   | Login of the user.                                                                                                                       |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.channel_points_used` | integer  | Number of Channel Points used by the user.                                                                                               |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.channel_points_won`  | integer  | Number of Channel Points won by the user.                                                                                                |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.color`                                   | string   | Color for the outcome. Valid values: `BLUE`, `PINK`                                                                                      |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `prediction_window`                               | integer  | Total duration for the Prediction (in seconds).                                                                                          |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`                                          | string   | Status of the Prediction. Valid values are:                                                                                              |
        |                                                   |          |                                                                                                                                          |
        |                                                   |          | `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who guessed the correct outcome. |
        |                                                   |          |                                                                                                                                          |
        |                                                   |          | `ACTIVE`: The Prediction is active and viewers can make predictions.                                                                     |
        |                                                   |          |                                                                                                                                          |
        |                                                   |          | `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.                                  |
        |                                                   |          |                                                                                                                                          |
        |                                                   |          | `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.                                                     |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`                                      | string   | UTC timestamp for the Prediction’s start time.                                                                                           |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`                                        | string   | UTC timestamp for when the Prediction ended. If the status is `ACTIVE`, this is set to `null`.                                           |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+
        | `locked_at`                                       | string   | UTC timestamp for when the Prediction was locked. If the status is not `LOCKED`, this is set to `null`.                                  |
        +---------------------------------------------------+----------+------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-------------------------------------------+
        | Code | Meaning                                   |
        +------+-------------------------------------------+
        | 200  | Prediction details returned successfully. |
        +------+-------------------------------------------+
        | 400  | Request was invalid.                      |
        +------+-------------------------------------------+
        | 401  | Authorization failed.                     |
        +------+-------------------------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first, id=id_)
        return await self._request('GET', 'predictions', params=params)

    async def create_prediction(
        self, *, broadcaster_id: str, outcome_title: List[str], prediction_window: int, title: str
    ):
        """
        Create a Channel Points Prediction for a specific Twitch channel.

        # Authorization:
        - User OAuth token

        - Required scope: `channel:manage:predictions`

        # URL:
        `POST https://api.twitch.tv/helix/predictions`

        # Required Body Parameter:
        +---------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Type     | Description                                                                                                                                                                                                              |
        +---------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`    | string   | The broadcaster running Predictions. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.                                                                                                         |
        |                     |          |                                                                                                                                                                                                                          |
        |                     |          | Maximum: 1                                                                                                                                                                                                               |
        +---------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`             | string   | Title for the Prediction.                                                                                                                                                                                                |
        |                     |          |                                                                                                                                                                                                                          |
        |                     |          | Maximum: 45 characters.                                                                                                                                                                                                  |
        +---------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcomes`          | object[] | Array of outcome objects with titles for the Prediction. Array size must be 2. The first outcome object is the “blue” outcome and the second outcome object is the “pink” outcome when viewing the Prediction on Twitch. |
        +---------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.title`     | string   | Text displayed for the outcome choice.                                                                                                                                                                                   |
        |                     |          |                                                                                                                                                                                                                          |
        |                     |          | Maximum: 25 characters.                                                                                                                                                                                                  |
        +---------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `prediction_window` | integer  | Total duration for the Prediction (in seconds).                                                                                                                                                                          |
        |                     |          |                                                                                                                                                                                                                          |
        |                     |          | Minimum: 1. Maximum: 1800.                                                                                                                                                                                               |
        +---------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                                         | Type     | Description                                                                                                                                |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                                              | string   | ID of the Prediction.                                                                                                                      |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`                                  | string   | ID of the broadcaster.                                                                                                                     |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`                               | string   | Login of the broadcaster.                                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`                                | string   | Name of the broadcaster.                                                                                                                   |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                                           | string   | Title for the Prediction.                                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `winning_outcome_id`                              | string   | ID of the winning outcome.                                                                                                                 |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcomes`                                        | object[] | Array of possible outcomes for the Prediction.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.id`                                      | string   | ID for the outcome.                                                                                                                        |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.title`                                   | string   | Text displayed for outcome.                                                                                                                |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.users`                                   | integer  | Number of unique users that chose the outcome.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.channel_points`                          | integer  | Number of Channel Points used for the outcome.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.color`                                   | string   | Color for the outcome. Valid values: `BLUE`, `PINK`                                                                                        |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors`                          | object[] | Array of users who were the top predictors.                                                                                                |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.id`                  | string   | ID of the user.                                                                                                                            |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.name`                | string   | Display name of the user.                                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.login`               | string   | Login of the user.                                                                                                                         |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.channel_points_used` | integer  | Number of Channel Points used by the user.                                                                                                 |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.channel_points_won`  | integer  | Number of Channel Points won by the user.                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `prediction_window`                               | integer  | Total duration for the Prediction (in seconds).                                                                                            |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`                                          | string   | Status of the Prediction. Valid values are:                                                                                                |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who predicted the correct outcome. |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `ACTIVE`: The Prediction is active and viewers can make predictions.                                                                       |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.                                    |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.                                                       |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`                                      | string   | UTC timestamp for the Prediction’s start time.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`                                        | string   | UTC timestamp for when the Prediction ended. If the status is `ACTIVE`, this is set to `null`.                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `locked_at`                                       | string   | UTC timestamp for when the Prediction was locked. If the status is not `LOCKED`, this is set to `null`.                                    |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+----------------------------------+
        | Code | Meaning                          |
        +------+----------------------------------+
        | 200  | Prediction created successfully. |
        +------+----------------------------------+
        | 400  | Request was invalid.             |
        +------+----------------------------------+
        | 401  | Authorization failed.            |
        +------+----------------------------------+
        """
        _outcomes = [exclude_non_empty(title=_title_part) for _title_part in outcome_title]
        data = exclude_non_empty(
            broadcaster_id=broadcaster_id,
            outcomes=_outcomes or _empty,
            prediction_window=prediction_window,
            title=title,
        )
        return await self._request('POST', 'predictions', data=data)

    async def end_prediction(self, *, broadcaster_id: str, id_: str, status: str, winning_outcome_id: str = _empty):
        """
        Lock, resolve, or cancel a Channel Points Prediction. Active Predictions can be updated to be “locked,”

        “resolved,” or “canceled.” Locked Predictions can be updated to be “resolved” or “canceled.”

        # Authorization:
        - User OAuth token

        - Required scope: `channel:manage:predictions`

        # URL:
        `PATCH https://api.twitch.tv/helix/predictions`

        # Required Body Parameter:
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | The broadcaster running prediction events. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.                     |
        |                  |        |                                                                                                                                            |
        |                  |        | Maximum: 1                                                                                                                                 |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`             | string | ID of the Prediction.                                                                                                                      |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`         | string | The Prediction status to be set. Valid values:                                                                                             |
        |                  |        |                                                                                                                                            |
        |                  |        | `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who predicted the correct outcome. |
        |                  |        |                                                                                                                                            |
        |                  |        | `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.                                    |
        |                  |        |                                                                                                                                            |
        |                  |        | `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.                                                       |
        +------------------+--------+--------------------------------------------------------------------------------------------------------------------------------------------+

        # Optional Body Parameter:
        +----------------------+--------+------------------------------------------------------------------------------------------------------------------+
        | Parameter            | Type   | Description                                                                                                      |
        +----------------------+--------+------------------------------------------------------------------------------------------------------------------+
        | `winning_outcome_id` | string | ID of the winning outcome for the Prediction. This parameter is required if `status` is being set to `RESOLVED`. |
        +----------------------+--------+------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                                         | Type     | Description                                                                                                                                |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                                              | string   | ID of the prediction.                                                                                                                      |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`                                  | string   | ID of the broadcaster.                                                                                                                     |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`                               | string   | Login of the broadcaster.                                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`                                | string   | Name of the broadcaster.                                                                                                                   |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                                           | string   | Title for the prediction.                                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `winning_outcome_id`                              | string   | ID of the winning outcome.                                                                                                                 |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcomes`                                        | object[] | Array of possible outcomes for the prediction.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.id`                                      | string   | ID for the outcome.                                                                                                                        |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.title`                                   | string   | Text displayed for outcome.                                                                                                                |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.users`                                   | integer  | Number of unique users that chose the outcome.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.channel_points`                          | integer  | Number of Channel Points used for the outcome.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.color`                                   | string   | Color for the outcome. Valid values: `BLUE`, `PINK`                                                                                        |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors`                          | object[] | Array of users who were the top predictors.                                                                                                |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.id`                  | string   | ID of the user.                                                                                                                            |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.name`                | string   | Display name of the user.                                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.login`               | string   | Login of the user.                                                                                                                         |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.channel_points_used` | integer  | Number of Channel Points used by the user.                                                                                                 |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `outcome.top_predictors.user.channel_points_won`  | integer  | Number of Channel Points won by the user.                                                                                                  |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `prediction_window`                               | integer  | Total duration for the prediction (in seconds).                                                                                            |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `status`                                          | string   | Status of the prediction. Valid values are:                                                                                                |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who predicted the correct outcome. |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `ACTIVE`: The Prediction is active and viewers can make predictions.                                                                       |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.                                    |
        |                                                   |          |                                                                                                                                            |
        |                                                   |          | `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.                                                       |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`                                      | string   | UTC timestamp for the prediction’s start time.                                                                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `ended_at`                                        | string   | UTC timestamp for when the prediction ended. If the status is `ACTIVE`, this is set to `null`.                                             |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+
        | `locked_at`                                       | string   | UTC timestamp for when the prediction was locked. If the status is not `LOCKED`, this is set to `null`.                                    |
        +---------------------------------------------------+----------+--------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+--------------------------------+
        | Code | Meaning                        |
        +------+--------------------------------+
        | 200  | Prediction ended successfully. |
        +------+--------------------------------+
        | 400  | Request was invalid.           |
        +------+--------------------------------+
        | 401  | Authorization failed.          |
        +------+--------------------------------+
        """
        data = exclude_non_empty(
            broadcaster_id=broadcaster_id, id=id_, status=status, winning_outcome_id=winning_outcome_id
        )
        return await self._request('PATCH', 'predictions', data=data)

    async def get_channel_stream_schedule(
        self,
        *,
        after: str = _empty,
        broadcaster_id: str,
        first: int = _empty,
        id_: Union[str, List[str]] = _empty,
        start_time: str = _empty,
        utc_offset: str = _empty,
    ):
        """
        NEW Gets all scheduled broadcasts or specific scheduled broadcasts from a channel’s stream schedule. Scheduled
        broadcasts are defined as “stream segments” in the API.

        # Authorization:
        - User OAuth Token or App Access Token

        # URL:
        `GET https://api.twitch.tv/helix/schedule`

        # Pagination Support:
        Forward pagination.

        # Required Query Parameters:
        +------------------+--------+---------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                         |
        +------------------+--------+---------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster who owns the channel streaming schedule. |
        |                  |        |                                                                     |
        |                  |        | Maximum: 1                                                          |
        +------------------+--------+---------------------------------------------------------------------+

        # Optional Query Parameters:
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter    | Type    | Description                                                                                                                                                                                                                                         |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`         | string  | The ID of the stream segment to return.                                                                                                                                                                                                             |
        |              |         |                                                                                                                                                                                                                                                     |
        |              |         | Maximum: 100.                                                                                                                                                                                                                                       |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `start_time` | string  | A timestamp in RFC3339 format to start returning stream segments from. If not specified, the current date and time is used.                                                                                                                         |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `utc_offset` | string  | A timezone offset for the requester specified in minutes. This is recommended to ensure stream segments are returned for the correct week. For example, a timezone that is +4 hours from GMT would be “240.” If not specified, “0” is used for GMT. |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`      | integer | Maximum number of stream segments to return.                                                                                                                                                                                                        |
        |              |         |                                                                                                                                                                                                                                                     |
        |              |         | Maximum: 25. Default: 20.                                                                                                                                                                                                                           |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`      | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.                                 |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                | Type             | Description                                                                                                                                                                                                 |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segments`               | array of objects | Scheduled broadcasts for this stream schedule.                                                                                                                                                              |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.id`             | string           | The ID for the scheduled broadcast.                                                                                                                                                                         |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.start_time`     | string           | Scheduled start time for the scheduled broadcast in RFC3339 format.                                                                                                                                         |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.end_time`       | string           | Scheduled end time for the scheduled broadcast in RFC3339 format.                                                                                                                                           |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.title`          | string           | Title for the scheduled broadcast.                                                                                                                                                                          |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.canceled_until` | string           | Used with recurring scheduled broadcasts. Specifies the date of the next recurring broadcast in RFC3339 format if one or more specific broadcasts have been deleted in the series. Set to `null` otherwise. |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category`       | object           | The category for the scheduled broadcast. Set to `null` if no category has been specified.                                                                                                                  |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category.id`    | string           | Game/category ID.                                                                                                                                                                                           |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category.name`  | string           | Game/category name.                                                                                                                                                                                         |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_recurring`           | boolean          | Indicates if the scheduled broadcast is recurring weekly.                                                                                                                                                   |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`         | string           | User ID of the broadcaster.                                                                                                                                                                                 |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`       | string           | Display name of the broadcaster.                                                                                                                                                                            |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`      | string           | Login of the broadcaster.                                                                                                                                                                                   |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation`               | object           | If Vacation Mode is enabled, this includes start and end dates for the vacation. If Vacation Mode is disabled, value is set to `null`.                                                                      |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation.start_time`    | string           | Start time for vacation specified in RFC3339 format.                                                                                                                                                        |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation.end_time`      | string           | End time for vacation specified in RFC3339 format.                                                                                                                                                          |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------+
        | Code | Meaning                                       |
        +------+-----------------------------------------------+
        | 200  | Stream schedule events returned successfully. |
        +------+-----------------------------------------------+
        | 400  | Request was invalid.                          |
        +------+-----------------------------------------------+
        | 401  | Authorization failed.                         |
        +------+-----------------------------------------------+
        """
        params = exclude_non_empty(
            after=after,
            broadcaster_id=broadcaster_id,
            first=first,
            id=id_,
            start_time=start_time,
            utc_offset=utc_offset,
        )
        return await self._request('GET', 'schedule', params=params)

    async def get_channel_icalendar(self, *, broadcaster_id: str):
        """
        NEW Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar.

        # Authorization:
        - None. OAuth token and Client ID not required.

        # URL:
        `GET https://api.twitch.tv/helix/schedule/icalendar`

        # Pagination Support:
        None.

        # Required Query Parameters:
        +------------------+--------+---------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                         |
        +------------------+--------+---------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster who owns the channel streaming schedule. |
        |                  |        |                                                                     |
        |                  |        | Maximum: 1                                                          |
        +------------------+--------+---------------------------------------------------------------------+

        # Return Values:
        iCalendar data is returned according to RFC5545. The expected MIME type is `text/calendar`.

        # Response Codes:
        +------+---------------------------------------+
        | Code | Meaning                               |
        +------+---------------------------------------+
        | 200  | iCalendar data returned successfully. |
        +------+---------------------------------------+
        | 400  | Request was invalid.                  |
        +------+---------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'schedule/icalendar', params=params)

    async def update_channel_stream_schedule(
        self,
        *,
        broadcaster_id: str,
        is_vacation_enabled: bool = _empty,
        timezone: str = _empty,
        vacation_end_time: str = _empty,
        vacation_start_time: str = _empty,
    ):
        """
        NEW Update the settings for a channel’s stream schedule. This can be used for setting vacation details.

        # Authorization:
        - User OAuth Token

        - Required scope: `channel:manage:schedule`

        # URL:
        `PATCH https://api.twitch.tv/helix/schedule/settings`

        # Pagination Support:
        None.

        # Required Query Parameters:
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                     |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                                                                 |
        |                  |        | Maximum: 1                                                                                                                                      |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+

        # Optional Query Parameters:
        +-----------------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter             | Type    | Description                                                                                                                                         |
        +-----------------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_vacation_enabled` | boolean | Indicates if Vacation Mode is enabled. Set to `true` to add a vacation or `false` to remove vacation from the channel streaming schedule.           |
        +-----------------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation_start_time` | string  | Start time for vacation specified in RFC3339 format. Required if `is_vacation_enabled` is set to `true`.                                            |
        +-----------------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation_end_time`   | string  | End time for vacation specified in RFC3339 format. Required if `is_vacation_enabled` is set to `true`.                                              |
        +-----------------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        | `timezone`            | string  | The timezone for when the vacation is being scheduled using the IANA time zone database format. Required if `is_vacation_enabled` is set to `true`. |
        +-----------------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------------+
        | Code | Meaning                                        |
        +------+------------------------------------------------+
        | 200  | Stream schedule settings updated successfully. |
        +------+------------------------------------------------+
        | 400  | Request was invalid.                           |
        +------+------------------------------------------------+
        | 401  | Authorization failed.                          |
        +------+------------------------------------------------+
        """
        params = exclude_non_empty(
            broadcaster_id=broadcaster_id,
            is_vacation_enabled=is_vacation_enabled,
            timezone=timezone,
            vacation_end_time=vacation_end_time,
            vacation_start_time=vacation_start_time,
        )
        return await self._request('PATCH', 'schedule/settings', params=params)

    async def create_channel_stream_schedule_segment(
        self,
        *,
        broadcaster_id: str,
        category_id: str = _empty,
        duration: str = _empty,
        is_recurring: bool,
        start_time: str,
        timezone: str,
        title: str = _empty,
    ):
        """
        NEW Create a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule.

        # Authorization:
        - User OAuth Token

        - Required scope: `channel:manage:schedule`

        # URL:
        `POST https://api.twitch.tv/helix/schedule/segment`

        # Pagination Support:
        Forward pagination.

        # Required Query Parameters:
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                     |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                                                                 |
        |                  |        | Maximum: 1                                                                                                                                      |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+

        # Required Body Parameters:
        +----------------+---------+------------------------------------------------------------------------------------------------------------+
        | Parameter      | Type    | Description                                                                                                |
        +----------------+---------+------------------------------------------------------------------------------------------------------------+
        | `start_time`   | string  | Start time for the scheduled broadcast specified in RFC3339 format.                                        |
        +----------------+---------+------------------------------------------------------------------------------------------------------------+
        | `timezone`     | string  | The timezone of the application creating the scheduled broadcast using the IANA time zone database format. |
        +----------------+---------+------------------------------------------------------------------------------------------------------------+
        | `is_recurring` | boolean | Indicates if the scheduled broadcast is recurring weekly.                                                  |
        +----------------+---------+------------------------------------------------------------------------------------------------------------+

        # Optional Body Parameters:
        +---------------+--------+-----------------------------------------------------------------------+
        | Parameter     | Type   | Description                                                           |
        +---------------+--------+-----------------------------------------------------------------------+
        | `duration`    | string | Duration of the scheduled broadcast in minutes from the `start_time`. |
        |               |        |                                                                       |
        |               |        | Default: 240.                                                         |
        +---------------+--------+-----------------------------------------------------------------------+
        | `category_id` | string | Game/Category ID for the scheduled broadcast.                         |
        +---------------+--------+-----------------------------------------------------------------------+
        | `title`       | string | Title for the scheduled broadcast.                                    |
        |               |        |                                                                       |
        |               |        | Maximum: 140 characters.                                              |
        +---------------+--------+-----------------------------------------------------------------------+

        # Return Values:
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                | Type             | Description                                                                                                                                                                                                 |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segments`               | array of objects | Scheduled broadcasts for this stream schedule.                                                                                                                                                              |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.id`             | string           | The ID for the scheduled broadcast.                                                                                                                                                                         |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.start_time`     | string           | Scheduled start time for the scheduled broadcast in RFC3339 format.                                                                                                                                         |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.end_time`       | string           | Scheduled end time for the scheduled broadcast in RFC3339 format.                                                                                                                                           |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.title`          | string           | Title for the scheduled broadcast.                                                                                                                                                                          |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.canceled_until` | string           | Used with recurring scheduled broadcasts. Specifies the date of the next recurring broadcast in RFC3339 format if one or more specific broadcasts have been deleted in the series. Set to `null` otherwise. |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category`       | object           | The category for the scheduled broadcast. Set to `null` if no category has been specified.                                                                                                                  |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category.id`    | string           | Game/category ID.                                                                                                                                                                                           |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category.name`  | string           | Game/category name.                                                                                                                                                                                         |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_recurring`           | boolean          | Indicates if the scheduled broadcast is recurring weekly.                                                                                                                                                   |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`         | string           | User ID of the broadcaster.                                                                                                                                                                                 |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`       | string           | Display name of the broadcaster.                                                                                                                                                                            |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`      | string           | Login of the broadcaster.                                                                                                                                                                                   |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation`               | object           | If Vacation Mode is enabled, this includes start and end dates for the vacation. If Vacation Mode is disabled, value is set to `null`.                                                                      |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation.start_time`    | string           | Start time for vacation specified in RFC3339 format.                                                                                                                                                        |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation.end_time`      | string           | End time for vacation specified in RFC3339 format.                                                                                                                                                          |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------+
        | Code | Meaning                                       |
        +------+-----------------------------------------------+
        | 200  | Stream schedule segment created successfully. |
        +------+-----------------------------------------------+
        | 400  | Request was invalid.                          |
        +------+-----------------------------------------------+
        | 401  | Authorization failed.                         |
        +------+-----------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        data = exclude_non_empty(
            category_id=category_id,
            duration=duration,
            is_recurring=is_recurring,
            start_time=start_time,
            timezone=timezone,
            title=title,
        )
        return await self._request('POST', 'schedule/segment', params=params, data=data)

    async def update_channel_stream_schedule_segment(
        self,
        *,
        broadcaster_id: str,
        id_: str,
        category_id: str = _empty,
        duration: str = _empty,
        is_canceled: bool = _empty,
        start_time: str = _empty,
        timezone: str = _empty,
        title: str = _empty,
    ):
        """
        NEW Update a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule.

        # Authorization:
        - User OAuth Token

        - Required scope: `channel:manage:schedule`

        # URL:
        `PATCH https://api.twitch.tv/helix/schedule/segment`

        # Pagination Support:
        None.

        # Required Query Parameters:
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                     |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                                                                 |
        |                  |        | Maximum: 1                                                                                                                                      |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`             | string | The ID of the streaming segment to update.                                                                                                      |
        |                  |        |                                                                                                                                                 |
        |                  |        | Maximum: 1                                                                                                                                      |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+

        # Optional Body Parameters:
        +---------------+---------+------------------------------------------------------------------------------------------------------------+
        | Parameter     | Type    | Description                                                                                                |
        +---------------+---------+------------------------------------------------------------------------------------------------------------+
        | `start_time`  | string  | Start time for the scheduled broadcast specified in RFC3339 format.                                        |
        +---------------+---------+------------------------------------------------------------------------------------------------------------+
        | `duration`    | string  | Duration of the scheduled broadcast in minutes from the `start_time`.                                      |
        |               |         |                                                                                                            |
        |               |         | Default: 240.                                                                                              |
        +---------------+---------+------------------------------------------------------------------------------------------------------------+
        | `category_id` | string  | Game/Category ID for the scheduled broadcast.                                                              |
        +---------------+---------+------------------------------------------------------------------------------------------------------------+
        | `title`       | string  | Title for the scheduled broadcast.                                                                         |
        |               |         |                                                                                                            |
        |               |         | Maximum: 140 characters.                                                                                   |
        +---------------+---------+------------------------------------------------------------------------------------------------------------+
        | `is_canceled` | boolean | Indicated if the scheduled broadcast is canceled.                                                          |
        +---------------+---------+------------------------------------------------------------------------------------------------------------+
        | `timezone`    | string  | The timezone of the application creating the scheduled broadcast using the IANA time zone database format. |
        +---------------+---------+------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter                | Type             | Description                                                                                                                                                                                     |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segments`               | array of objects | Scheduled events for this stream schedule.                                                                                                                                                      |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.id`             | string           | The ID for the scheduled event.                                                                                                                                                                 |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.start_time`     | string           | Scheduled start time for the scheduled event in RFC3339 format.                                                                                                                                 |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.end_time`       | string           | Scheduled end time for the scheduled event in RFC3339 format.                                                                                                                                   |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.title`          | string           | Title for the scheduled event.                                                                                                                                                                  |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.canceled_until` | string           | Used with recurring scheduled events. Specifies the date of the next recurring event in RFC3339 format if one or more specific events have been deleted in the series. Set to `null` otherwise. |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category`       | object           | The category for the scheduled broadcast. Set to `null` if no category has been specified.                                                                                                      |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category.id`    | string           | Game/category ID.                                                                                                                                                                               |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.category.name`  | string           | Game/category name.                                                                                                                                                                             |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `segment.is_recurring`   | boolean          | Indicates if the scheduled event is recurring.                                                                                                                                                  |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`         | string           | User ID of the broadcaster.                                                                                                                                                                     |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`       | string           | Display name of the broadcaster.                                                                                                                                                                |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`      | string           | Login of the broadcaster.                                                                                                                                                                       |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation`               | object           | If Vacation Mode is enabled, this includes start and end dates for the vacation. If Vacation Mode is disabled, value is set to `null`.                                                          |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation.start_time`    | string           | Start time for vacation specified in RFC3339 format.                                                                                                                                            |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `vacation.end_time`      | string           | End time for vacation specified in RFC3339 format.                                                                                                                                              |
        +--------------------------+------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------+
        | Code | Meaning                                       |
        +------+-----------------------------------------------+
        | 200  | Stream schedule segment updated successfully. |
        +------+-----------------------------------------------+
        | 400  | Request was invalid.                          |
        +------+-----------------------------------------------+
        | 401  | Authorization failed.                         |
        +------+-----------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, id=id_)
        data = exclude_non_empty(
            category_id=category_id,
            duration=duration,
            is_canceled=is_canceled,
            start_time=start_time,
            timezone=timezone,
            title=title,
        )
        return await self._request('PATCH', 'schedule/segment', params=params, data=data)

    async def delete_channel_stream_schedule_segment(self, *, broadcaster_id: str, id_: str):
        """
        NEW Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule.

        # Authorization:
        - User OAuth Token

        - Required scope: `channel:manage:schedule`

        # URL:
        `DELETE https://api.twitch.tv/helix/schedule/segment`

        # Pagination Support:
        None.

        # Required Query Parameters:
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                                                                                     |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token. |
        |                  |        |                                                                                                                                                 |
        |                  |        | Maximum: 1                                                                                                                                      |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`             | string | The ID of the streaming segment to delete.                                                                                                      |
        +------------------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------------+
        | Code | Meaning                                       |
        +------+-----------------------------------------------+
        | 204  | Stream schedule segment deleted successfully. |
        +------+-----------------------------------------------+
        | 400  | Request was invalid.                          |
        +------+-----------------------------------------------+
        | 401  | Authorization failed.                         |
        +------+-----------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, id=id_)
        return await self._request('DELETE', 'schedule/segment', params=params)

    async def search_categories(self, *, after: str = _empty, first: int = _empty, query: str):
        """
        Returns a list of games or categories that match the query via name either entirely or partially.

        # Authentication:
        OAuth or App Access Token required

        # URL:
        `GET https://api.twitch.tv/helix/search/categories`

        # Pagination Support:
        Forward pagination only.

        # Required Query Parameters:
        +-----------+--------+--------------------------+
        | Parameter | Type   | Description              |
        +-----------+--------+--------------------------+
        | `query`   | string | URl encoded search query |
        +-----------+--------+--------------------------+

        # Optional Query Parameters:
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type    | Description                                                                                                                                                                                                          |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | integer | Maximum number of objects to return.                                                                                                                                                                                 |
        |           |         | Maximum: 100.                                                                                                                                                                                                        |
        |           |         | Default: 20.                                                                                                                                                                                                         |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------+--------+--------------------------------------+
        | Parameter     | Type   | Description                          |
        +---------------+--------+--------------------------------------+
        | `box_art_url` | string | Template URL for the game’s box art. |
        +---------------+--------+--------------------------------------+
        | `name`        | string | Game/category name.                  |
        +---------------+--------+--------------------------------------+
        | `id`          | string | Game/category ID.                    |
        +---------------+--------+--------------------------------------+

        Note: The return values are the same as returned from `GET https://api.twitch.tv/helix/games`
        """
        params = exclude_non_empty(after=after, first=first, query=query)
        return await self._request('GET', 'search/categories', params=params)

    async def search_channels(self, *, after: str = _empty, first: int = _empty, live_only: bool = _empty, query: str):
        """
        Returns a list of channels (users who have streamed within the past 6 months) that match the query via channel
        name or description either entirely or partially. Results include both live and offline channels. Online
        channels will have additional metadata (e.g. `started_at`, `tag_ids`).

        # Authentication:
        OAuth or App Access Token required

        # Pagination Support:
        Forward only.

        # URL:
        `GET helix/search/channels`

        # Required Query Parameters:
        +-----------+--------+--------------------------+
        | Parameter | Type   | Description              |
        +-----------+--------+--------------------------+
        | `query`   | string | URl encoded search query |
        +-----------+--------+--------------------------+

        # Optional Query Parameters:
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter   | Type    | Description                                                                                                                                                                                                          |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`     | integer | Maximum number of objects to return.                                                                                                                                                                                 |
        |             |         | Maximum: 100                                                                                                                                                                                                         |
        |             |         | Default: 20                                                                                                                                                                                                          |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`     | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `live_only` | Boolean | Filter results for live streams only.                                                                                                                                                                                |
        |             |         | Default: false                                                                                                                                                                                                       |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter              | Type     | Description                                                                                                                                                             |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_language` | string   | Channel language                                                                                                                                                        |
        |                        |          | (Broadcaster Language field from the Channels service). A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.            |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login`    | string   | Login of the broadcaster.                                                                                                                                               |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `display_name`         | string   | Display name of the broadcaster.                                                                                                                                        |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`              | string   | ID of the game being played on the stream.                                                                                                                              |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_name`            | string   | Name of the game being played on the stream.                                                                                                                            |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`                   | string   | Channel ID.                                                                                                                                                             |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_live`              | Boolean  | Indicates if the channel is currently live.                                                                                                                              |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tag_ids`              | string[] | Tag IDs that apply to the stream. This array only contains strings when a channel is live. For all possibilities, see List of All Tags. Category Tags are not returned. |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `thumbnail_url`        | string   | Thumbnail URL of the stream. All image URLs have variable width and height. You can replace {width} and {height} with any values to get that size image.                |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`                | string   | Stream title.                                                                                                                                                           |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at`           | string   | UTC timestamp. Returns an empty string if the channel is not live.                                                                                                      |
        +------------------------+----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, first=first, live_only=live_only, query=query)
        return await self._request('GET', 'search/channels', params=params)

    async def get_soundtrack_current_track(self, *, broadcaster_id: str):
        """
        BETA Gets the Soundtrack track that the broadcaster is playing.

        # Authorization:
        Requires an App access token or User access token.

        # URL:
        `GET https://api.twitch.tv/helix/soundtrack/current_track`

        # Query Parameters:
        +----------------+----------+--------+--------------------------------------------------------------+
        | Parameter      | Required | Type   | Description                                                  |
        +----------------+----------+--------+--------------------------------------------------------------+
        | broadcaster_id | Yes      | String | The ID of the broadcaster that’s playing a Soundtrack track. |
        +----------------+----------+--------+--------------------------------------------------------------+

        # Response Body:
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | Field              | Type                     | Description                                                                                          |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | data               | SoundtrackCurrentTrack[] | A list that contains the Soundtrack track that the broadcaster is playing.                           |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | track              | SoundtrackTrack          | The track that’s currently playing.                                                                  |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | album              | SoundtrackAlbum          | The album that includes the track.                                                                   |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                   | The album’s ASIN (Amazon Standard Identification Number).                                            |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | image_url          | String                   | A URL to the album’s cover art.                                                                      |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | name               | String                   | The album’s name.                                                                                    |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | artist             | SoundtrackArtist         | The artists included on the track.                                                                   |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | creator_channel_id | String                   | The ID of the Twitch user that created the track. Is empty if a Twitch user didn’t create the track. |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                   | The artist’s ASIN (Amazon Standard Identification Number).                                           |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | name               | String                   | The artist’s name. This can be the band’s name or the solo artist’s name.                            |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | duration           | Integer                  | The duration of the track, in seconds.                                                               |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                   | The track’s ASIN (Amazon Standard Identification Number).                                            |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | title              | String                   | The track’s title.                                                                                   |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | source             | SoundtrackSource         | The source of the track that’s currently playing. For example, a playlist or station.                |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | content_type       | String                   | The type of content that `id` maps to. Possible values are:                                          |
        |                    |                          | - PLAYLIST                                                                                           |
        |                    |                          | - STATION                                                                                            |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                   | The playlist’s or station’s ASIN (Amazon Standard Identification Number).                            |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | image_url          | String                   | A URL to the playlist’s or station’s image art.                                                      |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | soundtrack_url     | String                   | A URL to the playlist on Soundtrack. The string is empty if `content-type` is STATION.               |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | spotify_url        | String                   | A URL to the playlist on Spotify. The string is empty if `content-type` is STATION.                  |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+
        | title              | String                   | The playlist’s or station’s title.                                                                   |
        +--------------------+--------------------------+------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------+
        | Code | Meaning                                 |
        +------+-----------------------------------------+
        | 200  | Success                                 |
        +------+-----------------------------------------+
        | 400  | Malformed request                       |
        +------+-----------------------------------------+
        | 401  | Unauthorized                            |
        +------+-----------------------------------------+
        | 404  | The broadcaster is not playing a track. |
        +------+-----------------------------------------+
        | 500  | Internal server error                   |
        +------+-----------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'soundtrack/current_track', params=params)

    async def get_soundtrack_playlist(self, *, id_: str):
        """
        BETA Gets a Soundtrack playlist, which includes its list of tracks.

        # Authorization:
        Requires an App access token or User access token.

        # URL:
        `GET https://api.twitch.tv/helix/soundtrack/playlist`

        # Query Parameters:
        +-----------+----------+--------+-------------------------------------------+
        | Parameter | Required | Type   | Description                               |
        +-----------+----------+--------+-------------------------------------------+
        | id        | Yes      | String | The ID of the Soundtrack playlist to get. |
        +-----------+----------+--------+-------------------------------------------+

        # Response Body:
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | Field              | Type                       | Description                                                                                          |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | data               | SoundtrackPlaylistTracks[] | A list that contains the single playlist you requested.                                              |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | description        | String                     | A short description about the music that the playlist includes.                                      |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                     | The playlist’s ASIN (Amazon Standard Identification Number).                                         |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | image_url          | String                     | A URL to the playlist’s image art. Is empty if the playlist doesn't include art.                     |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | title              | String                     | The playlist’s title.                                                                                |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | tracks             | SoundtrackTrack[]          | The list of tracks in the playlist.                                                                  |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | album              | SoundtrackAlbum            | The album that includes the track.                                                                   |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                     | The album’s ASIN (Amazon Standard Identification Number).                                            |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | image_url          | String                     | A URL to the album’s cover art.                                                                      |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | name               | String                     | The album’s name.                                                                                    |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | artist             | SoundtrackArtist           | The artists included on the track.                                                                   |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | creator_channel_id | String                     | The ID of the Twitch user that created the track. Is empty if a Twitch user didn’t create the track. |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                     | The artist’s ASIN (Amazon Standard Identification Number).                                           |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | name               | String                     | The artist’s name. This can be the band’s name or the solo artist’s name.                            |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | duration           | Integer                    | The duration of the track, in seconds.                                                               |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | id                 | String                     | The track’s ASIN (Amazon Standard Identification Number).                                            |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+
        | title              | String                     | The track’s title.                                                                                   |
        +--------------------+----------------------------+------------------------------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------+
        | Code | Meaning               |
        +------+-----------------------+
        | 200  | Success               |
        +------+-----------------------+
        | 400  | Malformed request     |
        +------+-----------------------+
        | 401  | Unauthorized          |
        +------+-----------------------+
        | 404  | Not found             |
        +------+-----------------------+
        | 500  | Internal server error |
        +------+-----------------------+
        """
        params = exclude_non_empty(id=id_)
        return await self._request('GET', 'soundtrack/playlist', params=params)

    async def get_soundtrack_playlists(self):
        """
        BETA Gets a list of Soundtrack playlists.

        The list contains information about the playlists, such as their titles and descriptions. To get a playlist’s tracks, call Get Soundtrack Playlist, and specify the playlist’s `id`.

        # Authorization:
        Requires an App access token or User access token.

        # URL:
        `GET https://api.twitch.tv/helix/soundtrack/playlists`

        # Query Parameters:
        None

        # Response Body:
        +-------------+------------------------------+----------------------------------------------------------------------------------+
        | Field       | Type                         | Description                                                                      |
        +-------------+------------------------------+----------------------------------------------------------------------------------+
        | data        | SoundtrackPlaylistMetadata[] | The list of Soundtrack playlists.                                                |
        +-------------+------------------------------+----------------------------------------------------------------------------------+
        | description | String                       | A short description about the music that the playlist includes.                  |
        +-------------+------------------------------+----------------------------------------------------------------------------------+
        | id          | String                       | The playlist’s ASIN (Amazon Standard Identification Number).                     |
        +-------------+------------------------------+----------------------------------------------------------------------------------+
        | image_url   | String                       | A URL to the playlist’s image art. Is empty if the playlist doesn't include art. |
        +-------------+------------------------------+----------------------------------------------------------------------------------+
        | title       | String                       | The playlist’s title.                                                            |
        +-------------+------------------------------+----------------------------------------------------------------------------------+

        # Response Codes:
        +------+-----------------------+
        | Code | Meaning               |
        +------+-----------------------+
        | 200  | Success               |
        +------+-----------------------+
        | 401  | Unauthorized          |
        +------+-----------------------+
        | 404  | Not found             |
        +------+-----------------------+
        | 500  | Internal server error |
        +------+-----------------------+
        """
        return await self._request('GET', 'soundtrack/playlists')

    async def get_stream_key(self, *, broadcaster_id: str):
        """
        Gets the channel stream key for a user.

        # Authentication:
        -
            User OAuth token


        -
            Required scope: `channel:read:stream_key`

        # URL:
        `https://api.twitch.tv/helix/streams/key`

        # Query Parameters:
        +------------------+----------+--------+----------------------------+
        | Parameter        | Required | Type   | Description                |
        +------------------+----------+--------+----------------------------+
        | `broadcaster_id` | yes      | string | User ID of the broadcaster |
        +------------------+----------+--------+----------------------------+

        # Response Body:
        +--------------+--------+----------------------------+
        | Parameter    | Type   | Description                |
        +--------------+--------+----------------------------+
        | `stream_key` | string | Stream key for the channel |
        +--------------+--------+----------------------------+

        # Possible Response Codes:
        +-----------+----------------------------------------------------------+
        | HTTP Code | Meaning                                                  |
        +-----------+----------------------------------------------------------+
        | 200       | Channel/Stream information returned successfully         |
        +-----------+----------------------------------------------------------+
        | 401       | Authentication failure                                   |
        +-----------+----------------------------------------------------------+
        | 500       | Internal Server Error, Failed to get channel information |
        +-----------+----------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'streams/key', params=params)

    async def get_streams(
        self,
        *,
        after: str = _empty,
        before: str = _empty,
        first: int = _empty,
        game_id: str = _empty,
        language: str = _empty,
        user_id: str = _empty,
        user_login: str = _empty,
    ):
        """
        Gets information about active streams. Streams are returned sorted by number of current viewers, in descending
        order. Across multiple pages of results, there may be duplicate or missing streams, as viewers join and leave
        streams.

        The response has a JSON payload with a `data` field containing an array of stream information elements and a `pagination` field containing information required to query for more streams.

        # Authentication:
        OAuth or App Access Token required

        # URL:
        `GET https://api.twitch.tv/helix/streams`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name         | Type    | Description                                                                                                                                                                                                           |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`      | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.  |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `before`     | string  | Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`      | integer | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                       |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`    | string  | Returns streams broadcasting a specified game ID. You can specify up to 100 IDs.                                                                                                                                      |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `language`   | string  | Stream language. You can specify up to 100 languages. A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”.                                                       |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`    | string  | Returns streams broadcast by one or more specified user IDs. You can specify up to 100 IDs.                                                                                                                           |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login` | string  | Returns streams broadcast by one or more specified user login names. You can specify up to 100 names.                                                                                                                 |
        +--------------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field           | Type                       | Description                                                                                                                                                 |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`            | string                     | Stream ID.                                                                                                                                                  |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`       | string                     | ID of the user who is streaming.                                                                                                                            |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login`    | string                     | Login of the user who is streaming.                                                                                                                         |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`     | string                     | Display name corresponding to `user_id`.                                                                                                                    |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`       | string                     | ID of the game being played on the stream.                                                                                                                  |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_name`     | string                     | Name of the game being played.                                                                                                                              |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`          | string                     | Stream type: `"live"` or `""` (in case of error).                                                                                                           |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`         | string                     | Stream title.                                                                                                                                               |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `viewer_count`  | int                        | Number of viewers watching the stream at the time of the query.                                                                                             |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at`    | string                     | UTC timestamp.                                                                                                                                              |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `language`      | string                     | Stream language. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.                                       |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `thumbnail_url` | string                     | Thumbnail URL of the stream. All image URLs have variable width and height. You can replace `{width}` and `{height}` with any values to get that size image |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tag_ids`       | string                     | Shows tag IDs that apply to the stream.                                                                                                                     |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_mature`     | boolean                    | Indicates if the broadcaster has specified their channel contains mature content that may be inappropriate for younger audiences.                           |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`    | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results.                                                |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after,
            before=before,
            first=first,
            game_id=game_id,
            language=language,
            user_id=user_id,
            user_login=user_login,
        )
        return await self._request('GET', 'streams', params=params)

    async def get_followed_streams(self, *, after: str = _empty, first: int = _empty, user_id: str):
        """
        Gets information about active streams belonging to channels that the authenticated user follows. Streams are
        returned sorted by number of current viewers, in descending order. Across multiple pages of results, there may
        be duplicate or missing streams, as viewers join and leave streams.

        # Authentication:
        - OAuth user token required

        - Required scope: `user:read:follows`

        # URL:
        `GET https://api.twitch.tv/helix/streams/followed`

        # Required Query Parameters:
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name      | Type   | Description                                                                                                                                     |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | Results will only include active streams from the channels that this Twitch user follows. `user_id` must match the User ID in the bearer token. |
        +-----------+--------+-------------------------------------------------------------------------------------------------------------------------------------------------+

        # Optional Query Parameters:
        +---------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name    | Type    | Description                                                                                                                                                                                                          |
        +---------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after` | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +---------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first` | integer | Maximum number of objects to return. Maximum: 100. Default: 100.                                                                                                                                                     |
        +---------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field           | Type                       | Description                                                                                                                                                 |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_id`       | string                     | ID of the game being played on the stream.                                                                                                                  |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `game_name`     | string                     | Name of the game being played.                                                                                                                              |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`            | string                     | Stream ID.                                                                                                                                                  |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `language`      | string                     | Stream language. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.                                       |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`    | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results.                                                |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `started_at`    | string                     | UTC timestamp.                                                                                                                                              |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tag_ids`       | string                     | Shows tag IDs that apply to the stream.                                                                                                                     |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `thumbnail_url` | string                     | Thumbnail URL of the stream. All image URLs have variable width and height. You can replace `{width}` and `{height}` with any values to get that size image |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `title`         | string                     | Stream title.                                                                                                                                               |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`          | string                     | Stream type: `"live"` or `""` (in case of error).                                                                                                           |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`       | string                     | ID of the user who is streaming.                                                                                                                            |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login`    | string                     | Login of the user who is streaming.                                                                                                                         |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`     | string                     | Display name corresponding to `user_id`.                                                                                                                    |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `viewer_count`  | int                        | Number of viewers watching the stream at the time of the query.                                                                                             |
        +-----------------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, first=first, user_id=user_id)
        return await self._request('GET', 'streams/followed', params=params)

    async def create_stream_marker(self, *, description: str = _empty, user_id: str):
        """
        Creates a marker in the stream of a user specified by user ID. A marker is an arbitrary point in a stream that
        the broadcaster wants to mark; e.g., to easily return to later. The marker is created at the current timestamp
        in the live broadcast when the request is processed. Markers can be created by the stream owner or editors. The
        user creating the marker is identified by a Bearer token.

        Markers cannot be created in some cases (an error will occur):

        - If the specified user’s stream is not live.

        - If VOD (past broadcast) storage is not enabled for the stream.

        - For premieres (live, first-viewing events that combine uploaded videos with live chat).

        - For reruns (subsequent (not live) streaming of any past broadcast, including past premieres).

        # Authentication:
        - OAuth token required

        - Required scope: `channel:manage:broadcast`

        # URL:
        `POST https://api.twitch.tv/helix/streams/markers`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        None

        # Required Body Parameter:
        +-----------+--------+-------------------------------------------------------------------+
        | Name      | Type   | Parameter                                                         |
        +-----------+--------+-------------------------------------------------------------------+
        | `user_id` | string | ID of the broadcaster in whose live stream the marker is created. |
        +-----------+--------+-------------------------------------------------------------------+

        # Optional Body Parameter:
        +---------------+--------+-------------------------------------------------------------------------+
        | Name          | Type   | Parameter                                                               |
        +---------------+--------+-------------------------------------------------------------------------+
        | `description` | string | Description of or comments on the marker. Max length is 140 characters. |
        +---------------+--------+-------------------------------------------------------------------------+

        # Response Fields:
        +--------------------+---------+-------------------------------------------------------------------------------+
        | Field              | Type    | Description                                                                   |
        +--------------------+---------+-------------------------------------------------------------------------------+
        | `created_at`       | string  | RFC3339 timestamp of the marker.                                              |
        +--------------------+---------+-------------------------------------------------------------------------------+
        | `description`      | string  | Description of the marker.                                                    |
        +--------------------+---------+-------------------------------------------------------------------------------+
        | `id`               | string  | Unique ID of the marker.                                                      |
        +--------------------+---------+-------------------------------------------------------------------------------+
        | `position_seconds` | integer | Relative offset (in seconds) of the marker, from the beginning of the stream. |
        +--------------------+---------+-------------------------------------------------------------------------------+
        """
        data = exclude_non_empty(description=description, user_id=user_id)
        return await self._request('POST', 'streams/markers', data=data)

    async def get_stream_markers(
        self, *, after: str = _empty, before: str = _empty, first: str = _empty, user_id: str, video_id: str
    ):
        """
        Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream),
        ordered by recency. A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to
        easily return to later. The only markers returned are those created by the user identified by the Bearer token.

        The response has a JSON payload with a `data` field containing an array of marker information elements and a `pagination` field containing information required to query for more follow information.

        # Authentication:
        - OAuth token required

        - Required scope: `user:read:broadcast`

        # URL:
        `GET https://api.twitch.tv/helix/streams/markers`

        # Required Query Parameter:
        Only one of `user_id` and `video_id` must be specified.

        +------------+--------+---------------------------------------------------------------+
        | Name       | Type   | Description                                                   |
        +------------+--------+---------------------------------------------------------------+
        | `user_id`  | string | ID of the broadcaster from whose stream markers are returned. |
        +------------+--------+---------------------------------------------------------------+
        | `video_id` | string | ID of the VOD/video whose stream markers are returned.        |
        +------------+--------+---------------------------------------------------------------+

        # Optional Query Parameters:
        +----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name     | Type   | Description                                                                                                                                                                                                           |
        +----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`  | string | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.  |
        +----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `before` | string | Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`  | string | Number of values to be returned when getting videos by user or game ID. Limit: 100. Default: 20.                                                                                                                      |
        +----------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field              | Type                       | Description                                                                                                                                              |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `id`               | string                     | ID of the marker.                                                                                                                                        |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `created_at`       | string                     | RFC3339 timestamp of the marker.                                                                                                                         |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `description`      | string                     | Description of the marker.                                                                                                                               |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`       | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results. If this is empty, you are at the last page. |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `position_seconds` | integer                    | Relative offset (in seconds) of the marker, from the beginning of the stream.                                                                            |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `URL`              | string                     | A link to the stream with a query parameter that is a timestamp of the marker's location.                                                                |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`          | string                     | ID of the user whose markers are returned.                                                                                                               |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`        | string                     | Display name corresponding to `user_id`.                                                                                                                 |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login`       | string                     | Login corresponding to `user_id`.                                                                                                                        |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `video_id`         | string                     | ID of the stream (VOD/video) that was marked.                                                                                                            |
        +--------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, before=before, first=first, user_id=user_id, video_id=video_id)
        return await self._request('GET', 'streams/markers', params=params)

    async def get_broadcaster_subscriptions(
        self, *, after: str = _empty, broadcaster_id: str, first: str = _empty, user_id: str = _empty
    ):
        """
        Gets a list of users that subscribe to the specified broadcaster.

        # Authentication:
        - OAuth token required

        - Required scope: `channel:read:subscriptions`

        Subscriptions can be requested on behalf of a broadcaster with a user access token or by a Twitch Extension with an app access token if the broadcaster has granted the `channel:read:subscriptions` scope from within the Twitch Extensions manager.

        # Pagination support:
        Forward only

        # URL:
        `GET https://api.twitch.tv/helix/subscriptions`

        # Required Query Parameter:
        +------------------+--------+-------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                             |
        +------------------+--------+-------------------------------------------------------------------------+
        | `broadcaster_id` | string | User ID of the broadcaster. Must match the User ID in the Bearer token. |
        +------------------+--------+-------------------------------------------------------------------------+

        # Optional Query Parameter:
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type   | Description                                                                                                                                                                                                                                                                                                                                    |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | Filters the list to include only the specified subscribers. To specify more than one subscriber, include this parameter for each subscriber. For example, &user_id=1234&user_id=5678. You may specify a maximum of 100 subscribers.                                                                                                            |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string | Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | string | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                                                                                                                                                |
        +-----------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Return Values:
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Type                       | Description                                                                                                                                                                                                                                                                                                                                                                                                |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_id`    | string                     | User ID of the broadcaster.                                                                                                                                                                                                                                                                                                                                                                                |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_login` | string                     | Login of the broadcaster.                                                                                                                                                                                                                                                                                                                                                                                  |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `broadcaster_name`  | string                     | Display name of the broadcaster.                                                                                                                                                                                                                                                                                                                                                                           |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `gifter_id`         | string                     | If the subscription was gifted, this is the user ID of the gifter. Empty string otherwise.                                                                                                                                                                                                                                                                                                                 |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `gifter_login`      | string                     | If the subscription was gifted, this is the login of the gifter. Empty string otherwise.                                                                                                                                                                                                                                                                                                                   |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `gifter_name`       | string                     | If the subscription was gifted, this is the display name of the gifter. Empty string otherwise.                                                                                                                                                                                                                                                                                                            |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_gift`           | Boolean                    | Is true if the subscription is a gift subscription.                                                                                                                                                                                                                                                                                                                                                        |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `plan_name`         | string                     | Name of the subscription.                                                                                                                                                                                                                                                                                                                                                                                  |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tier`              | string                     | Type of subscription (Tier 1, Tier 2, Tier 3).                                                                                                                                                                                                                                                                                                                                                             |
        |                     |                            | 1000 = Tier 1, 2000 = Tier 2, 3000 = Tier 3 subscriptions.                                                                                                                                                                                                                                                                                                                                                 |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_id`           | string                     | ID of the subscribed user.                                                                                                                                                                                                                                                                                                                                                                                 |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_name`         | string                     | Display name of the subscribed user.                                                                                                                                                                                                                                                                                                                                                                       |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `user_login`        | string                     | Login of the subscribed user.                                                                                                                                                                                                                                                                                                                                                                              |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`        | object containing a string | A cursor value,  to be used in a subsequent request to specify the starting point  of the next set of results. If this is empty, you are at the last page.                                                                                                                                                                                                                                                 |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `total`             | integer                    | The total number of users that subscribe to this broadcaster.                                                                                                                                                                                                                                                                                                                                              |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `points`            | integer                    | The current number of subscriber points earned by this broadcaster. Points are based on the subscription tier of each user that subscribes to this broadcaster. For example, a Tier 1 subscription is worth 1 point, Tier 2 is worth 2 points, and Tier 3 is worth 6 points. The number of points determines the number of emote slots that are unlocked for the broadcaster (see Subscriber Emote Slots). |
        +---------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first, user_id=user_id)
        return await self._request('GET', 'subscriptions', params=params)

    async def check_user_subscription(self, *, broadcaster_id: str, user_id: str):
        """
        Checks if a specific user (`user_id`) is subscribed to a specific channel (`broadcaster_id`).

        # Authentication:
        - User access token with scope `user:read:subscriptions`

        - App access token if the user has authorized your application with scope `user:read:subscriptions`

        # URL:
        `GET https://api.twitch.tv/helix/subscriptions/user`

        # Required Query Parameters:
        +------------------+--------+-------------------------------------------------+
        | Parameter        | Type   | Description                                     |
        +------------------+--------+-------------------------------------------------+
        | `broadcaster_id` | string | User ID of an Affiliate or Partner broadcaster. |
        +------------------+--------+-------------------------------------------------+
        | `user_id`        | string | User ID of a Twitch viewer.                     |
        +------------------+--------+-------------------------------------------------+

        # Response Fields:
        +---------------------+---------+------------------------------------------------------------------------+
        | Field               | Type    | Description                                                            |
        +---------------------+---------+------------------------------------------------------------------------+
        | `broadcaster_id`    | string  | User ID of the broadcaster.                                            |
        +---------------------+---------+------------------------------------------------------------------------+
        | `broadcaster_login` | string  | Login of the broadcaster.                                              |
        +---------------------+---------+------------------------------------------------------------------------+
        | `broadcaster_name`  | string  | Display name of the broadcaster.                                       |
        +---------------------+---------+------------------------------------------------------------------------+
        | `is_gift`           | boolean | Indicates if the subscription is a gift.                               |
        +---------------------+---------+------------------------------------------------------------------------+
        | `gifter_login`      | string  | Login of the gifter (if `is_gift` is `true`).                          |
        +---------------------+---------+------------------------------------------------------------------------+
        | `gifter_name`       | string  | Display name of the gifter (if `is_gift` is `true`).                   |
        +---------------------+---------+------------------------------------------------------------------------+
        | `tier`              | string  | Subscription tier. 1000 is tier 1, 2000 is tier 2, and 3000 is tier 3. |
        +---------------------+---------+------------------------------------------------------------------------+

        # Response Codes:
        +------+------------------------------------------+
        | Code | Meaning                                  |
        +------+------------------------------------------+
        | 200  | User subscription returned successfully. |
        +------+------------------------------------------+
        | 400  | Request was invalid.                     |
        +------+------------------------------------------+
        | 401  | Authorization failed.                    |
        +------+------------------------------------------+
        | 404  | User not subscribed to the channel.      |
        +------+------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id, user_id=user_id)
        return await self._request('GET', 'subscriptions/user', params=params)

    async def get_all_stream_tags(self, *, after: str = _empty, first: int = _empty, tag_id: str = _empty):
        """
        Gets the list of all stream tags that Twitch defines. You can also filter the list by one or more tag IDs.

        For an online list of the possible tags, see List of All Tags.

        # Authentication:
        Requires an application OAuth access token.

        # URL:
        `GET https://api.twitch.tv/helix/tags/streams`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name     | Type    | Description                                                                                                                                                                             |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`  | string  | The cursor used to get the next page of results. The `pagination` object in the response contains the cursor’s value.                                                                   |
        |          |         |                                                                                                                                                                                         |
        |          |         | The `after` and `tag_id` query parameters are mutually exclusive.                                                                                                                       |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`  | integer | The maximum number of tags to return per page.                                                                                                                                          |
        |          |         |                                                                                                                                                                                         |
        |          |         | Maximum: 100. Default: 20.                                                                                                                                                              |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tag_id` | string  | An ID that identifies a specific tag to return. Include the query parameter for each tag you want returned. For example, `tag_id=123&tag_id=456`. You may specify a maximum of 100 IDs. |
        +----------+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field                       | Type               | Description                                                                                                                                                                                                                                   |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`                      | object array       | An array of tag objects.                                                                                                                                                                                                                      |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tag_id`                    | string             | An ID that identifies the tag.                                                                                                                                                                                                                |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_auto`                   | Boolean            | A Boolean value that determines whether the tag is an automatic tag. An automatic tag is one that Twitch adds to the stream. You cannot add or remove automatic tags. The value is `true` if the tag is an automatic tag; otherwise, `false`. |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `localization_names`        | map[string,string] | A dictionary that contains the localized names of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized name.                                                                             |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `localization_descriptions` | map[string,string] | A dictionary that contains the localized descriptions of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized description.                                                               |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`                | object             | An object that contains the cursor used to get the next page of tags.                                                                                                                                                                         |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cursor`                    | string             | The cursor value that you set the `after` query parameter to.                                                                                                                                                                                 |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, first=first, tag_id=tag_id)
        return await self._request('GET', 'tags/streams', params=params)

    async def get_stream_tags(self, *, broadcaster_id: str):
        """
        Gets the list of stream tags that are set on the specified channel.

        # Authentication:
        Requires an application OAuth access token.

        # URL:
        `GET https://api.twitch.tv/helix/streams/tags`

        # Required Query Parameters:
        +------------------+--------+--------------------------------------------------+
        | Name             | Type   | Description                                      |
        +------------------+--------+--------------------------------------------------+
        | `broadcaster_id` | string | The user ID of the channel to get the tags from. |
        +------------------+--------+--------------------------------------------------+

        # Optional Query Parameters:
        None

        # Response Fields:
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Field                       | Type               | Description                                                                                                                                                                                                                                   |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `data`                      | object array       | An array of tag objects.                                                                                                                                                                                                                      |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `tag_id`                    | string             | An ID that identifies the tag.                                                                                                                                                                                                                |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `is_auto`                   | Boolean            | A Boolean value that determines whether the tag is an automatic tag. An automatic tag is one that Twitch adds to the stream. You cannot add or remove automatic tags. The value is `true` if the tag is an automatic tag; otherwise, `false`. |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `localization_names`        | map[string,string] | A dictionary that contains the localized names of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized name.                                                                             |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `localization_descriptions` | map[string,string] | A dictionary that contains the localized descriptions of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized description.                                                               |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `pagination`                | object             | An object that contains the cursor used to get the next page of tags.                                                                                                                                                                         |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `cursor`                    | string             | The cursor value that you set the `after` query parameter to.                                                                                                                                                                                 |
        +-----------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'streams/tags', params=params)

    async def replace_stream_tags(self, *, broadcaster_id: str, tag_ids: List[str] = _empty):
        """
        Applies one or more tags to the specified channel, overwriting any existing tags. If the request does not
        specify tags, all existing tags are removed from the channel.

        NOTE: You may not specify automatic tags; the call will fail if you specify automatic tags. Automatic tags are tags that Twitch applies to the channel. For a list of automatic tags, see List of All Tags. To get the list programmatically, see Get All Stream Tags.

        Tags expire 72 hours after they are applied, unless the channel is live within that time period. If the channel is live within the 72-hour window, the 72-hour clock restarts when the channel goes offline. The expiration period is subject to change.

        # Authentication:
        Requires a user OAuth access token with a scope of `channel:manage:broadcast`.

        # URL:
        `PUT https://api.twitch.tv/helix/streams/tags`

        # Required Query Parameters:
        +------------------+--------+--------------------------------------------------+
        | Name             | Type   | Description                                      |
        +------------------+--------+--------------------------------------------------+
        | `broadcaster_id` | string | The user ID of the channel to apply the tags to. |
        +------------------+--------+--------------------------------------------------+

        # Optional Query Parameters:
        None

        # Optional Body Parameter:
        +-----------+--------------+-------------------------------------------------------------------------------------------------------+
        | Name      | Type         | Description                                                                                           |
        +-----------+--------------+-------------------------------------------------------------------------------------------------------+
        | `tag_ids` | string array | A list of IDs that identify the tags to apply to the channel. You may specify a maximum of five tags. |
        |           |              |                                                                                                       |
        |           |              | To remove all tags from the channel, set `tag_ids` to an empty array.                                 |
        +-----------+--------------+-------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        data = exclude_non_empty(tag_ids=tag_ids)
        return await self._request('PUT', 'streams/tags', params=params, data=data)

    async def get_channel_teams(self, *, broadcaster_id: str):
        """
        Retrieves a list of Twitch Teams of which the specified channel/broadcaster is a member.

        # Authentication:
        - User OAuth Token or App Access Token

        # URL:
        `GET https://api.twitch.tv/helix/teams/channel`

        # Required Query Parameters:
        +------------------+--------+----------------------------+
        | Parameter        | Type   | Description                |
        +------------------+--------+----------------------------+
        | `broadcaster_id` | string | User ID for a Twitch user. |
        +------------------+--------+----------------------------+

        # Response Fields:
        +------------------------+--------+------------------------------------------+
        | Field                  | Type   | Description                              |
        +------------------------+--------+------------------------------------------+
        | `broadcaster_id`       | string | User ID of the broadcaster.              |
        +------------------------+--------+------------------------------------------+
        | `broadcaster_login`    | string | Login of the broadcaster.                |
        +------------------------+--------+------------------------------------------+
        | `broadcaster_name`     | string | Display name of the broadcaster.         |
        +------------------------+--------+------------------------------------------+
        | `background_image_url` | string | URL for the Team background image.       |
        +------------------------+--------+------------------------------------------+
        | `banner`               | string | URL for the Team banner.                 |
        +------------------------+--------+------------------------------------------+
        | `created_at`           | string | Date and time the Team was created.      |
        +------------------------+--------+------------------------------------------+
        | `updated_at`           | string | Date and time the Team was last updated. |
        +------------------------+--------+------------------------------------------+
        | `info`                 | string | Team description.                        |
        +------------------------+--------+------------------------------------------+
        | `thumbnail_url`        | string | Image URL for the Team logo.             |
        +------------------------+--------+------------------------------------------+
        | `team_name`            | string | Team name.                               |
        +------------------------+--------+------------------------------------------+
        | `team_display_name`    | string | Team display name.                       |
        +------------------------+--------+------------------------------------------+
        | `id`                   | string | Team ID.                                 |
        +------------------------+--------+------------------------------------------+

        # Response Codes:
        +------+----------------------------------------------+
        | Code | Meaning                                      |
        +------+----------------------------------------------+
        | 200  | List of Channel Teams returned successfully. |
        +------+----------------------------------------------+
        | 400  | Request was invalid.                         |
        +------+----------------------------------------------+
        | 401  | Authorization failed.                        |
        +------+----------------------------------------------+
        """
        params = exclude_non_empty(broadcaster_id=broadcaster_id)
        return await self._request('GET', 'teams/channel', params=params)

    async def get_teams(self, *, id_: str = _empty, name: str = _empty):
        """
        Gets information for a specific Twitch Team.

        # Authentication:
        - User OAuth Token or App Access Token

        # URL:
        `GET https://api.twitch.tv/helix/teams`

        # Required Query Parameters:
        One of the two optional query parameters must be specified to return Team information.

        # Optional Query Parameters:
        +-----------+--------+-------------+
        | Parameter | Type   | Description |
        +-----------+--------+-------------+
        | `name`    | string | Team name.  |
        +-----------+--------+-------------+
        | `id`      | string | Team ID.    |
        +-----------+--------+-------------+

        # Response Fields:
        +------------------------+-----------------------+------------------------------------------+
        | Field                  | Type                  | Description                              |
        +------------------------+-----------------------+------------------------------------------+
        | `users`                | Array of user objects | Users in the specified Team.             |
        +------------------------+-----------------------+------------------------------------------+
        | `users.user_id`        | string                | User ID of a Team member.                |
        +------------------------+-----------------------+------------------------------------------+
        | `users.user_login`     | string                | Login of a Team member.                  |
        +------------------------+-----------------------+------------------------------------------+
        | `users.user_name`      | string                | Display name of a Team member.           |
        +------------------------+-----------------------+------------------------------------------+
        | `background_image_url` | string                | URL of the Team background image.        |
        +------------------------+-----------------------+------------------------------------------+
        | `banner`               | string                | URL for the Team banner.                 |
        +------------------------+-----------------------+------------------------------------------+
        | `created_at`           | string                | Date and time the Team was created.      |
        +------------------------+-----------------------+------------------------------------------+
        | `updated_at`           | string                | Date and time the Team was last updated. |
        +------------------------+-----------------------+------------------------------------------+
        | `info`                 | string                | Team description.                        |
        +------------------------+-----------------------+------------------------------------------+
        | `thumbnail_url`        | string                | Image URL for the Team logo.             |
        +------------------------+-----------------------+------------------------------------------+
        | `team_name`            | string                | Team name.                               |
        +------------------------+-----------------------+------------------------------------------+
        | `team_display_name`    | string                | Team display name.                       |
        +------------------------+-----------------------+------------------------------------------+
        | `id`                   | string                | Team ID.                                 |
        +------------------------+-----------------------+------------------------------------------+

        # Response Codes:
        +------+-----------------------------------------+
        | Code | Meaning                                 |
        +------+-----------------------------------------+
        | 200  | Team information returned successfully. |
        +------+-----------------------------------------+
        | 400  | Request was invalid.                    |
        +------+-----------------------------------------+
        | 401  | Authorization failed.                   |
        +------+-----------------------------------------+
        """
        params = exclude_non_empty(id=id_, name=name)
        return await self._request('GET', 'teams', params=params)

    async def get_users(self, *, id_: Union[str, List[str]] = _empty, login: Union[str, List[str]] = _empty):
        """
        Gets information about one or more specified Twitch users. Users are identified by optional user IDs and/or
        login name. If neither a user ID nor a login name is specified, the user is looked up by Bearer token.

        The response has a JSON payload with a `data` field containing an array of user-information elements.

        # Authentication:
        - OAuth or App Access Token required.

        # Authorization:
        - OAuth token with `user:read:email` scope required to include the user’s verified email address in response.

        # URL:
        `GET https://api.twitch.tv/helix/users`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +---------+--------+---------------------------------------------------------------------+
        | Name    | Type   | Description                                                         |
        +---------+--------+---------------------------------------------------------------------+
        | `id`    | string | User ID. Multiple user IDs can be specified. Limit: 100.            |
        +---------+--------+---------------------------------------------------------------------+
        | `login` | string | User login name. Multiple login names can be specified. Limit: 100. |
        +---------+--------+---------------------------------------------------------------------+

        Note: The limit of 100 IDs and login names is the total limit. You can request, for example, 50 of each or 100 of one of them. You cannot request 100 of both.

        A request can include a mixture of login names and user ID. If specifying multiple values (any combination of `id` and/or `login` values), separate them with ampersands; e.g.,
        `GET https://api.twitch.tv/helix/users?login=<login name>&id=<user ID>...`
        `GET https://api.twitch.tv/helix/users?id=<user ID>&id=<user ID>...`
        GET https://api.twitch.tv/helix/users?login=<login name>&login=<login name>...

        # Response Fields:
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | Field               | Type    | Description                                                                                  |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `broadcaster_type`  | string  | User’s broadcaster type: `"partner"`, `"affiliate"`, or `""`.                                |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `description`       | string  | User’s channel description.                                                                  |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `display_name`      | string  | User’s display name.                                                                         |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `id`                | string  | User’s ID.                                                                                   |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `login`             | string  | User’s login name.                                                                           |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `offline_image_url` | string  | URL of the user’s offline image.                                                             |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `profile_image_url` | string  | URL of the user’s profile image.                                                             |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `type`              | string  | User’s type: `"staff"`, `"admin"`, `"global_mod"`, or `""`.                                  |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `view_count`        | integer | Total number of views of the user’s channel.                                                 |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `email`             | string  | User’s verified email address. Returned if the request includes the `user:read:email` scope. |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        | `created_at`        | string  | Date when the user was created.                                                              |
        +---------------------+---------+----------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(id=id_, login=login)
        return await self._request('GET', 'users', params=params)

    async def update_user(self, *, description: str = _empty):
        """
        Updates the description of a user specified by the bearer token. Note that the description parameter is optional
        should other updatable parameters become available in the future. If the description parameter is not provided,
        no update will occur and the current user data is returned.

        # Authentication:
        -
            OAuth token required


        -
            Required scope: `user:edit`

        # URL:
        `PUT https://api.twitch.tv/helix/users?description=<description>`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +-------------+--------+----------------------------+
        | Parameter   | Type   | Description                |
        +-------------+--------+----------------------------+
        | description | string | User’s account description |
        +-------------+--------+----------------------------+

        # Response Fields:
        Response fields are the same as for Get Users. Email is only returned if the `user:read:email` is also provided.
        """
        params = exclude_non_empty(description=description)
        return await self._request('PUT', 'users', params=params)

    async def get_users_follows(
        self, *, after: str = _empty, first: int = _empty, from_id: str = _empty, to_id: str = _empty
    ):
        """
        Gets information on follow relationships between two Twitch users. This can return information like “who is
        qotrok following,” “who is following qotrok,” or “is user X following user Y.” Information returned is sorted in
        order, most recent follow first.

        The response has a JSON payload with a `data` field containing an array of follow relationship elements and a `pagination` field containing information required to query for more follow information.

        # Authentication:
        - User OAuth Token or App Access Token

        # URLs:
        `GET https://api.twitch.tv/helix/users/follows?from_id=<user ID>`
        `GET https://api.twitch.tv/helix/users/follows?to_id=<user ID>`

        At minimum, `from_id` or `to_id` must be provided for a query to be valid.

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name      | Type    | Description                                                                                                                                                                                                          |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | integer | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                      |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `from_id` | string  | User ID. The request returns information about users who are being followed by the `from_id` user.                                                                                                                   |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `to_id`   | string  | User ID. The request returns information about users who are following the `to_id` user.                                                                                                                             |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | Field         | Type                       | Description                                                                                                     |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `followed_at` | string                     | Date and time when the `from_id` user followed the `to_id` user.                                                |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `from_id`     | string                     | ID of the user following the `to_id` user.                                                                      |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `from_login`  | string                     | Login of the user following the `to_id` user.                                                                   |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `from_name`   | string                     | Display name corresponding to `from_id`.                                                                        |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `pagination`  | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results.    |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `to_id`       | string                     | ID of the user being followed by the `from_id` user.                                                            |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `to_login`    | string                     | Login of the user being followed by the `from_id` user.                                                         |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `to_name`     | string                     | Display name corresponding to `to_id`.                                                                          |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        | `total`       | int                        | Total number of items returned.                                                                                 |
        |               |                            | - If only `from_id` was in the request, this is the total number of followed users.                             |
        |               |                            | - If only `to_id` was in the request, this is the total number of followers.                                    |
        |               |                            | - If both `from_id` and `to_id` were in the request, this is 1 (if the "from" user follows the "to" user) or 0. |
        +---------------+----------------------------+-----------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(after=after, first=first, from_id=from_id, to_id=to_id)
        return await self._request('GET', 'users/follows', params=params)

    async def get_user_block_list(self, *, after: str = _empty, broadcaster_id: str, first: int = _empty):
        """
        Gets a specified user’s block list. The list is sorted by when the block occurred in descending order (i.e. most
        recent block first).

        # Authentication:
        - OAuth user token required

        - Required scope: `user:read:blocked_users`

        # URL:
        `GET https://api.twitch.tv/helix/users/blocks`

        # Required Query Parameters:
        +------------------+--------+----------------------------+
        | Parameter        | Type   | Description                |
        +------------------+--------+----------------------------+
        | `broadcaster_id` | string | User ID for a Twitch user. |
        +------------------+--------+----------------------------+

        # Optional Query Parameters:
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter | Type    | Description                                                                                                                                                                                                          |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`   | integer | Maximum number of objects to return. Maximum: 100. Default: 20.                                                                                                                                                      |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`   | string  | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +-----------+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +----------------+--------+-----------------------------------+
        | Field          | Type   | Description                       |
        +----------------+--------+-----------------------------------+
        | `user_id`      | string | User ID of the blocked user.      |
        +----------------+--------+-----------------------------------+
        | `user_login`   | string | Login of the blocked user.        |
        +----------------+--------+-----------------------------------+
        | `display_name` | string | Display name of the blocked user. |
        +----------------+--------+-----------------------------------+

        # Response Codes:
        +------+------------------------------------------+
        | Code | Meaning                                  |
        +------+------------------------------------------+
        | 200  | User’s block list returned successfully. |
        +------+------------------------------------------+
        | 400  | Request was invalid.                     |
        +------+------------------------------------------+
        | 401  | Authorization failed.                    |
        +------+------------------------------------------+
        """
        params = exclude_non_empty(after=after, broadcaster_id=broadcaster_id, first=first)
        return await self._request('GET', 'users/blocks', params=params)

    async def block_user(self, *, reason: str = _empty, source_context: str = _empty, target_user_id: str):
        """
        Blocks the specified user on behalf of the authenticated user.

        # Authentication:
        - OAuth user token required

        - Required scope: `user:manage:blocked_users`

        # URL:
        `PUT https://api.twitch.tv/helix/users/blocks`

        # Required Query Parameters:
        +------------------+--------+------------------------------------+
        | Parameter        | Type   | Description                        |
        +------------------+--------+------------------------------------+
        | `target_user_id` | string | User ID of the user to be blocked. |
        +------------------+--------+------------------------------------+

        # Optional Query Parameters:
        +------------------+--------+-------------------------------------------------------------------------------------+
        | Parameter        | Type   | Description                                                                         |
        +------------------+--------+-------------------------------------------------------------------------------------+
        | `source_context` | string | Source context for blocking the user. Valid values: `"chat"`, `"whisper"`.          |
        +------------------+--------+-------------------------------------------------------------------------------------+
        | `reason`         | string | Reason for blocking the user. Valid values: `"spam"`, `"harassment"`, or `"other"`. |
        +------------------+--------+-------------------------------------------------------------------------------------+

        # Response Codes:
        +------+----------------------------+
        | Code | Meaning                    |
        +------+----------------------------+
        | 204  | User blocked successfully. |
        +------+----------------------------+
        | 400  | Request was invalid.       |
        +------+----------------------------+
        | 401  | Authorization failed.      |
        +------+----------------------------+
        """
        params = exclude_non_empty(reason=reason, source_context=source_context, target_user_id=target_user_id)
        return await self._request('PUT', 'users/blocks', params=params)

    async def unblock_user(self, *, target_user_id: str):
        """
        Unblocks the specified user on behalf of the authenticated user.

        # Authentication:
        - OAuth user token required

        - Required scope: `user:manage:blocked_users`

        # URL:
        `DELETE https://api.twitch.tv/helix/users/blocks`

        # Required Query Parameters:
        +------------------+--------+--------------------------------------+
        | Parameter        | Type   | Description                          |
        +------------------+--------+--------------------------------------+
        | `target_user_id` | string | User ID of the user to be unblocked. |
        +------------------+--------+--------------------------------------+

        # Optional Query Parameters:
        None.

        # Response Codes:
        +------+------------------------------+
        | Code | Meaning                      |
        +------+------------------------------+
        | 204  | User unblocked successfully. |
        +------+------------------------------+
        | 400  | Request was invalid.         |
        +------+------------------------------+
        | 401  | Authorization failed.        |
        +------+------------------------------+
        """
        params = exclude_non_empty(target_user_id=target_user_id)
        return await self._request('DELETE', 'users/blocks', params=params)

    async def get_user_extensions(self):
        """
        Gets a list of all extensions (both active and inactive) for a specified user, identified by a Bearer token.

        The response has a JSON payload with a `data` field containing an array of user-information elements.

        # Authentication:
        - OAuth token required

        - Required scope: `user:read:broadcast`

        # URL:
        `GET https://api.twitch.tv/helix/users/extensions/list`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        None

        # Response Fields:
        +----------------+--------------+------------------------------------------------------------------------------------------------------------------+
        | Field          | Type         | Description                                                                                                      |
        +----------------+--------------+------------------------------------------------------------------------------------------------------------------+
        | `can_activate` | boolean      | Indicates whether the extension is configured such that it can be activated.                                     |
        +----------------+--------------+------------------------------------------------------------------------------------------------------------------+
        | `id`           | string       | ID of the extension.                                                                                             |
        +----------------+--------------+------------------------------------------------------------------------------------------------------------------+
        | `name`         | string       | Name of the extension.                                                                                           |
        +----------------+--------------+------------------------------------------------------------------------------------------------------------------+
        | `type`         | string array | Types for which the extension can be activated. Valid values: `"component"`, `"mobile"`, `"panel"`, `"overlay"`. |
        +----------------+--------------+------------------------------------------------------------------------------------------------------------------+
        | `version`      | string       | Version of the extension.                                                                                        |
        +----------------+--------------+------------------------------------------------------------------------------------------------------------------+
        """
        return await self._request('GET', 'users/extensions/list')

    async def get_user_active_extensions(self, *, user_id: str = _empty):
        """
        Gets information about active extensions installed by a specified user, identified by a user ID or Bearer token.

        # Authentication:
        - OAuth token required

        - Optional scope: `user:read:broadcast` or `user:edit:broadcast`

        # URL:
        `GET https://api.twitch.tv/helix/users/extensions`

        # Required Query Parameters:
        None

        # Optional Query Parameter:
        +-----------+--------+-----------------------------------------------------------------------+
        | Name      | Type   | Description                                                           |
        +-----------+--------+-----------------------------------------------------------------------+
        | `user_id` | string | ID of the user whose installed extensions will be returned. Limit: 1. |
        +-----------+--------+-----------------------------------------------------------------------+

        # Response Fields:
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | Field       | Type    | Description                                                                                                                            |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `active`    | boolean | Activation state of the extension, for each extension type (component, overlay, mobile, panel). If `false`, no other data is provided. |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `component` | map     | Contains data for video-component Extensions.                                                                                          |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `id`        | string  | ID of the extension.                                                                                                                   |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `name`      | string  | Name of the extension.                                                                                                                 |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `overlay`   | map     | Contains data for video-overlay Extensions.                                                                                            |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `panel`     | map     | Contains data for panel Extensions.                                                                                                    |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `version`   | string  | Version of the extension.                                                                                                              |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `x`         | int     | (Video-component Extensions only) X-coordinate of the placement of the extension.                                                      |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        | `y`         | int     | (Video-component Extensions only) Y-coordinate of the placement of the extension.                                                      |
        +-------------+---------+----------------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(user_id=user_id)
        return await self._request('GET', 'users/extensions', params=params)

    async def update_user_extensions(self):
        """
        Updates the activation state, extension ID, and/or version number of installed extensions for a specified user,
        identified by a Bearer token. If you try to activate a given extension under multiple extension types, the last
        write wins (and there is no guarantee of write order).

        # Authentication:
        - OAuth token required

        - Required scope: `user:edit:broadcast`

        # URL:
        `PUT https://api.twitch.tv/helix/users/extensions`

        # Required Query Parameters:
        None

        # Optional Query Parameters:
        None

        # Response Fields:
        Response fields are the same as for Get User Active Extensions.
        """
        return await self._request('PUT', 'users/extensions')

    async def get_videos(
        self,
        *,
        after: str = _empty,
        before: str = _empty,
        first: str = _empty,
        game_id: str,
        id_: Union[str, List[str]],
        language: str = _empty,
        period: str = _empty,
        sort: str = _empty,
        type_: str = _empty,
        user_id: str,
    ):
        """
        Gets video information by one or more video IDs, user ID, or game ID. For lookup by user or game, several
        filters are available that can be specified as query parameters.

        # Authentication:
        - User OAuth Token or App Access Token

        # Pagination Support:
        Forward pagination for requests that specify `user_id` or `game_id`. If a game is specified, a maximum of 500 results are available.

        # URL:
        `GET https://api.twitch.tv/helix/videos`

        # Required Query Parameters:
        Each request must specify one or more video `id`s, one `user_id`, or one `game_id`.

        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------+
        | Name      | Type   | Description                                                                                                                 |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------+
        | `id`      | string | ID of the video being queried. Limit: 100. If this is specified, you cannot use any of the optional query parameters below. |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------+
        | `user_id` | string | ID of the user who owns the video. Limit 1.                                                                                 |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------+
        | `game_id` | string | ID of the game the video is of. Limit 1.                                                                                    |
        +-----------+--------+-----------------------------------------------------------------------------------------------------------------------------+

        # Optional Query Parameters:
        These can be used if the request specifies a `user_id` or `game_id`, not a video `id`.

        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Name       | Type   | Description                                                                                                                                                                                                           |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `after`    | string | Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.  |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `before`   | string | Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query. |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `first`    | string | Number of values to be returned when getting videos by user or game ID. Limit: 100. Default: 20.                                                                                                                      |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `language` | string | Language of the video being queried. Limit: 1. A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”.                                                              |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `period`   | string | Period during which the video was created. Valid values: `"all"`, `"day"`, `"week"`, `"month"`. Default: `"all"`.                                                                                                     |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `sort`     | string | Sort order of the videos. Valid values: `"time"`, `"trending"`, `"views"`. Default: `"time"`.                                                                                                                         |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | `type`     | string | Type of video. Valid values: `"all"`, `"upload"`, `"archive"`, `"highlight"`. Default: `"all"`.                                                                                                                       |
        +------------+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        # Response Fields:
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | Fields             | Type                       | Description                                                                                                                 |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `id`               | string                     | ID of the video.                                                                                                            |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `stream_id`        | string                     | ID of the stream that the video originated from if the `type` is `"archive"`. Otherwise set to `null`.                      |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `user_id`          | string                     | ID of the user who owns the video.                                                                                          |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `user_login`       | string                     | Login of the user who owns the video.                                                                                       |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `user_name`        | string                     | Display name corresponding to `user_id`.                                                                                    |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `title`            | string                     | Title of the video.                                                                                                         |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `description`      | string                     | Description of the video.                                                                                                   |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `created_at`       | string                     | Date when the video was created.                                                                                            |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `published_at`     | string                     | Date when the video was published.                                                                                          |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `url`              | object                     | URL of the video.                                                                                                           |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `thumbnail_url`    | object                     | Template URL for the thumbnail of the video.                                                                                |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `viewable`         | string                     | Indicates whether the video is publicly viewable. Valid values: `"public"`, `"private"`.                                    |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `view_count`       | int                        | Number of times the video has been viewed.                                                                                  |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `language`         | string                     | Language of the video. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”. |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `type`             | string                     | Type of video. Valid values: `"upload"`, `"archive"`, `"highlight"`.                                                        |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `duration`         | string                     | Length of the video.                                                                                                        |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `muted_segments`   | object[]                   | Array of muted segments in the video. If there are no muted segments, the value will be `null`.                             |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `segment.duration` | integer                    | Duration of the muted segment.                                                                                              |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `segment.offset`   | integer                    | Offset in the video at which the muted segment begins.                                                                      |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | `pagination`       | object containing a string | A cursor value, to be used in a subsequent request to specify the starting point of the next set of results.                |
        +--------------------+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(
            after=after,
            before=before,
            first=first,
            game_id=game_id,
            id=id_,
            language=language,
            period=period,
            sort=sort,
            type=type_,
            user_id=user_id,
        )
        return await self._request('GET', 'videos', params=params)

    async def delete_videos(self, *, id_: Union[str, List[str]]):
        """
        Deletes one or more videos. Videos are past broadcasts, Highlights, or uploads.

        Invalid Video IDs will be ignored (i.e. IDs provided that do not have a video associated with it). If the OAuth user token does not have permission to delete even one of the valid Video IDs, no videos will be deleted and the response will return a 401.

        # Authentication:
        - User OAuth token

        - Required scope: `channel:manage:videos`

        # URL:
        `DELETE https://api.twitch.tv/helix/videos`

        # Required Query Parameters:
        +------+--------+---------------------------------------------+
        | Name | Type   | Description                                 |
        +------+--------+---------------------------------------------+
        | `id` | string | ID of the video(s) to be deleted. Limit: 5. |
        +------+--------+---------------------------------------------+

        # Optional Query Parameters:
        None.

        # Response Codes:
        +------+-------------------------------------------------------------------------------------------------------------------------------+
        | Code | Meaning                                                                                                                       |
        +------+-------------------------------------------------------------------------------------------------------------------------------+
        | 200  | Video(s) deleted.                                                                                                             |
        +------+-------------------------------------------------------------------------------------------------------------------------------+
        | 400  | Request was invalid.                                                                                                          |
        +------+-------------------------------------------------------------------------------------------------------------------------------+
        | 401  | Authorization failed; either for the API request itself or if the requester is not authorized to delete the specified videos. |
        +------+-------------------------------------------------------------------------------------------------------------------------------+
        """
        params = exclude_non_empty(id=id_)
        return await self._request('DELETE', 'videos', params=params)
