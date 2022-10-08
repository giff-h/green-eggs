/* eslint-disable @typescript-eslint/naming-convention */
export interface PaginatedCursorResponse {
    pagination: { cursor?: string };
}
export interface PaginatedFlatResponse {
    pagination: string;
}
export interface DataObjectResponse<T> {
    data: T;
}
export interface DataListResponse<T> {
    data: T[];
}
interface EventSubBroadcasterCondition {
    /**
     * The broadcaster user ID for the channel you want to get events for.
     */
    broadcaster_user_id: string;
}
interface EventSubRaidCondition {
    /**
     * The broadcaster user ID that created the channel raid you want to get notifications for. Use this parameter if you want to know when a specific broadcaster raids another broadcaster. The channel raid condition must include either `from_broadcaster_user_id` or `to_broadcaster_user_id`.
     */
    from_broadcaster_user_id?: string;
    /**
     * The broadcaster user ID that received the channel raid you want to get notifications for. Use this parameter if you want to know when a specific broadcaster is raided by another broadcaster. The channel raid condition must include either `from_broadcaster_user_id` or `to_broadcaster_user_id`.
     */
    to_broadcaster_user_id?: string;
}
interface EventSubRewardCondition extends EventSubBroadcasterCondition {
    /**
     * Optional. Specify a reward id to only receive notifications for a specific reward.
     */
    reward_id?: string;
}
interface EventSubDropEntitlementGrantCondition {
    /**
     * The organization ID of the organization that owns the game on the developer portal.
     */
    organization_id: string;
    /**
     * The category (or game) ID of the game for which entitlement notifications will be received.
     */
    category_id?: string;
    /**
     * The campaign ID for a specific campaign for which entitlement notifications will be received.
     */
    campaign_id?: string;
}
interface EventSubExtensionBitsTransactionCreateCondition {
    /**
     * The client ID of the extension.
     */
    extension_client_id: string;
}
interface EventSubUserAuthorizationCondition {
    /**
     * Your application’s client id. The provided `client_id` must match the client id in the application access token.
     */
    client_id: string;
}
interface EventSubUserUpdateCondition {
    /**
     * The user ID for the user you want update notifications for.
     */
    user_id: string;
}
type EventSubCondition =
    | EventSubBroadcasterCondition
    | EventSubRaidCondition
    | EventSubRewardCondition
    | EventSubDropEntitlementGrantCondition
    | EventSubExtensionBitsTransactionCreateCondition
    | EventSubUserAuthorizationCondition
    | EventSubUserUpdateCondition;
interface EventSubTransport {
    /**
     * The transport method. Supported values: `webhook`.
     */
    method: "webhook";
    /**
     * The callback URL where the notification should be sent.
     */
    callback: string;
    /**
     * The secret used for verifying a signature.
     */
    secret: string;
}
// All code below is automatically generated
export interface StartCommercialBody {
/**
 * ID of the channel requesting a commercial
 * Minimum: 1 Maximum: 1
 */
broadcaster_id: string;
/**
 * Desired length of the commercial in seconds. 
 * Valid options are 30, 60, 90, 120, 150, 180.
 */
length: number;
}
export interface StartCommercialResponseData {
/**
 * Length of the triggered commercial
 */
length: number;
/**
 * Provides contextual information on why the request failed
 */
message: string;
/**
 * Seconds until the next commercial can be served on this channel
 */
retry_after: number;
}
export type StartCommercialResponse = DataListResponse<StartCommercialResponseData>;
export interface GetExtensionAnalyticsParams {
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries without `extension_id`. If an `extension_id `is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`. The report covers the entire ending date; e.g., if `2018-05-01T00:00:00Z` is specified, the report covers up to `2018-05-01T23:59:59Z`.
 * 
 * If this is provided, `started_at` also must be specified. If `ended_at` is later than the default end date, the default date is used. Default: 1-2 days before the request was issued (depending on report availability).
 */
ended_at?: string;
/**
 * Client ID value assigned to the extension when it is created. If this is specified, the returned URL points to an analytics report for just the specified extension. If this is not specified, the response includes multiple URLs (paginated), pointing to separate analytics reports for each of the authenticated user’s Extensions.
 */
extension_id?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: number;
/**
 * Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`. This must be on or after January 31, 2018.
 * 
 * If this is provided, `ended_at` also must be specified. If `started_at` is earlier than the default start date, the default date is used. The file contains one row of data per day.
 */
started_at?: string;
/**
 * Type of analytics report that is returned. Currently, this field has no affect on the response as there is only one report type. If additional types were added, using this field would return only the URL for the specified report. Limit: 1. Valid values: `"overview_v2"`.
 */
type?: string;
}
export interface GetExtensionAnalyticsResponseData {
/**
 * Report end date/time.
 */
ended_at: string;
/**
 * ID of the extension whose analytics data is being provided.
 */
extension_id: string;
/**
 * Report start date/time. Note this may differ from (be later than) the `started_at` value in the request; the response value is the date when data for the extension is available.
 */
started_at: string;
/**
 * Type of report.
 */
type: string;
/**
 * URL to the downloadable CSV file containing analytics data. Valid for 5 minutes.
 */
URL: string;
}
export type GetExtensionAnalyticsResponse = DataListResponse<GetExtensionAnalyticsResponseData> & PaginatedCursorResponse;
export interface GetGameAnalyticsParams {
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries without `game_id`. If a `game_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`. The report covers the entire ending date; e.g., if `2018-05-01T00:00:00Z` is specified, the report covers up to `2018-05-01T23:59:59Z`.
 * 
 * If this is provided, `started_at` also must be specified. If `ended_at` is later than the default end date, the default date is used. Default: 1-2 days before the request was issued (depending on report availability).
 */
ended_at?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: number;
/**
 * Game ID. If this is specified, the returned URL points to an analytics report for just the specified game. If this is not specified, the response includes multiple URLs (paginated), pointing to separate analytics reports for each of the authenticated user’s games.
 */
game_id?: string;
/**
 * Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: `YYYY-MM-DDT00:00:00Z`.
 * 
 * If this is provided, `ended_at` also must be specified. If `started_at` is earlier than the default start date, the default date is used. Default: 365 days before the report was issued. The file contains one row of data per day.
 */
started_at?: string;
/**
 * Type of analytics report that is returned. Currently, this field has no affect on the response as there is only one report type. If additional types were added, using this field would return only the URL for the specified report. Limit: 1. Valid values: `"overview_v2"`.
 */
type?: string;
}
export interface GetGameAnalyticsResponseData {
/**
 * Report end date/time.
 */
ended_at: string;
/**
 * ID of the game whose analytics data is being provided.
 */
game_id: string;
/**
 * Report start date/time.
 */
started_at: string;
/**
 * Type of report.
 */
type: string;
/**
 * URL to the downloadable CSV file containing analytics data. Valid for 5 minutes.
 */
URL: string;
}
export type GetGameAnalyticsResponse = DataListResponse<GetGameAnalyticsResponseData> & PaginatedCursorResponse;
export interface GetBitsLeaderboardParams {
/**
 * Number of results to be returned. Maximum: 100. Default: 10.
 */
count?: number;
/**
 * Time period over which data is aggregated (PST time zone). This parameter interacts with `started_at`. Valid values follow. Default: `"all"`.
 * - `"day"` – 00:00:00 on the day specified in `started_at`, through 00:00:00 on the following day.
 * - `"week"` – 00:00:00 on Monday of the week specified in `started_at`, through 00:00:00 on the following Monday.
 * - `"month"` – 00:00:00 on the first day of the month specified in `started_at`, through 00:00:00 on the first day of the following month.
 * - `"year"` – 00:00:00 on the first day of the year specified in `started_at`, through 00:00:00 on the first day of the following year.
 * - `"all"` – The lifetime of the broadcaster's channel. If this is specified (or used by default), `started_at` is ignored.
 */
period?: string;
/**
 * Timestamp for the period over which the returned data is aggregated. Must be in RFC 3339 format. If this is not provided, data is aggregated over the current period; e.g., the current day/week/month/year. This value is ignored if `period` is `"all"`.
 * 
 * Any `+` operator should be URL encoded.
 * 
 * Currently, the HH:MM:SS part of this value is used only to identify a given day in PST and otherwise ignored. For example, if the `started_at` value resolves to 5PM PST yesterday and `period` is `"day"`, data is returned for all of yesterday.
 */
started_at?: string;
/**
 * ID of the user whose results are returned; i.e., the person who paid for the Bits.
 * 
 * As long as `count` is greater than 1, the returned data includes additional users, with Bits amounts above and below the user specified by `user_id`.
 * 
 * If `user_id` is not provided, the endpoint returns the Bits leaderboard data across top users (subject to the value of `count`).
 */
user_id?: string;
}
export interface GetBitsLeaderboardResponseData {
/**
 * End of the date range for the returned data.
 */
ended_at: string;
/**
 * Leaderboard rank of the user.
 */
rank: number;
/**
 * Leaderboard score (number of Bits) of the user.
 */
score: number;
/**
 * Start of the date range for the returned data.
 */
started_at: string;
/**
 * Total number of results (users) returned. This is `count` or the total number of entries in the leaderboard, whichever is less.
 */
total: number;
/**
 * ID of the user (viewer) in the leaderboard entry.
 */
user_id: string;
/**
 * User login name.
 */
user_login: string;
/**
 * Display name corresponding to `user_id`.
 */
user_name: string;
}
export type GetBitsLeaderboardResponse = DataListResponse<GetBitsLeaderboardResponseData>;
export interface GetCheermotesParams {
/**
 * ID for the broadcaster who might own specialized Cheermotes.
 */
broadcaster_id?: string;
}
export interface GetCheermotesResponseData {
/**
 * The string used to Cheer that precedes the Bits amount.
 */
prefix: string;
/**
 * An array of Cheermotes with their metadata.
 */
tiers: {
/**
 * Minimum number of bits needed to be used to hit the given tier of emote. 
 */
min_bits: number;
/**
 * ID of the emote tier. Possible tiers are: 1,100,500,1000,5000, 10k, or 100k.
 */
id: string;
/**
 * Hex code for the color associated with the bits of that tier. Grey, Purple, Teal, Blue, or Red color to match the base bit type.
 */
color: string;
/**
 * Structure containing both animated and static image sets, sorted by light and dark.
 */
images: Record<"dark" | "light", Record<"animated" | "static", Record<"1" | "1.5" | "2" | "3" | "4", string>>>;
/**
 * Indicates whether or not emote information is accessible to users.
 */
can_cheer: boolean;
/**
 * Indicates whether or not we hide the emote from the bits card.
 */
show_in_bits_card: boolean;};
/**
 * Shows whether the emote is `global_first_party`, `global_third_party`, `channel_custom`, `display_only`, or `sponsored`.
 */
type: string;
/**
 * Order of the emotes as shown in the bits card, in ascending order.
 */
order: number;
/**
 * The data when this Cheermote was last updated.
 */
last_updated: string;
/**
 * Indicates whether or not this emote provides a charity contribution match during charity campaigns.
 */
is_charitable: boolean;
}
export type GetCheermotesResponse = DataListResponse<GetCheermotesResponseData>;
export interface GetExtensionTransactionsParams {
/**
 * ID of the Extension to list transactions for.
 * 
 * Maximum: 1
 */
extension_id: string;
/**
 * Transaction IDs to look up. Can include multiple to fetch multiple transactions in a single request.
 * 
 * For example, `/helix/extensions/transactions?extension_id=1234&id=1&id=2&id=3`
 * 
 * Maximum: 100.
 */
id?: string | string[];
/**
 * The cursor used to fetch the next page of data. This only applies to queries without ID. If an ID is specified, it supersedes the cursor.
 */
after?: string;
/**
 * Maximum number of objects to return.
 * 
 * Maximum: 100. Default: 20.
 */
first?: number;
}
export interface GetExtensionTransactionsResponseData {
/**
 * Unique identifier of the Bits-in-Extensions transaction.
 */
id: string;
/**
 * UTC timestamp when this transaction occurred.
 */
timestamp: string;
/**
 * Twitch user ID of the channel the transaction occurred on.
 */
broadcaster_id: string;
/**
 * Login name of the broadcaster.
 */
broadcaster_login: string;
/**
 * Twitch display name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Twitch user ID of the user who generated the transaction.
 */
user_id: string;
/**
 * Login name of the user who generated the transaction.
 */
user_login: string;
/**
 * Twitch display name of the user who generated the transaction.
 */
user_name: string;
/**
 * Enum of the product type. Currently only `BITS_IN_EXTENSION`.
 */
product_type: string;
/**
 * Represents the product acquired, as it looked at the time of the transaction.
 */
product_data: {
/**
 * Set to twitch.ext + your Extension ID.
 */
domain: string;
/**
 * Unique identifier for the product across the Extension.
 */
sku: string;
/**
 * Represents the cost to acquire the product.
 */
cost: {
/**
 * Number of Bits required to acquire the product.
 */
amount: number;
/**
 * Identifies the contribution method. Currently only `bits`.
 */
type: string;};
/**
 * Indicates if the product is in development.
 */
inDevelopment: boolean;
/**
 * Display name of the product.
 */
displayName: string;};
/**
 * Always empty since only unexpired products can be purchased.
 */
expiration: string;
/**
 * Indicates whether or not the data was sent over the Extension PubSub to all instances of the Extension.
 */
broadcast: boolean;
}
export type GetExtensionTransactionsResponse = DataListResponse<GetExtensionTransactionsResponseData> & PaginatedCursorResponse;
export interface GetChannelInformationParams {
/**
 * The ID of the broadcaster whose channel you want to get. To specify more than one ID, include this parameter for each broadcaster you want to get. For example, `broadcaster_id=1234&broadcaster_id=5678`. You may specify a maximum of 100 IDs.
 */
broadcaster_id: string | string[];
}
export interface GetChannelInformationResponseData {
/**
 * Twitch User ID of this channel owner.
 */
broadcaster_id: string;
/**
 * Broadcaster’s user login name.
 */
broadcaster_login: string;
/**
 * Twitch user display name of this channel owner.
 */
broadcaster_name: string;
/**
 * Name of the game being played on the channel.
 */
game_name: string;
/**
 * Current game ID being played on the channel.
 */
game_id: string;
/**
 * Language of the channel. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
broadcaster_language: string;
/**
 * Title of the stream.
 */
title: string;
/**
 * Stream delay in seconds.
 */
delay: number;
}
export type GetChannelInformationResponse = DataListResponse<GetChannelInformationResponseData>;
export interface ModifyChannelInformationParams {
/**
 * ID of the channel to be updated
 */
broadcaster_id: string;
}
export interface ModifyChannelInformationBody {
/**
 * The current game ID being played on the channel. Use “0” or “” (an empty string) to unset the game.
 */
game_id?: string;
/**
 * The language of the channel. A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
broadcaster_language?: string;
/**
 * The title of the stream. Value must not be an empty string.
 */
title?: string;
/**
 * Stream delay in seconds. Stream delay is a Twitch Partner feature; trying to set this value for other account types will return a 400 error.
 */
delay?: number;
}
export interface GetChannelEditorsParams {
/**
 * Broadcaster’s user ID associated with the channel.
 */
broadcaster_id: string;
}
export interface GetChannelEditorsResponseData {
/**
 * User ID of the editor.
 */
user_id: string;
/**
 * Display name of the editor.
 */
user_name: string;
/**
 * Date and time the editor was given editor permissions.
 */
created_at: string;
}
export type GetChannelEditorsResponse = DataListResponse<GetChannelEditorsResponseData>;
export interface CreateCustomRewardsParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 */
broadcaster_id: string;
}
export interface CreateCustomRewardsBody {
/**
 * The title of the reward.
 */
title: string;
/**
 * The cost of the reward.
 */
cost: number;
/**
 * The prompt for the viewer when redeeming the reward.
 */
prompt?: string;
/**
 * Is the reward currently enabled, if false the reward won’t show up to viewers. Default: true
 */
is_enabled?: boolean;
/**
 * Custom background color for the reward. Format: Hex with # prefix. Example: `#00E5CB`.
 */
background_color?: string;
/**
 * Does the user need to enter information when redeeming the reward. Default: false.
 */
is_user_input_required?: boolean;
/**
 * Whether a maximum per stream is enabled. Default: false.
 */
is_max_per_stream_enabled?: boolean;
/**
 * The maximum number per stream if enabled. Required when any value of `is_max_per_stream_enabled` is included.
 */
max_per_stream?: number;
/**
 * Whether a maximum per user per stream is enabled. Default: false.
 */
is_max_per_user_per_stream_enabled?: boolean;
/**
 * The maximum number per user per stream if enabled. Required when any value of `is_max_per_user_per_stream_enabled` is included.
 */
max_per_user_per_stream?: number;
/**
 * Whether a cooldown is enabled. Default: false.
 */
is_global_cooldown_enabled?: boolean;
/**
 * The cooldown in seconds if enabled. Required when any value of `is_global_cooldown_enabled` is included.
 */
global_cooldown_seconds?: number;
/**
 * Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status. Default: false.
 */
should_redemptions_skip_request_queue?: boolean;
}
export interface CreateCustomRewardsResponseData {
/**
 * ID of the channel the reward is for.
 */
broadcaster_id: string;
/**
 * Broadcaster’s user login name.
 */
broadcaster_login: string;
/**
 * Display name of the channel the reward is for.
 */
broadcaster_name: string;
/**
 * ID of the reward.
 */
id: string;
/**
 * The title of the reward.
 */
title: string;
/**
 * The prompt for the viewer when they are redeeming the reward.
 */
prompt: string;
/**
 * The cost of the reward.
 */
cost: number;
/**
 * Set of custom images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }, can be null if no images have been uploaded
 */
image: Record<"url_1x" | "url_2x" | "url_4x", string> | null;
/**
 * Set of default images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }
 */
default_image: Record<"url_1x" | "url_2x" | "url_4x", string>;
/**
 * Custom background color for the reward. Format: Hex with # prefix. Example: `#00E5CB`.
 */
background_color: string;
/**
 * Is the reward currently enabled, if false the reward won’t show up to viewers
 */
is_enabled: boolean;
/**
 * Does the user need to enter information when redeeming the reward
 */
is_user_input_required: boolean;
/**
 * Whether a maximum per stream is enabled and what the maximum is. { is_enabled: bool, max_per_stream: int }
 */
max_per_stream_setting: { is_enabled: boolean; max_per_stream: number; };
/**
 * Whether a maximum per user per stream is enabled and what the maximum is. { is_enabled: bool, max_per_user_per_stream: int }
 */
max_per_user_per_stream_setting: { is_enabled: boolean; max_per_user_per_stream: number; };
/**
 * Whether a cooldown is enabled and what the cooldown is. { is_enabled: bool, global_cooldown_seconds: int }
 */
global_cooldown_setting: { is_enabled: boolean; global_cooldown_seconds: number; };
/**
 * Is the reward currently paused, if true viewers can’t redeem
 */
is_paused: boolean;
/**
 * Is the reward currently in stock, if false viewers can’t redeem
 */
is_in_stock: boolean;
/**
 * Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status.
 */
should_redemptions_skip_request_queue: boolean;
/**
 * The number of redemptions redeemed during the current live stream. Counts against the max_per_stream_setting limit. Null if the broadcasters stream isn’t live or max_per_stream_setting isn’t enabled.
 */
redemptions_redeemed_current_stream: number | null;
/**
 * Timestamp of the cooldown expiration. Null if the reward isn’t on cooldown.
 */
cooldown_expires_at: string | null;
}
export type CreateCustomRewardsResponse = DataListResponse<CreateCustomRewardsResponseData>;
export interface DeleteCustomRewardParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 */
broadcaster_id: string;
/**
 * ID of the Custom Reward to delete, must match a Custom Reward on `broadcaster_id`’s channel.
 */
id: string;
}
export interface GetCustomRewardParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 */
broadcaster_id: string;
/**
 * When used, this parameter filters the results and only returns reward objects for the Custom Rewards with matching ID. Maximum: 50
 */
id?: string | string[];
/**
 * When set to true, only returns custom rewards that the calling `client_id` can manage. Default: false.
 */
only_manageable_rewards?: boolean;
}
export interface GetCustomRewardResponseData {
/**
 * ID of the channel the reward is for.
 */
broadcaster_id: string;
/**
 * Login of the channel the reward is for.
 */
broadcaster_login: string;
/**
 * Display name of the channel the reward is for.
 */
broadcaster_name: string;
/**
 * ID of the reward.
 */
id: string;
/**
 * The title of the reward.
 */
title: string;
/**
 * The prompt for the viewer when redeeming the reward.
 */
prompt: string;
/**
 * The cost of the reward.
 */
cost: number;
/**
 * Set of custom images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }, can be null if no images have been uploaded.
 */
image: Record<"url_1x" | "url_2x" | "url_4x", string> | null;
/**
 * Set of default images of 1x, 2x and 4x sizes for the reward { url_1x: string, url_2x: string, url_4x: string }
 */
default_image: Record<"url_1x" | "url_2x" | "url_4x", string>;
/**
 * Custom background color for the reward. Format: Hex with # prefix. Example: `#00E5CB`.
 */
background_color: string;
/**
 * Is the reward currently enabled, if false the reward won’t show up to viewers.
 */
is_enabled: boolean;
/**
 * Does the user need to enter information when redeeming the reward
 */
is_user_input_required: boolean;
/**
 * Whether a maximum per stream is enabled and what the maximum is. { is_enabled: bool, max_per_stream: int }
 */
max_per_stream_setting: { is_enabled: boolean; max_per_stream: number; };
/**
 * Whether a maximum per user per stream is enabled and what the maximum is. { is_enabled: bool, max_per_user_per_stream: int }
 */
max_per_user_per_stream_setting: { is_enabled: boolean; max_per_user_per_stream: number; };
/**
 * Whether a cooldown is enabled and what the cooldown is. { is_enabled: bool, global_cooldown_seconds: int }
 */
global_cooldown_setting: { is_enabled: boolean; global_cooldown_seconds: number; };
/**
 * Is the reward currently paused, if true viewers can’t redeem.
 */
is_paused: boolean;
/**
 * Is the reward currently in stock, if false viewers can’t redeem.
 */
is_in_stock: boolean;
/**
 * Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status.
 */
should_redemptions_skip_request_queue: boolean;
/**
 * The number of redemptions redeemed during the current live stream. Counts against the max_per_stream_setting limit. Null if the broadcasters stream isn’t live or max_per_stream_setting isn’t enabled.
 */
redemptions_redeemed_current_stream: number | null;
/**
 * Timestamp of the cooldown expiration. Null if the reward isn’t on cooldown.
 */
cooldown_expires_at: string | null;
}
export type GetCustomRewardResponse = DataListResponse<GetCustomRewardResponseData>;
export interface GetCustomRewardRedemptionParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 */
broadcaster_id: string;
/**
 * When ID is not provided, this parameter returns paginated Custom Reward Redemption objects for redemptions of the Custom Reward with ID `reward_id`.
 */
reward_id: string;
/**
 * When used, this param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID. Maximum: 50
 */
id?: string | string[];
/**
 * When id is not provided, this param is required and filters the paginated Custom Reward Redemption objects for redemptions with the matching status. Can be one of UNFULFILLED, FULFILLED or CANCELED
 */
status?: string;
/**
 * Sort order of redemptions returned when getting the paginated Custom Reward Redemption objects for a reward. One of: OLDEST, NEWEST. Default: OLDEST.
 */
sort?: string;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries without ID. If an ID is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the pagination response field of a prior query.
 */
after?: string;
/**
 * Number of results to be returned when getting the paginated Custom Reward Redemption objects for a reward. Limit: 50. Default: 20.
 */
first?: number;
}
export interface GetCustomRewardRedemptionResponseData {
/**
 * The id of the broadcaster that the reward belongs to.
 */
broadcaster_id: string;
/**
 * Broadcaster’s user login name.
 */
broadcaster_login: string;
/**
 * The display name of the broadcaster that the reward belongs to.
 */
broadcaster_name: string;
/**
 * The ID of the redemption.
 */
id: string;
/**
 * The login of the user who redeemed the reward.
 */
user_login: string;
/**
 * The ID of the user that redeemed the reward.
 */
user_id: string;
/**
 * The display name of the user that redeemed the reward.
 */
user_name: string;
/**
 * Basic information about the Custom Reward that was redeemed at the time it was redeemed. { “id”: string, “title”: string, “prompt”: string, “cost”: int, }
 */
reward: { id: string; title: string; prompt: string; cost: number; };
/**
 * The user input provided. Empty string if not provided.
 */
user_input: string;
/**
 * One of UNFULFILLED, FULFILLED or CANCELED
 */
status: string;
/**
 * RFC3339 timestamp of when the reward was redeemed.
 */
redeemed_at: string;
}
export type GetCustomRewardRedemptionResponse = DataListResponse<GetCustomRewardRedemptionResponseData> & PaginatedCursorResponse;
export interface UpdateCustomRewardParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 */
broadcaster_id: string;
/**
 * ID of the Custom Reward to update. Must match a Custom Reward on the channel of the `broadcaster_id`.
 */
id: string;
}
export interface UpdateCustomRewardBody {
/**
 * The title of the reward.
 */
title?: string;
/**
 * The prompt for the viewer when they are redeeming the reward.
 */
prompt?: string;
/**
 * The cost of the reward.
 */
cost?: number;
/**
 * Custom background color for the reward as a hexadecimal value. Example: `#00E5CB`.
 */
background_color?: string;
/**
 * Is the reward currently enabled, if false the reward won’t show up to viewers.
 */
is_enabled?: boolean;
/**
 * Does the user need to enter information when redeeming the reward.
 */
is_user_input_required?: boolean;
/**
 * Whether a maximum per stream is enabled. Required when any value of `max_per_stream` is included.
 */
is_max_per_stream_enabled?: boolean;
/**
 * The maximum number per stream if enabled. Required when any value of `is_max_per_stream_enabled` is included.
 */
max_per_stream?: number;
/**
 * Whether a maximum per user per stream is enabled. Required when any value of `max_per_user_per_stream` is included.
 */
is_max_per_user_per_stream_enabled?: boolean;
/**
 * The maximum number per user per stream if enabled. Required when any value of `is_max_per_user_per_stream_enabled` is included.
 */
max_per_user_per_stream?: number;
/**
 * Whether a cooldown is enabled. Required when any value of `global_cooldown_seconds` is included.
 */
is_global_cooldown_enabled?: boolean;
/**
 * The cooldown in seconds if enabled. Required when any value of `is_global_cooldown_enabled` is included.
 */
global_cooldown_seconds?: number;
/**
 * Is the reward currently paused, if true viewers cannot redeem.
 */
is_paused?: boolean;
/**
 * Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status.
 */
should_redemptions_skip_request_queue?: boolean;
}
export interface UpdateCustomRewardResponseData {
/**
 * ID of the channel the reward is for.
 */
broadcaster_id: string;
/**
 * Broadcaster’s user login name.
 */
broadcaster_login: string;
/**
 * Display name of the channel the reward is for.
 */
broadcaster_name: string;
/**
 * ID of the reward.
 */
id: string;
/**
 * The title of the reward.
 */
title: string;
/**
 * The prompt for the viewer when they are redeeming the reward.
 */
prompt: string;
/**
 * The cost of the reward.
 */
cost: number;
/**
 * Set of custom images of 1x, 2x, and 4x sizes for the reward, can be null if no images have been uploaded.
 */
image: Record<"url_1x" | "url_2x" | "url_4x", string> | null;
/**
 * Set of default images of 1x, 2x, and 4x sizes for the reward.
 */
default_image: Record<"url_1x" | "url_2x" | "url_4x", string>;
/**
 * Custom background color for the reward as a hexadecimal value. Example: `#00E5CB`.
 */
background_color: string;
/**
 * Is the reward currently enabled, if false the reward won’t show up to viewers.
 */
is_enabled: boolean;
/**
 * Does the user need to enter information when redeeming the reward.
 */
is_user_input_required: boolean;
/**
 * Whether a maximum per stream is enabled and what the maximum is.
 */
max_per_stream_setting: { is_enabled: boolean; max_per_stream: number; };
/**
 * Whether a maximum per user per stream is enabled and what the maximum is.
 */
max_per_user_per_stream_setting: { is_enabled: boolean; max_per_user_per_stream: number; };
/**
 * Whether a cooldown is enabled and what the cooldown is.
 */
global_cooldown_setting: { is_enabled: boolean; global_cooldown_seconds: number; };
/**
 * Is the reward currently paused, if true viewers cannot redeem.
 */
is_paused: boolean;
/**
 * Is the reward currently in stock, if false viewers can’t redeem.
 */
is_in_stock: boolean;
/**
 * Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status.
 */
should_redemptions_skip_request_queue: boolean;
/**
 * The number of redemptions redeemed during the current live stream. Counts against the max_per_stream_setting limit. `null` if the broadcasters stream is not live or max_per_stream_setting is not enabled.
 */
redemptions_redeemed_current_stream: number | null;
/**
 * Timestamp of the cooldown expiration. `null` if the reward is not on cooldown.
 */
cooldown_expires_at: string | null;
}
export type UpdateCustomRewardResponse = DataListResponse<UpdateCustomRewardResponseData>;
export interface UpdateRedemptionStatusParams {
/**
 * ID of the Custom Reward Redemption to update, must match a Custom Reward Redemption on `broadcaster_id`’s channel. Maximum: 50.
 */
id: string | string[];
/**
 * Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 */
broadcaster_id: string;
/**
 * ID of the Custom Reward the redemptions to be updated are for.
 */
reward_id: string;
}
export interface UpdateRedemptionStatusBody {
/**
 * The new status to set redemptions to. Can be either FULFILLED or CANCELED. Updating to CANCELED will refund the user their Channel Points.
 */
status: string;
}
export interface UpdateRedemptionStatusResponseData {
/**
 * The ID of the broadcaster that the reward belongs to.
 */
broadcaster_id: string;
/**
 * Broadcaster’s user login name.
 */
broadcaster_login: string;
/**
 * The display name of the broadcaster that the reward belongs to.
 */
broadcaster_name: string;
/**
 * The ID of the redemption.
 */
id: string;
/**
 * The ID of the user that redeemed the reward.
 */
user_id: string;
/**
 * The display name of the user that redeemed the reward.
 */
user_name: string;
/**
 * The login of the user that redeemed the reward.
 */
user_login: string;
/**
 * Basic information about the Custom Reward that was redeemed at the time it was redeemed. { “id”: string, “title”: string, “prompt”: string, “cost”: int, }
 */
reward: { id: string; title: string; prompt: string; cost: number; };
/**
 * The user input provided. Null if not provided.
 */
user_input: string | null;
/**
 * One of UNFULFILLED, FULFILLED or CANCELED.
 */
status: string;
/**
 * RFC3339 timestamp of when the reward was redeemed.
 */
redeemed_at: string;
}
export type UpdateRedemptionStatusResponse = DataListResponse<UpdateRedemptionStatusResponseData>;
export interface GetChannelEmotesParams {
/**
 * An ID that identifies the broadcaster to get the emotes from.
 */
broadcaster_id: string;
}
export interface GetChannelEmotesResponseData {
/**
 * An ID that identifies the emote.
 */
id: string;
/**
 * The name of the emote. This is the name that viewers type in the chat window to get the emote to appear.
 */
name: string;
/**
 * Contains the image URLs for the emote. These image URLs will always provide a static (i.e., non-animated) emote image with a light background. NOTE: The preference is for you to use the templated URL in the `template` field to fetch the image instead of using these URLs.
 */
images: {
/**
 * A URL to the small version (28px x 28px) of the emote.
 */
url_1x: string;
/**
 * A URL to the medium version (56px x 56px) of the emote.
 */
url_2x: string;
/**
 * A URL to the large version (112px x 112px) of the emote.
 */
url_4x: string;};
/**
 * The subscriber tier at which the emote is unlocked. This field contains the tier information only if `emote_type` is set to `subscriptions`, otherwise, it’s an empty string.
 */
tier: string;
/**
 * The type of emote. The possible values are: 
 * - bitstier — Indicates a custom Bits tier emote.
 * - follower — Indicates a custom follower emote.
 * - subscriptions — Indicates a custom subscriber emote.
 */
emote_type: string;
/**
 * An ID that identifies the emote set that the emote belongs to.
 */
emote_set_id: string;
/**
 * The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only `static`. But if it’s available as a static PNG and an animated GIF, the array contains `static` and `animated`. The possible formats are: 
 * - animated — Indicates an animated GIF is available for this emote.
 * - static — Indicates a static PNG file is available for this emote.
 */
format: string[];
/**
 * The sizes that the emote is available in. For example, if the emote is available in small and medium sizes, the array contains 1.0 and 2.0. Possible sizes are: 
 * - 1.0 — A small version (28px x 28px) is available.
 * - 2.0 — A medium version (56px x 56px) is available.
 * - 3.0 — A large version (112px x 112px) is available.
 */
scale: string[];
/**
 * The background themes that the emote is available in. Possible themes are: 
 * - dark
 * - light
 */
theme_mode: string[];
}
export interface GetChannelEmotesResponse extends DataListResponse<GetChannelEmotesResponseData> {
/**
 * A templated URL. Use the values from `id`, `format`, `scale`, and `theme_mode` to replace the like-named placeholder strings in the templated URL to create a CDN (content delivery network) URL that you use to fetch the emote. For information about what the template looks like and how to use it to fetch emotes, see Emote CDN URL format.
 */
template: string;
}
export interface GetGlobalEmotesResponseData {
/**
 * An ID that identifies the emote.
 */
id: string;
/**
 * The name of the emote. This is the name that viewers type in the chat window to get the emote to appear.
 */
name: string;
/**
 * Contains the image URLs for the emote. These image URLs will always provide a static (i.e., non-animated) emote image with a light background. NOTE: The preference is for you to use the templated URL in the `template` field to fetch the image instead of using these URLs.
 */
images: {
/**
 * A URL to the small version (28px x 28px) of the emote.
 */
url_1x: string;
/**
 * A URL to the medium version (56px x 56px) of the emote.
 */
url_2x: string;
/**
 * A URL to the large version (112px x 112px) of the emote.
 */
url_4x: string;};
/**
 * The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only `static`. But if it’s available as a static PNG and an animated GIF, the array contains `static` and `animated`. The possible formats are: 
 * - animated — Indicates an animated GIF is available for this emote.
 * - static — Indicates a static PNG file is available for this emote.
 */
format: string[];
/**
 * The sizes that the emote is available in. For example, if the emote is available in small and medium sizes, the array contains 1.0 and 2.0. Possible sizes are: 
 * - 1.0 — A small version (28px x 28px) is available.
 * - 2.0 — A medium version (56px x 56px) is available.
 * - 3.0 — A large version (112px x 112px) is available.
 */
scale: string[];
/**
 * The background themes that the emote is available in. Possible themes are: 
 * - dark
 * - light
 */
theme_mode: string[];
}
export interface GetGlobalEmotesResponse extends DataListResponse<GetGlobalEmotesResponseData> {
/**
 * A templated URL. Use the values from `id`, `format`, `scale`, and `theme_mode` to replace the like-named placeholder strings in the templated URL to create a CDN (content delivery network) URL that you use to fetch the emote. For information about what the template looks like and how to use it to fetch emotes, see Emote CDN URL format.
 */
template: string;
}
export interface GetEmoteSetsParams {
/**
 * An ID that identifies the emote set. Include the parameter for each emote set you want to get. For example, `emote_set_id=1234&emote_set_id=5678`. You may specify a maximum of 25 IDs.
 */
emote_set_id: string | string[];
}
export interface GetEmoteSetsResponseData {
/**
 * An ID that identifies the emote.
 */
id: string;
/**
 * The name of the emote. This is the name that viewers type in the chat window to get the emote to appear.
 */
name: string;
/**
 * Contains the image URLs for the emote. These image URLs will always provide a static (i.e., non-animated) emote image with a light background. NOTE: The preference is for you to use the templated URL in the `template` field to fetch the image instead of using these URLs.
 */
images: {
/**
 * A URL to the small version (28px x 28px) of the emote.
 */
url_1x: string;
/**
 * A URL to the medium version (56px x 56px) of the emote.
 */
url_2x: string;
/**
 * A URL to the large version (112px x 112px) of the emote.
 */
url_4x: string;};
/**
 * The type of emote. The possible values are: 
 * - bitstier — Indicates a Bits tier emote.
 * - follower — Indicates a follower emote.
 * - subscriptions — Indicates a subscriber emote.
 */
emote_type: string;
/**
 * An ID that identifies the emote set that the emote belongs to.
 */
emote_set_id: string;
/**
 * The ID of the broadcaster who owns the emote.
 */
owner_id: string;
/**
 * The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only `static`. But if it’s available as a static PNG and an animated GIF, the array contains `static` and `animated`. The possible formats are: 
 * - animated — Indicates an animated GIF is available for this emote.
 * - static — Indicates a static PNG file is available for this emote.
 */
format: string[];
/**
 * The sizes that the emote is available in. For example, if the emote is available in small and medium sizes, the array contains 1.0 and 2.0. Possible sizes are: 
 * - 1.0 — A small version (28px x 28px) is available.
 * - 2.0 — A medium version (56px x 56px) is available.
 * - 3.0 — A large version (112px x 112px) is available.
 */
scale: string[];
/**
 * The background themes that the emote is available in. Possible themes are: 
 * - dark
 * - light
 */
theme_mode: string[];
}
export interface GetEmoteSetsResponse extends DataListResponse<GetEmoteSetsResponseData> {
/**
 * A templated URL. Use the values from `id`, `format`, `scale`, and `theme_mode` to replace the like-named placeholder strings in the templated URL to create a CDN (content delivery network) URL that you use to fetch the emote. For information about what the template looks like and how to use it to fetch emotes, see Emote CDN URL format.
 */
template: string;
}
export interface GetChannelChatBadgesParams {
/**
 * The broadcaster whose chat badges are being requested. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
}
export interface GetChannelChatBadgesResponseData {
/**
 * ID for the chat badge set.
 */
set_id: string;
/**
 * Contains chat badge objects for the set.
 */
versions: Array<{
/**
 * ID of the chat badge version.
 */
id: string;
/**
 * Small image URL.
 */
image_url_1x: string;
/**
 * Medium image URL.
 */
image_url_2x: string;
/**
 * Large image URL.
 */
image_url_4x: string;}>;
}
export type GetChannelChatBadgesResponse = DataListResponse<GetChannelChatBadgesResponseData>;
export interface GetGlobalChatBadgesResponseData {
/**
 * ID for the chat badge set.
 */
set_id: string;
/**
 * Contains chat badge objects for the set.
 */
versions: Array<{
/**
 * ID of the chat badge version.
 */
id: string;
/**
 * Small image URL.
 */
image_url_1x: string;
/**
 * Medium image URL.
 */
image_url_2x: string;
/**
 * Large image URL.
 */
image_url_4x: string;}>;
}
export type GetGlobalChatBadgesResponse = DataListResponse<GetGlobalChatBadgesResponseData>;
export interface GetChatSettingsParams {
/**
 * The ID of the broadcaster whose chat settings you want to get.
 */
broadcaster_id: string;
/**
 * Required only to access the `non_moderator_chat_delay` or `non_moderator_chat_delay_duration` settings.
 * 
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to get their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id?: string;
}
export interface GetChatSettingsResponseData {
/**
 * The ID of the broadcaster specified in the request.
 */
broadcaster_id: string;
/**
 * A Boolean value that determines whether chat messages must contain only emotes. Is true, if only messages that are 100% emotes are allowed; otherwise, false.
 */
emote_mode: boolean;
/**
 * A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed.
 * 
 * Is true, if the broadcaster restricts the chat room to followers only; otherwise, false.
 * 
 * See `follower_mode_duration` for how long the followers must have followed the broadcaster to participate in the chat room.
 */
follower_mode: boolean;
/**
 * The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room. See `follower_mode`.
 * 
 * Is null if `follower_mode` is false.
 */
follower_mode_duration: number | null;
/**
 * The moderator’s ID. The response includes this field only if the request specifies a User access token that includes the  moderator:read:chat_settings scope.
 */
moderator_id: string;
/**
 * A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room. This gives chat moderators and bots a chance to remove them before viewers can see the message.
 * 
 * Is true, if the broadcaster applies a delay; otherwise, false.
 * 
 * See `non_moderator_chat_delay_duration` for the length of the delay.
 * 
 * The response includes this field only if the request specifies a User access token that includes the  moderator:read:chat_settings scope.
 */
non_moderator_chat_delay: boolean;
/**
 * The amount of time, in seconds, that messages are delayed from appearing in chat. See `non_moderator_chat_delay`.
 * 
 * Is null if non_moderator_chat_delay is false.
 * 
 * The response includes this field only if the request specifies a User access token that includes the  moderator:read:chat_settings scope.
 */
non_moderator_chat_delay_duration: number | null;
/**
 * A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages.
 * 
 * Is true, if the broadcaster applies a delay; otherwise, false.
 * 
 * See `slow_mode_wait_time` for the delay.
 */
slow_mode: boolean;
/**
 * The amount of time, in seconds, that users need to wait between sending messages. See `slow_mode`.
 * 
 * Is null if slow_mode is false.
 */
slow_mode_wait_time: number | null;
/**
 * A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room.
 * 
 * Is true, if the broadcaster restricts the chat room to subscribers only; otherwise, false.
 */
subscriber_mode: boolean;
/**
 * A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room.
 * 
 * Is true, if the broadcaster requires unique messages only; otherwise, false.
 */
unique_chat_mode: boolean;
}
export type GetChatSettingsResponse = DataListResponse<GetChatSettingsResponseData>;
export interface UpdateChatSettingsParams {
/**
 * The ID of the broadcaster whose chat settings you want to update. This ID must match the user ID associated with the user OAuth token.
 */
broadcaster_id: string;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to update their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
}
export interface UpdateChatSettingsBody {
/**
 * A Boolean value that determines whether chat messages must contain only emotes.
 * 
 * Set to true, if only messages that are 100% emotes are allowed; otherwise, false. Default is false.
 */
emote_mode?: boolean;
/**
 * A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed.
 * 
 * Set to true, if the broadcaster restricts the chat room to followers only; otherwise, false. Default is true.
 * 
 * See `follower_mode_duration` for how long the followers must have followed the broadcaster to participate in the chat room.
 */
follower_mode?: boolean;
/**
 * The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room (see `follower_mode`).
 * 
 * You may specify a value in the range: 0 (no restriction) through 129600 (3 months). The default is 0.
 */
follower_mode_duration?: number;
/**
 * A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room. This gives chat moderators and bots a chance to remove them before viewers can see the message.
 * 
 * Set to true, if the broadcaster applies a delay; otherwise, false. Default is false.
 * 
 * See `non_moderator_chat_delay_duration` for the length of the delay.
 */
non_moderator_chat_delay?: boolean;
/**
 * The amount of time, in seconds, that messages are delayed from appearing in chat.
 * 
 * Possible values are:
 * - 2  —  2 second delay (recommended)
 * - 4  —  4 second delay
 * - 6  —  6 second delaySee `non_moderator_chat_delay`.
 */
non_moderator_chat_delay_duration?: number;
/**
 * A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages.
 * 
 * Set to true, if the broadcaster applies a wait period messages; otherwise, false. Default is false.
 * 
 * See `slow_mode_wait_time` for the delay.
 */
slow_mode?: boolean;
/**
 * The amount of time, in seconds, that users need to wait between sending messages (see `slow_mode`).
 * 
 * You may specify a value in the range: 3 (3 second delay) through 120 (2 minute delay). The default is 30 seconds.
 */
slow_mode_wait_time?: number;
/**
 * A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room.
 * 
 * Set to true, if the broadcaster restricts the chat room to subscribers only; otherwise, false. Default is false.
 */
subscriber_mode?: boolean;
/**
 * A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room.
 * 
 * Set to true, if the broadcaster requires unique messages only; otherwise, false. Default is false.
 */
unique_chat_mode?: boolean;
}
export interface UpdateChatSettingsResponseData {
/**
 * The ID of the broadcaster specified in the request.
 */
broadcaster_id: string;
/**
 * A Boolean value that determines whether chat messages must contain only emotes. Is true, if only messages that are 100% emotes are allowed; otherwise, false.
 */
emote_mode: boolean;
/**
 * A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed.
 * 
 * Is true, if the broadcaster restricts the chat room to followers only; otherwise, false.
 * 
 * See `follower_mode_duration` for how long the followers must have followed the broadcaster to participate in the chat room.
 */
follower_mode: boolean;
/**
 * The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room. See `follower_mode`.
 * 
 * Is null if `follower_mode` is false.
 */
follower_mode_duration: number | null;
/**
 * The ID of the moderator specified in the request.
 */
moderator_id: string;
/**
 * A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room. This gives chat moderators and bots a chance to remove them before viewers can see the message.
 * 
 * Is true, if the broadcaster applies a delay; otherwise, false.
 * 
 * See `non_moderator_chat_delay_duration` for the length of the delay.
 */
non_moderator_chat_delay: boolean;
/**
 * The amount of time, in seconds, that messages are delayed from appearing in chat. See `non_moderator_chat_delay`.
 * 
 * Is null if non_moderator_chat_delay is false.
 */
non_moderator_chat_delay_duration: number | null;
/**
 * A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages.
 * 
 * Is true, if the broadcaster applies a delay; otherwise, false.
 * 
 * See `slow_mode_wait_time` for the delay.
 */
slow_mode: boolean;
/**
 * The amount of time, in seconds, that users need to wait between sending messages. See `slow_mode`.
 * 
 * Is null if slow_mode is false.
 */
slow_mode_wait_time: number | null;
/**
 * A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room.
 * 
 * Is true, if the broadcaster restricts the chat room to subscribers only; otherwise, false.
 */
subscriber_mode: boolean;
/**
 * A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room.
 * 
 * Is true, if the broadcaster requires unique messages only; otherwise, false.
 */
unique_chat_mode: boolean;
}
export type UpdateChatSettingsResponse = DataListResponse<UpdateChatSettingsResponseData>;
export interface CreateClipParams {
/**
 * ID of the stream from which the clip will be made.
 */
broadcaster_id: string;
/**
 * If `false`, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream). Default: `false`.
 */
has_delay?: boolean;
}
export interface CreateClipResponseData {
/**
 * URL of the edit page for the clip.
 */
edit_url: string;
/**
 * ID of the clip that was created.
 */
id: string;
}
export type CreateClipResponse = DataListResponse<CreateClipResponseData>;
export interface GetClipsParams {
/**
 * ID of the broadcaster for whom clips are returned. The number of clips returned is determined by the `first` query-string parameter (default: 20). Results are ordered by view count.
 */
broadcaster_id: string;
/**
 * ID of the game for which clips are returned. The number of clips returned is determined by the `first` query-string parameter (default: 20). Results are ordered by view count.
 */
game_id: string;
/**
 * ID of the clip being queried. Limit: 100.
 */
id: string | string[];
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries specifying `broadcaster_id` or `game_id`. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. This applies only to queries specifying `broadcaster_id` or `game_id`. The cursor value specified here is from the `pagination` response field of a prior query.
 */
before?: string;
/**
 * Ending date/time for returned clips, in RFC3339 format. (Note that the seconds value is ignored.) If this is specified, `started_at` also must be specified; otherwise, the time period is ignored.
 */
ended_at?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: number;
/**
 * Starting date/time for returned clips, in RFC3339 format. (The seconds value is ignored.) If this is specified, `ended_at` also should be specified; otherwise, the `ended_at` date/time will be 1 week after the `started_at` value.
 */
started_at?: string;
}
export interface GetClipsResponseData {
/**
 * ID of the clip being queried.
 */
id: string;
/**
 * URL where the clip can be viewed.
 */
url: string;
/**
 * URL to embed the clip.
 */
embed_url: string;
/**
 * User ID of the stream from which the clip was created.
 */
broadcaster_id: string;
/**
 * Display name corresponding to `broadcaster_id`.
 */
broadcaster_name: string;
/**
 * ID of the user who created the clip.
 */
creator_id: string;
/**
 * Display name corresponding to `creator_id`.
 */
creator_name: string;
/**
 * ID of the video from which the clip was created.
 */
video_id: string;
/**
 * ID of the game assigned to the stream when the clip was created.
 */
game_id: string;
/**
 * Language of the stream from which the clip was created. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
language: string;
/**
 * Title of the clip.
 */
title: string;
/**
 * Number of times the clip has been viewed.
 */
view_count: number;
/**
 * Date when the clip was created.
 */
created_at: string;
/**
 * URL of the clip thumbnail.
 */
thumbnail_url: string;
/**
 * Duration of the Clip in seconds (up to 0.1 precision).
 */
duration: number;
}
export type GetClipsResponse = DataListResponse<GetClipsResponseData> & PaginatedCursorResponse;
export interface GetDropsEntitlementsParams {
/**
 * Unique identifier of the entitlement.
 */
id?: string;
/**
 * A Twitch user ID.
 */
user_id?: string;
/**
 * A Twitch game ID.
 */
game_id?: string;
/**
 * An optional fulfillment status used to filter entitlements. Valid values are `"CLAIMED"` or `"FULFILLED"`.
 */
fulfillment_status?: string;
/**
 * The cursor used to fetch the next page of data.
 */
after?: string;
/**
 * Maximum number of entitlements to return.
 * 
 * Default: 20
 * Max: 1000
 */
first?: number;
}
export interface GetDropsEntitlementsResponseData {
/**
 * Unique identifier of the entitlement.
 */
id: string;
/**
 * Identifier of the benefit.
 */
benefit_id: string;
/**
 * UTC timestamp in ISO format when this entitlement was granted on Twitch.
 */
timestamp: string;
/**
 * Twitch user ID of the user who was granted the entitlement.
 */
user_id: string;
/**
 * Twitch game ID of the game that was being played when this benefit was entitled.
 */
game_id: string;
/**
 * The fulfillment status of the entitlement as determined by the game developer. Valid values are `"CLAIMED"` or `"FULFILLED"`.
 */
fulfillment_status: string;
/**
 * UTC timestamp in ISO format for when this entitlement was last updated.
 */
updated_at: string;
}
export type GetDropsEntitlementsResponse = DataListResponse<GetDropsEntitlementsResponseData> & PaginatedCursorResponse;
export interface UpdateDropsEntitlementsParams {
/**
 * An array of unique identifiers of the entitlements to update.
 * 
 * Maximum: 100.
 */
entitlement_ids?: string[];
/**
 * A fulfillment status. Valid values are `"CLAIMED"` or `"FULFILLED"`.
 */
fulfillment_status?: string;
}
export interface UpdateDropsEntitlementsResponseData {
/**
 * Status code applied to a set of entitlements for the update operation that can be used to indicate partial success. Valid values are:
 * 
 * `SUCCESS`: Entitlement was successfully updated.
 * 
 * `INVALID_ID`: Invalid format for entitlement ID.
 * 
 * `NOT_FOUND`: Entitlement ID does not exist.
 * 
 * `UNAUTHORIZED`: Entitlement is not owned by the organization or the user when called with a user OAuth token.
 * 
 * `UPDATE_FAILED`: Indicates the entitlement update operation failed. Errors in the this state are expected to be be transient and should be retried later.
 */
status: string;
/**
 * Array of unique identifiers of the entitlements for the specified status.
 */
ids: string[];
}
export type UpdateDropsEntitlementsResponse = DataListResponse<UpdateDropsEntitlementsResponseData>;
export interface RedeemCodeParams {
/**
 * The redemption code to redeem. To redeem multiple codes, include this parameter for each redemption code. For example, `code=1234&code=5678`. You may specify a maximum of 20 codes.
 */
code?: string | string[];
/**
 * The ID of the user that owns the redemption code to redeem.
 */
user_id?: number;
}
export interface RedeemCodeResponseData {
/**
 * The redemption code.
 */
code: string;
/**
 * The redemption code’s status. Possible values are:
 * - ALREADY_CLAIMED — The code has already been claimed. All codes are single-use.
 * - EXPIRED — The code has expired and can no longer be claimed.
 * - INACTIVE — The code has not been activated.
 * - INCORRECT_FORMAT — The code is not properly formatted.
 * - INTERNAL_ERROR — An internal or unknown error occurred when accessing the code.
 * - NOT_FOUND — The code was not found.
 * - SUCCESSFULLY_REDEEMED — Successfully redeemed the code and credited the user's account with the entitlement.
 * - UNUSED — The code has not been claimed.
 * - USER_NOT_ELIGIBLE — The user is not eligible to redeem this code.
 */
status: string;
}
export type RedeemCodeResponse = DataListResponse<RedeemCodeResponseData>;
export interface GetExtensionConfigurationSegmentParams {
/**
 * The ID of the broadcaster for the configuration returned. This parameter is required if you set the `segment` parameter to broadcaster or developer. Do not specify this parameter if you set `segment` to global.
 */
broadcaster_id: string;
/**
 * The ID of the extension that contains the configuration segment you want to get.
 */
extension_id: string;
/**
 * The type of configuration segment to get. Valid values are: 
 * - broadcaster
 * - developer
 * - globalYou may specify one or more segments. To specify multiple segments, include the `segment` parameter for each segment to get. For example, `segment=broadcaster&segment=developer`.
 */
segment: string;
}
export interface GetExtensionConfigurationSegmentResponseData {
/**
 * The type of segment. Possible values are: 
 * - broadcaster
 * - developer
 * - global
 */
segment: string;
/**
 * The ID of the broadcaster that owns the extension. The object includes this field only if the `segment` query parameter is set to developer or broadcaster.
 */
broadcaster_id: string;
/**
 * The contents of the segment. This string may be a plain string or a string-encoded JSON object.
 */
content: string;
/**
 * The version that identifies the segment’s definition.
 */
version: string;
}
export type GetExtensionConfigurationSegmentResponse = DataListResponse<GetExtensionConfigurationSegmentResponseData>;
export interface SetExtensionConfigurationSegmentBody {
/**
 * ID for the Extension which the configuration is for.
 */
extension_id: string;
/**
 * Configuration type. Valid values are `"global"`, `"developer"`, or `"broadcaster"`.
 */
segment: string;
/**
 * User ID of the broadcaster. Required if the segment type is `"developer"` or `"broadcaster"`.
 */
broadcaster_id?: string;
/**
 * Configuration in a string-encoded format.
 */
content?: string;
/**
 * Configuration version with the segment type.
 */
version?: string;
}
export interface SetExtensionRequiredConfigurationParams {
/**
 * User ID of the broadcaster who has activated the specified Extension on their channel.
 */
broadcaster_id: string;
}
export interface SetExtensionRequiredConfigurationBody {
/**
 * ID for the Extension to activate.
 */
extension_id: string;
/**
 * The version fo the Extension to release.
 */
extension_version: string;
/**
 * The version of the configuration to use with the Extension.
 */
configuration_version: string;
}
export interface SendExtensionPubsubMessageBody {
/**
 * Array of strings for valid PubSub targets. Valid values: `"broadcast"`, `"global"`, `"whisper-<user-id>"`
 */
target: string[];
/**
 * ID of the broadcaster receiving the payload. This is not required if `is_global_broadcast` is set to `true`.
 */
broadcaster_id: string;
/**
 * Indicates if the message should be sent to all channels where your Extension is active.
 * 
 * Default: `false`.
 */
is_global_broadcast: boolean;
/**
 * String-encoded JSON message to be sent.
 */
message: string;
}
export interface GetExtensionLiveChannelsParams {
/**
 * ID of the Extension to search for.
 */
extension_id: string;
/**
 * Maximum number of objects to return.
 * 
 * Maximum: 100. Default: 20.
 */
first?: number;
/**
 * The cursor used to fetch the next page of data.
 */
after?: string;
}
export interface GetExtensionLiveChannelsResponseData {
/**
 * Title of the stream.
 */
title: string;
/**
 * User ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Broadcaster’s display name.
 */
broadcaster_name: string;
/**
 * Name of the game being played.
 */
game_name: string;
/**
 * ID of the game being played.
 */
game_id: string;
}
export type GetExtensionLiveChannelsResponse = DataListResponse<GetExtensionLiveChannelsResponseData> & PaginatedFlatResponse;
export interface GetExtensionSecretsResponseData {
/**
 * Indicates the version associated with the Extension secrets in the response.
 */
format_version: number;
/**
 * Array of secret objects.
 */
secrets: {
/**
 * Raw secret that should be used with JWT encoding.
 */
content: string;
/**
 * The earliest possible time this secret is valid to sign a JWT in RFC 3339 format.
 */
active: string;
/**
 * The latest possible time this secret may be used to decode a JWT in RFC 3339 format.
 */
expires: string;};
}
export type GetExtensionSecretsResponse = DataListResponse<GetExtensionSecretsResponseData>;
export interface CreateExtensionSecretParams {
/**
 * JWT signing activation delay for the newly created secret in seconds.
 * 
 * Minimum: 300. Default: 300.
 */
delay?: number;
}
export interface CreateExtensionSecretResponseData {
/**
 * Indicates the version associated with the Extension secrets in the response.
 */
format_version: number;
/**
 * Array of secret objects.
 */
secrets: {
/**
 * Raw secret that should be used with JWT encoding.
 */
content: string;
/**
 * The earliest possible time this secret is valid to sign a JWT in RFC 3339 format.
 */
active: string;
/**
 * The latest possible time this secret may be used to decode a JWT in RFC 3339 format.
 */
expires: string;};
}
export type CreateExtensionSecretResponse = DataListResponse<CreateExtensionSecretResponseData>;
export interface SendExtensionChatMessageParams {
/**
 * User ID of the broadcaster whose channel has the Extension activated.
 */
broadcaster_id: string;
}
export interface SendExtensionChatMessageBody {
/**
 * Message for Twitch chat.
 * 
 * Maximum: 280 characters.
 */
text: string;
/**
 * Client ID associated with the Extension.
 */
extension_id: string;
/**
 * Version of the Extension sending this message.
 */
extension_version: string;
}
export interface GetExtensionsParams {
/**
 * ID of the Extension.
 */
extension_id: string;
/**
 * The specific version of the Extension to return. If not provided, the current version is returned.
 */
extension_version?: string;
}
export interface GetExtensionsResponseData {
/**
 * Name of the individual or organization that owns the Extension.
 */
author_name: string;
/**
 * Whether the Extension has features that use Bits.
 */
bits_enabled: boolean;
/**
 * Indicates if a user can install the Extension on their channel. They may not be allowed if the Extension is currently in testing mode and the user is not on the allow list.
 */
can_install: boolean;
/**
 * Whether the Extension configuration is hosted by the EBS or the Extensions Configuration Service.
 */
configuration_location: string;
/**
 * The description of the Extension.
 */
description: string;
/**
 * URL to the Extension’s Terms of Service.
 */
eula_tos_url: string;
/**
 * Indicates if the Extension can communicate with the installed channel’s chat.
 */
has_chat_support: boolean;
/**
 * The default icon to be displayed in the Extensions directory.
 */
icon_url: string;
/**
 * The default icon in a variety of sizes.
 */
icon_urls: Record<string, string>;
/**
 * The autogenerated ID of the Extension.
 */
id: string;
/**
 * The name of the Extension.
 */
name: string;
/**
 * URL to the Extension’s privacy policy.
 */
privacy_policy_url: string;
/**
 * Indicates if the Extension wants to explicitly ask viewers to link their Twitch identity.
 */
request_identity_link: boolean;
/**
 * Screenshots to be shown in the Extensions marketplace.
 */
screenshot_urls: string[];
/**
 * The current state of the Extension. Valid values are `"InTest"`, `"InReview"`, `"Rejected"`, `"Approved"`, `"Released"`, `"Deprecated"`, `"PendingAction"`, `"AssetsUploaded"`, `"Deleted"`.
 */
state: string;
/**
 * Indicates if the Extension can determine a user’s subscription level on the channel the Extension is installed on.
 */
subscriptions_support_level: string;
/**
 * A brief description of the Extension.
 */
summary: string;
/**
 * The email users can use to receive Extension support.
 */
support_email: string;
/**
 * The version of the Extension.
 */
version: string;
/**
 * A brief description displayed on the channel to explain how the Extension works.
 */
viewer_summary: string;
/**
 * All configurations related to views such as: mobile, panel, video_overlay, and component.
 */
views: Record<string, Record<string, string | number | boolean>>;
/**
 * Allow-listed configuration URLs for displaying the Extension.
 */
allowlisted_config_urls: string[];
/**
 * Allow-listed panel URLs for displaying the Extension.
 */
allowlisted_panel_urls: string[];
}
export type GetExtensionsResponse = DataListResponse<GetExtensionsResponseData>;
export interface GetReleasedExtensionsParams {
/**
 * ID of the Extension.
 */
extension_id: string;
/**
 * The specific version of the Extension to return. If not provided, the current version is returned.
 */
extension_version?: string;
}
export interface GetReleasedExtensionsResponseData {
/**
 * Name of the individual or organization that owns the Extension.
 */
author_name: string;
/**
 * Whether the Extension has features that use Bits.
 */
bits_enabled: boolean;
/**
 * Indicates if a user can install the Extension on their channel. They may not be allowed if the Extension is currently in testing mode and the user is not on the allow list.
 */
can_install: boolean;
/**
 * Whether the Extension configuration is hosted by the EBS or the Extensions Configuration Service.
 */
configuration_location: string;
/**
 * The description of the Extension.
 */
description: string;
/**
 * URL to the Extension’s Terms of Service.
 */
eula_tos_url: string;
/**
 * Indicates if the Extension can communicate with the installed channel’s chat.
 */
has_chat_support: boolean;
/**
 * The default icon to be displayed in the Extensions directory.
 */
icon_url: string;
/**
 * The default icon in a variety of sizes.
 */
icon_urls: Record<string, string>;
/**
 * The autogenerated ID of the Extension.
 */
id: string;
/**
 * The name of the Extension.
 */
name: string;
/**
 * URL to the Extension’s privacy policy.
 */
privacy_policy_url: string;
/**
 * Indicates if the Extension wants to explicitly ask viewers to link their Twitch identity.
 */
request_identity_link: boolean;
/**
 * Screenshots to be shown in the Extensions marketplace.
 */
screenshot_urls: string[];
/**
 * The current state of the Extension. Valid values are `"InTest"`, `"InReview"`, `"Rejected"`, `"Approved"`, `"Released"`, `"Deprecated"`, `"PendingAction"`, `"AssetsUploaded"`, `"Deleted"`.
 */
state: string;
/**
 * Indicates if the Extension can determine a user’s subscription level on the channel the Extension is installed on.
 */
subscriptions_support_level: string;
/**
 * A brief description of the Extension.
 */
summary: string;
/**
 * The email users can use to receive Extension support.
 */
support_email: string;
/**
 * The version of the Extension.
 */
version: string;
/**
 * A brief description displayed on the channel to explain how the Extension works.
 */
viewer_summary: string;
/**
 * All configurations related to views such as: mobile, panel, video_overlay, and component.
 */
views: Record<string, Record<string, string | number | boolean>>;
/**
 * Allow-listed configuration URLs for displaying the Extension.
 */
allowlisted_config_urls: string[];
/**
 * Allow-listed panel URLs for displaying the Extension.
 */
allowlisted_panel_urls: string[];
}
export type GetReleasedExtensionsResponse = DataListResponse<GetReleasedExtensionsResponseData>;
export interface GetExtensionBitsProductsParams {
/**
 * Whether Bits products that are disabled/expired should be included in the response.
 * 
 * Default: `false`.
 */
should_include_all?: boolean;
}
export interface GetExtensionBitsProductsResponseData {
/**
 * SKU of the Bits product. This is unique across all products that belong to an Extension.
 */
sku: string;
/**
 * Object containing cost information.
 */
cost: {
/**
 * Number of Bits for which the product will be exchanged.
 */
amount: number;
/**
 * Cost type. The one valid value is `"bits"`.
 */
type: string;};
/**
 * Indicates if the product is in development and not yet released for public use.
 */
in_development: boolean;
/**
 * Name of the product to be displayed in the Extension.
 */
display_name: string;
/**
 * Expiration time for the product in RFC3339 format.
 */
expiration: string;
/**
 * Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback.
 */
is_broadcast: boolean;
}
export type GetExtensionBitsProductsResponse = DataListResponse<GetExtensionBitsProductsResponseData>;
export interface UpdateExtensionBitsProductBody {
/**
 * SKU of the Bits product. This must be unique across all products that belong to an Extension. The SKU cannot be changed after saving.
 * 
 * Maximum: 255 characters, no white spaces.
 */
sku: string;
/**
 * Object containing cost information.
 */
cost: {
/**
 * Number of Bits for which the product will be exchanged.
 * 
 * Minimum: 1, Maximum: 10000.
 */
amount: number;
/**
 * Cost type. The one valid value is `"bits"`.
 */
type: string;};
/**
 * Name of the product to be displayed in the Extension.
 * 
 * Maximum: 255 characters.
 */
display_name: string;
/**
 * Set to `true` if the product is in development and not yet released for public use.
 * 
 * Default: `false`.
 */
in_development?: boolean;
/**
 * Expiration time for the product in RFC3339 format. If not provided, the Bits product will not have an expiration date. Setting an expiration in the past will disable the product.
 */
expiration?: string;
/**
 * Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback.
 * 
 * Default: `false`.
 */
is_broadcast?: boolean;
}
export interface UpdateExtensionBitsProductResponseData {
/**
 * SKU of the Bits product. This is unique across all products that belong to an Extension.
 */
sku: string;
/**
 * Object containing cost information.
 */
cost: {
/**
 * Number of Bits for which the product will be exchanged.
 */
amount: number;
/**
 * Cost type. The one valid value is `"bits"`.
 */
type: string;};
/**
 * Indicates if the product is in development and not yet released for public use.
 */
in_development: boolean;
/**
 * Name of the product to be displayed in the Extension.
 */
display_name: string;
/**
 * Expiration time for the product in RFC3339 format.
 */
expiration: string;
/**
 * Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback.
 */
is_broadcast: boolean;
}
export type UpdateExtensionBitsProductResponse = DataListResponse<UpdateExtensionBitsProductResponseData>;
export interface CreateEventsubSubscriptionBody {
/**
 * The type of subscription to create. For a list of subscriptions you can create, see Subscription Types. Set `type` to the value in the Name column of the Subscription Types table.
 */
type: string;
/**
 * The version of the subscription type used in this request. A subscription type could define one or more object definitions, so you need to specify which definition you’re using.
 */
version: string;
/**
 * The parameter values that are specific to the specified subscription type.
 */
condition: EventSubCondition;
/**
 * The transport details, such as the transport method and callback URL, that you want Twitch to use when sending you notifications.
 */
transport: EventSubTransport;
}
export interface CreateEventsubSubscriptionResponseData {
/**
 * An ID that identifies the subscription.
 */
id: string;
/**
 * The status of the create subscription request. Possible values are: 
 * - enabled — The subscription is enabled.
 * - webhook_callback_verification_pending — The subscription is pending verification of the specified callback URL. To determine if the subscription moved from pending to another state, send a GET request and use the ID to find the subscription in the list.
 * - webhook_callback_verification_failed — The specified callback URL failed verification.
 * - notification_failures_exceeded — The notification delivery failure rate was too high.
 * - authorization_revoked — The authorization was revoked for one or more users specified in the Condition object.
 * - user_removed — One of the users specified in the Condition object was removed.
 */
status: string;
/**
 * The type of subscription.
 */
type: string;
/**
 * The version of the subscription type.
 */
version: string;
/**
 * The parameter values for the subscription type.
 */
condition: EventSubCondition;
/**
 * The RFC 3339 timestamp indicating when the subscription was created.
 */
created_at: string;
/**
 * The transport details used to send you notifications.
 */
transport: EventSubTransport;
/**
 * The amount that the subscription counts against your limit. Learn More
 */
cost: number;
}
export interface CreateEventsubSubscriptionResponse extends DataListResponse<CreateEventsubSubscriptionResponseData> {
/**
 * The total number of subscriptions you’ve created.
 */
total: number;
/**
 * The sum of all of your subscription costs. Learn More
 */
total_cost: number;
/**
 * The maximum total cost that you may incur for all subscriptions you create.
 */
max_total_cost: number;
}
export interface DeleteEventsubSubscriptionParams {
/**
 * The ID of the subscription to delete. This is the ID that Create Eventsub Subscription returns.
 */
id: string;
}
export interface GetEventsubSubscriptionsParams {
/**
 * Filter subscriptions by its status. You may specify only one status value. Valid values are: 
 * - enabled — The subscription is enabled.
 * - webhook_callback_verification_pending — The subscription is pending verification of the specified callback URL.
 * - webhook_callback_verification_failed — The specified callback URL failed verification.
 * - notification_failures_exceeded — The notification delivery failure rate was too high.
 * - authorization_revoked — The authorization was revoked for one or more users specified in the Condition object.
 * - user_removed — One of the users specified in the Condition object was removed.
 */
status?: string;
/**
 * Filter subscriptions by subscription type (e.g., `channel.update`). For a list of subscription types, see Subscription Types.
 */
type?: string;
/**
 * The cursor used to get the next page of results. The `pagination` object in the response contains the cursor’s value.
 */
after?: string;
}
export interface GetEventsubSubscriptionsResponseData {
/**
 * An ID that identifies the subscription.
 */
id: string;
/**
 * The subscription’s status. Possible values are: 
 * - enabled — The subscription is enabled.
 * - webhook_callback_verification_pending — The subscription is pending verification of the specified callback URL.
 * - webhook_callback_verification_failed — The specified callback URL failed verification.
 * - notification_failures_exceeded — The notification delivery failure rate was too high.
 * - authorization_revoked — The authorization was revoked for one or more users specified in the Condition object.
 * - user_removed — One of the users specified in the Condition object was removed.
 */
status: string;
/**
 * The subscription’s type.
 */
type: string;
/**
 * The version of the subscription type.
 */
version: string;
/**
 * The subscription’s parameter values.
 */
condition: EventSubCondition;
/**
 * The RFC 3339 timestamp indicating when the subscription was created.
 */
created_at: string;
/**
 * The transport details used to send you notifications.
 */
transport: EventSubTransport;
/**
 * The amount that the subscription counts against your limit. Learn More
 */
cost: number;
}
export interface GetEventsubSubscriptionsResponse extends DataListResponse<GetEventsubSubscriptionsResponseData>, PaginatedCursorResponse {
/**
 * The total number of subscriptions you’ve created.
 */
total: number;
/**
 * The sum of all of your subscription costs. Learn More
 */
total_cost: number;
/**
 * The maximum total cost that you’re allowed to incur for all subscriptions you create.
 */
max_total_cost: number;
}
export interface GetTopGamesParams {
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
before?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: number;
}
export interface GetTopGamesResponseData {
/**
 * Template URL for a game’s box art.
 */
box_art_url: string;
/**
 * Game ID.
 */
id: string;
/**
 * Game name.
 */
name: string;
}
export type GetTopGamesResponse = DataListResponse<GetTopGamesResponseData> & PaginatedCursorResponse;
export interface GetGamesParams {
/**
 * Game ID. At most 100 `id` values can be specified.
 */
id: string;
/**
 * Game name. The name must be an exact match. For example, “Pokemon” will not return a list of Pokemon games; instead, query any specific Pokemon games in which you are interested. At most 100 `name` values can be specified.
 */
name: string;
}
export interface GetGamesResponseData {
/**
 * Template URL for the game’s box art.
 */
box_art_url: string;
/**
 * Game ID.
 */
id: string;
/**
 * Game name.
 */
name: string;
}
export type GetGamesResponse = DataListResponse<GetGamesResponseData> & PaginatedCursorResponse;
export interface GetCreatorGoalsParams {
/**
 * The ID of the broadcaster that created the goals.
 */
broadcaster_id: string;
}
export interface GetCreatorGoalsResponseData {
/**
 * An ID that uniquely identifies this goal.
 */
id: string;
/**
 * An ID that uniquely identifies the broadcaster.
 */
broadcaster_id: string;
/**
 * The broadcaster’s display name.
 */
broadcaster_name: string;
/**
 * The broadcaster’s user handle.
 */
broadcaster_login: string;
/**
 * The type of goal. Possible values are: 
 * - follower — The goal is to increase followers.
 * - subscription — The goal is to increase subscriptions. This type shows the net increase or decrease in subscriptions.
 * - new_subscription — The goal is to increase subscriptions. This type shows only the net increase in subscriptions (it does not account for users that stopped subscribing since the goal's inception).
 */
type: string;
/**
 * A description of the goal, if specified. The description may contain a maximum of 40 characters.
 */
description: string;
/**
 * The current value.
 * 
 * If the goal is to increase followers, this field is set to the current number of followers. This number increases with new followers and decreases if users unfollow the channel.
 * 
 * For subscriptions, `current_amount` is increased and decreased by the points value associated with the subscription tier. For example, if a tier-two subscription is worth 2 points, `current_amount` is increased or decreased by 2, not 1.
 * 
 * For new_subscriptions, `current_amount` is increased by the points value associated with the subscription tier. For example, if a tier-two subscription is worth 2 points, `current_amount` is increased by 2, not 1.
 */
current_amount: number;
/**
 * The goal’s target value. For example, if the broadcaster has 200 followers before creating the goal, and their goal is to double that number, this field is set to 400.
 */
target_amount: number;
/**
 * The UTC timestamp in RFC 3339 format, which indicates when the broadcaster created the goal.
 */
created_at: string;
}
export type GetCreatorGoalsResponse = DataListResponse<GetCreatorGoalsResponseData>;
export interface GetHypeTrainEventsParams {
/**
 * User ID of the broadcaster. Must match the User ID in the Bearer token if User Token is used.
 */
broadcaster_id: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 1.
 */
first?: number;
/**
 * The id of the wanted event, if known
 */
id?: string;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without id. If an ID is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the pagination response field of a prior query.
 */
cursor?: string;
}
export interface GetHypeTrainEventsResponseData {
/**
 * The distinct ID of the event
 */
id: string;
/**
 * Displays hypetrain.{event_name}, currently only hypetrain.progression
 */
event_type: string;
/**
 * RFC3339 formatted timestamp of event
 */
event_timestamp: string;
/**
 * Returns the version of the endpoint
 */
version: string;
/**
 * (See below for the schema)
 */
event_data: {
/**
 * The distinct ID of this Hype Train
 */
id: string;
/**
 * Channel ID of which Hype Train events the clients are interested in
 */
broadcaster_id: string;
/**
 * RFC3339 formatted timestamp of when this Hype Train started
 */
started_at: string;
/**
 * RFC3339 formatted timestamp of the expiration time of this Hype Train
 */
expires_at: string;
/**
 * RFC3339 formatted timestamp of when another Hype Train can be started again
 */
cooldown_end_time: string;
/**
 * The highest level (in the scale of 1-5) reached of the Hype Train
 */
level: number;
/**
 * The goal value of the level above
 */
goal: number;
/**
 * The total score so far towards completing the level goal above
 */
total: number;
/**
 * An array of top contribution objects, one object for each type. For example, one object would represent top contributor of `BITS`, by aggregate, and one would represent top contributor of `SUBS` by count.
 */
top_contributions: {
/**
 * Total aggregated amount of all contributions by the top contributor. If type is `BITS`, total represents aggregate amount of bits used. If type is `SUBS`, aggregate total where 500, 1000, or 2500 represent tier 1, 2, or 3 subscriptions respectively. For example, if top contributor has gifted a tier 1, 2, and 3 subscription, total would be 4000.
 */
total: number;
/**
 * Identifies the contribution method, either `BITS `or `SUBS`
 */
type: string;
/**
 * ID of the contributing user
 */
user: string;};
/**
 * An object that represents the most recent contribution
 */
last_contribution: {
/**
 * Total amount contributed. If type is `BITS`, total represents amounts of bits used. If type is `SUBS`, total is 500, 1000, or 2500 to represent tier 1, 2, or 3 subscriptions respectively
 */
total: number;
/**
 * Identifies the contribution method, either `BITS `or `SUBS`
 */
type: string;
/**
 * ID of the contributing user
 */
user: string;};};
}
export type GetHypeTrainEventsResponse = DataListResponse<GetHypeTrainEventsResponseData> & PaginatedCursorResponse;
export interface CheckAutomodStatusParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the auth token.
 */
broadcaster_id: string;
}
export interface CheckAutomodStatusBody {
/**
 * Developer-generated identifier for mapping messages to results.
 */
msg_id: string;
/**
 * Message text.
 */
msg_text: string;
/**
 * User ID of the sender.
 */
user_id: string;
}
export interface CheckAutomodStatusResponseData {
/**
 * The `msg_id` passed in the body of the `POST` message. Maps each message to its status.
 */
msg_id: string;
/**
 * Indicates if this message meets AutoMod requirements.
 */
is_permitted: boolean;
}
export type CheckAutomodStatusResponse = DataListResponse<CheckAutomodStatusResponseData>;
export interface ManageHeldAutomodMessagesBody {
/**
 * The moderator who is approving or rejecting the held message. Must match the `user_id` in the user OAuth token.
 */
user_id: string;
/**
 * ID of the message to be allowed or denied. These message IDs are retrieved from PubSub as mentioned above. Only one message ID can be provided.
 */
msg_id: string;
/**
 * The action to take for the message. Must be `"ALLOW"` or `"DENY"`.
 */
action: string;
}
export interface GetAutomodSettingsParams {
/**
 * The ID of the broadcaster whose AutoMod settings you want to get.
 */
broadcaster_id: string;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to get their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
}
export interface GetAutomodSettingsResponseData {
/**
 * The Automod level for hostility involving aggression.
 */
aggression: number;
/**
 * The broadcaster’s ID.
 */
broadcaster_id: string;
/**
 * The Automod level for hostility involving name calling or insults.
 */
bullying: number;
/**
 * The Automod level for discrimination against disability.
 */
disability: number;
/**
 * The Automod level for discrimination against women.
 */
misogyny: number;
/**
 * The moderator’s ID.
 */
moderator_id: string;
/**
 * The default AutoMod level for the broadcaster. This field is null if the broadcaster has set one or more of the individual settings.
 */
overall_level: number | null;
/**
 * The Automod level for racial discrimination.
 */
race_ethnicity_or_religion: number;
/**
 * The Automod level for sexual content.
 */
sex_based_terms: number;
/**
 * The AutoMod level for discrimination based on sexuality, sex, or gender.
 */
sexuality_sex_or_gender: number;
/**
 * The Automod level for profanity.
 */
swearing: number;
}
export type GetAutomodSettingsResponse = DataListResponse<GetAutomodSettingsResponseData>;
export interface UpdateAutomodSettingsParams {
/**
 * The ID of the broadcaster whose AutoMod settings you want to update.
 */
broadcaster_id: string;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to update their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
}
export interface UpdateAutomodSettingsBody {
/**
 * The Automod level for hostility involving aggression.
 */
aggression?: number;
/**
 * The Automod level for hostility involving name calling or insults.
 */
bullying?: number;
/**
 * The Automod level for discrimination against disability.
 */
disability?: number;
/**
 * The Automod level for discrimination against women.
 */
misogyny?: number;
/**
 * The default AutoMod level for the broadcaster.
 */
overall_level?: number;
/**
 * The Automod level for racial discrimination.
 */
race_ethnicity_or_religion?: number;
/**
 * The Automod level for sexual content.
 */
sex_based_terms?: number;
/**
 * The AutoMod level for discrimination based on sexuality, sex, or gender.
 */
sexuality_sex_or_gender?: number;
/**
 * The Automod level for profanity.
 */
swearing?: number;
}
export interface UpdateAutomodSettingsResponseData {
/**
 * The Automod level for hostility involving aggression.
 */
aggression: number;
/**
 * The broadcaster’s ID.
 */
broadcaster_id: string;
/**
 * The Automod level for hostility involving name calling or insults.
 */
bullying: number;
/**
 * The Automod level for discrimination against disability.
 */
disability: number;
/**
 * The Automod level for discrimination against women.
 */
misogyny: number;
/**
 * The moderator’s ID.
 */
moderator_id: string;
/**
 * The default AutoMod level for the broadcaster. This field is null if the broadcaster has set one or more of the individual settings.
 */
overall_level: number | null;
/**
 * The Automod level for racial discrimination.
 */
race_ethnicity_or_religion: number;
/**
 * The Automod level for sexual content.
 */
sex_based_terms: number;
/**
 * The AutoMod level for discrimination based on sexuality, sex, or gender.
 */
sexuality_sex_or_gender: number;
/**
 * The Automod level for profanity.
 */
swearing: number;
}
export type UpdateAutomodSettingsResponse = DataListResponse<UpdateAutomodSettingsResponseData>;
export interface GetBannedUsersParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the OAuth token.
 */
broadcaster_id: string;
/**
 * Filters the results and only returns a status object for users who are banned in the channel and have a matching user_id.
 * 
 * Multiple user IDs can be provided, e.g. `/moderation/banned/events?broadcaster_id=1&user_id=2&user_id=3`
 * 
 * Maximum: 100.
 */
user_id?: string | string[];
/**
 * Maximum number of objects to return.
 * 
 * Maximum: 100.
 * Default: 1.
 */
first?: string;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Cursor for backward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset. combinations. The cursor value specified here is from the `pagination` response field of a prior query.
 */
before?: string;
}
export interface GetBannedUsersResponseData {
/**
 * User ID of the banned user.
 */
user_id: string;
/**
 * Login of the banned user.
 */
user_login: string;
/**
 * Display name of the banned user.
 */
user_name: string;
/**
 * Timestamp of the ban expiration. Set to empty string if the ban is permanent.
 */
expires_at: string;
/**
 * The reason for the ban if provided by the moderator.
 */
reason: string;
/**
 * User ID of the moderator who initiated the ban.
 */
moderator_id: string;
/**
 * Login of the moderator who initiated the ban.
 */
moderator_login: string;
/**
 * Display name of the moderator who initiated the ban.
 */
moderator_name: string;
}
export type GetBannedUsersResponse = DataListResponse<GetBannedUsersResponseData> & PaginatedCursorResponse;
export interface BanUserParams {
/**
 * The ID of the broadcaster whose chat room the user is being banned from.
 */
broadcaster_id: string;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to ban the user (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
}
export interface BanUserBody {
/**
 * The user to ban or put in a timeout.
 */
data: {
/**
 * To ban a user indefinitely, don’t include this field.
 * 
 * To put a user in a timeout, include this field and specify the timeout period, in seconds.
 * 
 * The minimum timeout is 1 second and the maximum is 1,209,600 seconds (2 weeks).
 * 
 * To end a user’s timeout early, set this field to 1, or send an Unban user request.
 */
duration?: number;
/**
 * The reason the user is being banned or put in a timeout. The text is user defined and limited to a maximum of 500 characters.
 */
reason: string;
/**
 * The ID of the user to ban or put in a timeout.
 */
user_id: string;};
}
export interface BanUserResponseData {
/**
 * The broadcaster whose chat room the user was banned from chatting in.
 */
broadcaster_id: string;
/**
 * The UTC date and time (in RFC3339 format) that the timeout will end. Is null if the user was banned instead of put in a timeout.
 */
end_time: string | null;
/**
 * The moderator that banned or put the user in the timeout.
 */
moderator_id: string;
/**
 * The user that was banned or was put in a timeout.
 */
user_id: string;
}
export type BanUserResponse = DataListResponse<BanUserResponseData>;
export interface UnbanUserParams {
/**
 * The ID of the broadcaster whose chat room the user is banned from chatting in.
 */
broadcaster_id: string;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to remove the ban (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
/**
 * The ID of the user to remove the ban or timeout from.
 */
user_id: string;
}
export interface GetBlockedTermsParams {
/**
 * The cursor used to get the next page of results. The Pagination object in the response contains the cursor’s value.
 */
after?: string;
/**
 * The ID of the broadcaster whose blocked terms you’re getting.
 */
broadcaster_id: string;
/**
 * The maximum number of blocked terms to return per page in the response. The minimum page size is 1 blocked term per page and the maximum is 100. The default is 20.
 */
first?: number;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to get their own block terms (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
}
export interface GetBlockedTermsResponseData {
/**
 * The broadcaster that owns the list of blocked terms.
 */
broadcaster_id: string;
/**
 * The UTC date and time (in RFC3339 format) of when the term was blocked.
 */
created_at: string;
/**
 * The UTC date and time (in RFC3339 format) of when the blocked term is set to expire. After the block expires, user’s will be able to use the term in the broadcaster’s chat room.
 * 
 * This field is null if the term was added manually or was permanently blocked by AutoMod.
 */
expires_at: string | null;
/**
 * An ID that uniquely identifies this blocked term.
 */
id: string;
/**
 * The moderator that blocked the word or phrase from being used in the broadcaster’s chat room.
 */
moderator_id: string;
/**
 * The blocked word or phrase.
 */
text: string;
/**
 * The UTC date and time (in RFC3339 format) of when the term was updated.
 * 
 * When the term is added, this timestamp is the same as created_at. The timestamp changes as AutoMod continues to deny the term.
 */
updated_at: string;
}
export type GetBlockedTermsResponse = DataListResponse<GetBlockedTermsResponseData> & PaginatedCursorResponse;
export interface AddBlockedTermParams {
/**
 * The ID of the broadcaster that owns the list of blocked terms.
 */
broadcaster_id: string;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to add the blocked term (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
}
export interface AddBlockedTermBody {
/**
 * The word or phrase to block from being used in the broadcaster’s chat room.
 * 
 * The term must contain a minimum of 2 characters and may contain up to a maximum of 500 characters.
 * 
 * Terms can use a wildcard character (*). The wildcard character must appear at the beginning or end of a word, or set of characters. For example, *foo or foo*.
 */
text: string;
}
export interface AddBlockedTermResponseData {
/**
 * The broadcaster that owns the list of blocked terms.
 */
broadcaster_id: string;
/**
 * The UTC date and time (in RFC3339 format) of when the term was blocked.
 */
created_at: string;
/**
 * Is set to null.
 */
expires_at: string | null;
/**
 * An ID that uniquely identifies this blocked term.
 */
id: string;
/**
 * The moderator that blocked the word or phrase from being used in the broadcaster’s chat room.
 */
moderator_id: string;
/**
 * The blocked word or phrase.
 */
text: string;
/**
 * The UTC date and time (in RFC3339 format) of when the term was updated. This timestamp is the same as created_at.
 */
updated_at: string;
}
export type AddBlockedTermResponse = DataListResponse<AddBlockedTermResponseData>;
export interface RemoveBlockedTermParams {
/**
 * The ID of the broadcaster that owns the list of blocked terms.
 */
broadcaster_id: string;
/**
 * The ID of the blocked term you want to delete.
 */
id: string;
/**
 * The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID associated with the user OAuth token.
 * 
 * If the broadcaster wants to delete the blocked term (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too.
 */
moderator_id: string;
}
export interface GetModeratorsParams {
/**
 * Provided `broadcaster_id` must match the `user_id` in the auth token. Maximum: 1
 */
broadcaster_id: string;
/**
 * Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id.
 * 
 * Format: Repeated Query Parameter, eg. `/moderation/moderators?broadcaster_id=1&user_id=2&user_id=3`
 * 
 * Maximum: 100
 */
user_id?: string | string[];
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: string;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
}
export interface GetModeratorsResponseData {
/**
 * User ID of a moderator in the channel.
 */
user_id: string;
/**
 * Login of a moderator in the channel.
 */
user_login: string;
/**
 * Display name of a moderator in the channel.
 */
user_name: string;
}
export type GetModeratorsResponse = DataListResponse<GetModeratorsResponseData> & PaginatedCursorResponse;
export interface GetPollsParams {
/**
 * The broadcaster running polls. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * ID of a poll. Filters results to one or more specific polls. Not providing one or more IDs will return the full list of polls for the authenticated channel.
 * 
 * Maximum: 100
 */
id?: string | string[];
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Maximum number of objects to return.
 * 
 * Maximum: 20. Default: 20.
 */
first?: string;
}
export interface GetPollsResponseData {
/**
 * ID of the poll.
 */
id: string;
/**
 * ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Question displayed for the poll.
 */
title: string;
/**
 * Array of the poll choices.
 */
choices: Array<{
/**
 * ID for the choice.
 */
id: string;
/**
 * Text displayed for the choice.
 */
title: string;
/**
 * Total number of votes received for the choice across all methods of voting.
 */
votes: number;
/**
 * Number of votes received via Channel Points.
 */
channel_points_votes: number;
/**
 * Number of votes received via Bits.
 */
bits_votes: number;}>;
/**
 * Indicates if Bits can be used for voting.
 */
bits_voting_enabled: boolean;
/**
 * Number of Bits required to vote once with Bits.
 */
bits_per_vote: number;
/**
 * Indicates if Channel Points can be used for voting.
 */
channel_points_voting_enabled: boolean;
/**
 * Number of Channel Points required to vote once with Channel Points.
 */
channel_points_per_vote: number;
/**
 * Poll status. Valid values are:
 * 
 * `ACTIVE`: Poll is currently in progress.
 * 
 * `COMPLETED`: Poll has reached its `ended_at` time.
 * 
 * `TERMINATED`: Poll has been manually terminated before its `ended_at` time.
 * 
 * `ARCHIVED`: Poll is no longer visible on the channel.
 * 
 * `MODERATED`: Poll is no longer visible to any user on Twitch.
 * 
 * `INVALID`: Something went wrong determining the state.
 */
status: string;
/**
 * Total duration for the poll (in seconds).
 */
duration: number;
/**
 * UTC timestamp for the poll’s start time.
 */
started_at: string;
/**
 * UTC timestamp for the poll’s end time. Set to `null` if the poll is active.
 */
ended_at: string | null;
}
export type GetPollsResponse = DataListResponse<GetPollsResponseData> & PaginatedCursorResponse;
export interface CreatePollBody {
/**
 * The broadcaster running polls. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * Question displayed for the poll.
 * 
 * Maximum: 60 characters.
 */
title: string;
/**
 * Array of the poll choices.
 * 
 * Minimum: 2 choices. Maximum: 5 choices.
 */
choices: Array<{
/**
 * Text displayed for the choice.
 * 
 * Maximum: 25 characters.
 */
title: string;}>;
/**
 * Total duration for the poll (in seconds).
 * 
 * Minimum: 15. Maximum: 1800.
 */
duration: number;
/**
 * Indicates if Bits can be used for voting.
 * 
 * Default: `false`
 */
bits_voting_enabled?: boolean;
/**
 * Number of Bits required to vote once with Bits.
 * 
 * Minimum: 0. Maximum: 10000.
 */
bits_per_vote?: number;
/**
 * Indicates if Channel Points can be used for voting.
 * 
 * Default: `false`
 */
channel_points_voting_enabled?: boolean;
/**
 * Number of Channel Points required to vote once with Channel Points.
 * 
 * Minimum: 0. Maximum: 1000000.
 */
channel_points_per_vote?: number;
}
export interface CreatePollResponseData {
/**
 * ID of the poll.
 */
id: string;
/**
 * ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Question displayed for the poll.
 */
title: string;
/**
 * Array of the poll choices.
 */
choices: Array<{
/**
 * ID for the choice.
 */
id: string;
/**
 * Text displayed for the choice.
 */
title: string;
/**
 * Total number of votes received for the choice.
 */
votes: number;
/**
 * Number of votes received via Channel Points.
 */
channel_points_votes: number;
/**
 * Number of votes received via Bits.
 */
bits_votes: number;}>;
/**
 * Indicates if Bits can be used for voting.
 */
bits_voting_enabled: boolean;
/**
 * Number of Bits required to vote once with Bits.
 */
bits_per_vote: number;
/**
 * Indicates if Channel Points can be used for voting.
 */
channel_points_voting_enabled: boolean;
/**
 * Number of Channel Points required to vote once with Channel Points.
 */
channel_points_per_vote: number;
/**
 * Poll status. Valid values are:
 * 
 * `ACTIVE`: Poll is currently in progress.
 * 
 * `COMPLETED`: Poll has reached its `ended_at` time.
 * 
 * `TERMINATED`: Poll has been manually terminated before its `ended_at` time.
 * 
 * `ARCHIVED`: Poll is no longer visible on the channel.
 * 
 * `MODERATED`: Poll is no longer visible to any user on Twitch.
 * 
 * `INVALID`: Something went wrong determining the state.
 */
status: string;
/**
 * Total duration for the poll (in seconds).
 */
duration: number;
/**
 * UTC timestamp for the poll’s start time.
 */
started_at: string;
/**
 * UTC timestamp for the poll’s end time. Set to `null` if the poll is active.
 */
ended_at: string | null;
}
export type CreatePollResponse = DataListResponse<CreatePollResponseData>;
export interface EndPollBody {
/**
 * The broadcaster running polls. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * ID of the poll.
 */
id: string;
/**
 * The poll status to be set. Valid values:
 * 
 * `TERMINATED`: End the poll manually, but allow it to be viewed publicly.
 * 
 * `ARCHIVED`: End the poll manually and do not allow it to be viewed publicly.
 */
status: string;
}
export interface EndPollResponseData {
/**
 * ID of the poll.
 */
id: string;
/**
 * ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Question displayed for the poll.
 */
title: string;
/**
 * Array of the poll choices.
 */
choices: Array<{
/**
 * ID for the choice.
 */
id: string;
/**
 * Text displayed for the choice.
 */
title: string;
/**
 * Total number of votes received for the choice.
 */
votes: number;
/**
 * Number of votes received via Channel Points.
 */
channel_points_votes: number;
/**
 * Number of votes received via Bits.
 */
bits_votes: number;}>;
/**
 * Indicates if Bits can be used for voting.
 */
bits_voting_enabled: boolean;
/**
 * Number of Bits required to vote once with Bits.
 */
bits_per_vote: number;
/**
 * Indicates if Channel Points can be used for voting.
 */
channel_points_voting_enabled: boolean;
/**
 * Number of Channel Points required to vote once with Channel Points.
 */
channel_points_per_vote: number;
/**
 * Poll Status. Valid values are:
 * 
 * `ACTIVE`: Poll is currently in progress.
 * 
 * `COMPLETED`: Poll has reached its `ended_at` time.
 * 
 * `TERMINATED`: Poll has been manually terminated before its `ended_at` time.
 * 
 * `ARCHIVED`: Poll is no longer visible on the channel.
 * 
 * `MODERATED`: Poll is no longer visible to any user on Twitch.
 * 
 * `INVALID`: Something went wrong determining the state.
 */
status: string;
/**
 * Total duration for the poll (in seconds).
 */
duration: number;
/**
 * UTC timestamp for the poll’s start time.
 */
started_at: string;
/**
 * UTC timestamp for the poll’s end time.
 */
ended_at: string;
}
export type EndPollResponse = DataListResponse<EndPollResponseData>;
export interface GetPredictionsParams {
/**
 * The broadcaster running Predictions. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * ID of a Prediction. Filters results to one or more specific Predictions. Not providing one or more IDs will return the full list of Predictions for the authenticated channel.
 * 
 * Maximum: 100
 */
id?: string | string[];
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Maximum number of objects to return.
 * 
 * Maximum: 20. Default: 20.
 */
first?: string;
}
export interface GetPredictionsResponseData {
/**
 * ID of the Prediction.
 */
id: string;
/**
 * ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Title for the Prediction.
 */
title: string;
/**
 * ID of the winning outcome. If the status is `ACTIVE`, this is set to `null`.
 */
winning_outcome_id: string | null;
/**
 * Array of possible outcomes for the Prediction.
 */
outcomes: Array<{
/**
 * ID for the outcome.
 */
id: string;
/**
 * Text displayed for outcome.
 */
title: string;
/**
 * Number of unique users that chose the outcome.
 */
users: number;
/**
 * Number of Channel Points used for the outcome.
 */
channel_points: number;
/**
 * Array of users who were the top predictors. `null` if none.
 */
top_predictors: Array<{
/**
 * ID of the user.
 */
id: string;
/**
 * Display name of the user.
 */
name: string;
/**
 * Login of the user.
 */
login: string;
/**
 * Number of Channel Points used by the user.
 */
channel_points_used: number;
/**
 * Number of Channel Points won by the user.
 */
channel_points_won: number;}> | null;
/**
 * Color for the outcome. Valid values: `BLUE`, `PINK`
 */
color: string;}>;
/**
 * Total duration for the Prediction (in seconds).
 */
prediction_window: number;
/**
 * Status of the Prediction. Valid values are:
 * 
 * `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who guessed the correct outcome.
 * 
 * `ACTIVE`: The Prediction is active and viewers can make predictions.
 * 
 * `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.
 * 
 * `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.
 */
status: string;
/**
 * UTC timestamp for the Prediction’s start time.
 */
created_at: string;
/**
 * UTC timestamp for when the Prediction ended. If the status is `ACTIVE`, this is set to `null`.
 */
ended_at: string | null;
/**
 * UTC timestamp for when the Prediction was locked. If the status is not `LOCKED`, this is set to `null`.
 */
locked_at: string | null;
}
export type GetPredictionsResponse = DataListResponse<GetPredictionsResponseData> & PaginatedCursorResponse;
export interface CreatePredictionBody {
/**
 * The broadcaster running Predictions. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * Title for the Prediction.
 * 
 * Maximum: 45 characters.
 */
title: string;
/**
 * Array of outcome objects with titles for the Prediction. Array size must be 2. The first outcome object is the “blue” outcome and the second outcome object is the “pink” outcome when viewing the Prediction on Twitch.
 */
outcomes: Array<{
/**
 * Text displayed for the outcome choice.
 * 
 * Maximum: 25 characters.
 */
title: string;}>;
/**
 * Total duration for the Prediction (in seconds).
 * 
 * Minimum: 1. Maximum: 1800.
 */
prediction_window: number;
}
export interface CreatePredictionResponseData {
/**
 * ID of the Prediction.
 */
id: string;
/**
 * ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Title for the Prediction.
 */
title: string;
/**
 * ID of the winning outcome.
 */
winning_outcome_id: string;
/**
 * Array of possible outcomes for the Prediction.
 */
outcomes: Array<{
/**
 * ID for the outcome.
 */
id: string;
/**
 * Text displayed for outcome.
 */
title: string;
/**
 * Number of unique users that chose the outcome.
 */
users: number;
/**
 * Number of Channel Points used for the outcome.
 */
channel_points: number;
/**
 * Color for the outcome. Valid values: `BLUE`, `PINK`
 */
color: string;
/**
 * Array of users who were the top predictors.
 */
top_predictors: Array<{
/**
 * ID of the user.
 */
id: string;
/**
 * Display name of the user.
 */
name: string;
/**
 * Login of the user.
 */
login: string;
/**
 * Number of Channel Points used by the user.
 */
channel_points_used: number;
/**
 * Number of Channel Points won by the user.
 */
channel_points_won: number;}>;}>;
/**
 * Total duration for the Prediction (in seconds).
 */
prediction_window: number;
/**
 * Status of the Prediction. Valid values are:
 * 
 * `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who predicted the correct outcome.
 * 
 * `ACTIVE`: The Prediction is active and viewers can make predictions.
 * 
 * `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.
 * 
 * `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.
 */
status: string;
/**
 * UTC timestamp for the Prediction’s start time.
 */
created_at: string;
/**
 * UTC timestamp for when the Prediction ended. If the status is `ACTIVE`, this is set to `null`.
 */
ended_at: string | null;
/**
 * UTC timestamp for when the Prediction was locked. If the status is not `LOCKED`, this is set to `null`.
 */
locked_at: string | null;
}
export type CreatePredictionResponse = DataListResponse<CreatePredictionResponseData>;
export interface EndPredictionBody {
/**
 * The broadcaster running prediction events. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * ID of the Prediction.
 */
id: string;
/**
 * The Prediction status to be set. Valid values:
 * 
 * `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who predicted the correct outcome.
 * 
 * `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.
 * 
 * `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.
 */
status: string;
/**
 * ID of the winning outcome for the Prediction. This parameter is required if `status` is being set to `RESOLVED`.
 */
winning_outcome_id?: string;
}
export interface EndPredictionResponseData {
/**
 * ID of the prediction.
 */
id: string;
/**
 * ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Title for the prediction.
 */
title: string;
/**
 * ID of the winning outcome.
 */
winning_outcome_id: string;
/**
 * Array of possible outcomes for the prediction.
 */
outcomes: Array<{
/**
 * ID for the outcome.
 */
id: string;
/**
 * Text displayed for outcome.
 */
title: string;
/**
 * Number of unique users that chose the outcome.
 */
users: number;
/**
 * Number of Channel Points used for the outcome.
 */
channel_points: number;
/**
 * Color for the outcome. Valid values: `BLUE`, `PINK`
 */
color: string;
/**
 * Array of users who were the top predictors.
 */
top_predictors: Array<{
/**
 * ID of the user.
 */
id: string;
/**
 * Display name of the user.
 */
name: string;
/**
 * Login of the user.
 */
login: string;
/**
 * Number of Channel Points used by the user.
 */
channel_points_used: number;
/**
 * Number of Channel Points won by the user.
 */
channel_points_won: number;}>;}>;
/**
 * Total duration for the prediction (in seconds).
 */
prediction_window: number;
/**
 * Status of the prediction. Valid values are:
 * 
 * `RESOLVED`: A winning outcome has been chosen and the Channel Points have been distributed to the users who predicted the correct outcome.
 * 
 * `ACTIVE`: The Prediction is active and viewers can make predictions.
 * 
 * `CANCELED`: The Prediction has been canceled and the Channel Points have been refunded to participants.
 * 
 * `LOCKED`: The Prediction has been locked and viewers can no longer make predictions.
 */
status: string;
/**
 * UTC timestamp for the prediction’s start time.
 */
created_at: string;
/**
 * UTC timestamp for when the prediction ended. If the status is `ACTIVE`, this is set to `null`.
 */
ended_at: string | null;
/**
 * UTC timestamp for when the prediction was locked. If the status is not `LOCKED`, this is set to `null`.
 */
locked_at: string | null;
}
export type EndPredictionResponse = DataListResponse<EndPredictionResponseData>;
export interface GetChannelStreamScheduleParams {
/**
 * User ID of the broadcaster who owns the channel streaming schedule.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * The ID of the stream segment to return.
 * 
 * Maximum: 100.
 */
id?: string | string[];
/**
 * A timestamp in RFC3339 format to start returning stream segments from. If not specified, the current date and time is used.
 */
start_time?: string;
/**
 * A timezone offset for the requester specified in minutes. This is recommended to ensure stream segments are returned for the correct week. For example, a timezone that is +4 hours from GMT would be “240.” If not specified, “0” is used for GMT.
 */
utc_offset?: string;
/**
 * Maximum number of stream segments to return.
 * 
 * Maximum: 25. Default: 20.
 */
first?: number;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
}
export interface GetChannelStreamScheduleResponseData {
/**
 * Scheduled broadcasts for this stream schedule.
 */
segments: Array<{
/**
 * The ID for the scheduled broadcast.
 */
id: string;
/**
 * Scheduled start time for the scheduled broadcast in RFC3339 format.
 */
start_time: string;
/**
 * Scheduled end time for the scheduled broadcast in RFC3339 format.
 */
end_time: string;
/**
 * Title for the scheduled broadcast.
 */
title: string;
/**
 * Used with recurring scheduled broadcasts. Specifies the date of the next recurring broadcast in RFC3339 format if one or more specific broadcasts have been deleted in the series. Set to `null` otherwise.
 */
canceled_until: string | null;
/**
 * The category for the scheduled broadcast. Set to `null` if no category has been specified.
 */
category: {
/**
 * Game/category ID.
 */
id: string;
/**
 * Game/category name.
 */
name: string;} | null;}>;
/**
 * Indicates if the scheduled broadcast is recurring weekly.
 */
is_recurring: boolean;
/**
 * User ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Display name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * If Vacation Mode is enabled, this includes start and end dates for the vacation. If Vacation Mode is disabled, value is set to `null`.
 */
vacation: {
/**
 * Start time for vacation specified in RFC3339 format.
 */
start_time: string;
/**
 * End time for vacation specified in RFC3339 format.
 */
end_time: string;} | null;
}
export type GetChannelStreamScheduleResponse = DataObjectResponse<GetChannelStreamScheduleResponseData> & PaginatedCursorResponse;
export interface GetChannelIcalendarParams {
/**
 * User ID of the broadcaster who owns the channel streaming schedule.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
}
export interface UpdateChannelStreamScheduleParams {
/**
 * User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * Indicates if Vacation Mode is enabled. Set to `true` to add a vacation or `false` to remove vacation from the channel streaming schedule.
 */
is_vacation_enabled?: boolean;
/**
 * Start time for vacation specified in RFC3339 format. Required if `is_vacation_enabled` is set to `true`.
 */
vacation_start_time?: string;
/**
 * End time for vacation specified in RFC3339 format. Required if `is_vacation_enabled` is set to `true`.
 */
vacation_end_time?: string;
/**
 * The timezone for when the vacation is being scheduled using the IANA time zone database format. Required if `is_vacation_enabled` is set to `true`.
 */
timezone?: string;
}
export interface CreateChannelStreamScheduleSegmentParams {
/**
 * User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
}
export interface CreateChannelStreamScheduleSegmentBody {
/**
 * Start time for the scheduled broadcast specified in RFC3339 format.
 */
start_time: string;
/**
 * The timezone of the application creating the scheduled broadcast using the IANA time zone database format.
 */
timezone: string;
/**
 * Indicates if the scheduled broadcast is recurring weekly.
 */
is_recurring: boolean;
/**
 * Duration of the scheduled broadcast in minutes from the `start_time`.
 * 
 * Default: 240.
 */
duration?: string;
/**
 * Game/Category ID for the scheduled broadcast.
 */
category_id?: string;
/**
 * Title for the scheduled broadcast.
 * 
 * Maximum: 140 characters.
 */
title?: string;
}
export interface CreateChannelStreamScheduleSegmentResponseData {
/**
 * Scheduled broadcasts for this stream schedule.
 */
segments: Array<{
/**
 * The ID for the scheduled broadcast.
 */
id: string;
/**
 * Scheduled start time for the scheduled broadcast in RFC3339 format.
 */
start_time: string;
/**
 * Scheduled end time for the scheduled broadcast in RFC3339 format.
 */
end_time: string;
/**
 * Title for the scheduled broadcast.
 */
title: string;
/**
 * Used with recurring scheduled broadcasts. Specifies the date of the next recurring broadcast in RFC3339 format if one or more specific broadcasts have been deleted in the series. Set to `null` otherwise.
 */
canceled_until: string | null;
/**
 * The category for the scheduled broadcast. Set to `null` if no category has been specified.
 */
category: {
/**
 * Game/category ID.
 */
id: string;
/**
 * Game/category name.
 */
name: string;} | null;}>;
/**
 * Indicates if the scheduled broadcast is recurring weekly.
 */
is_recurring: boolean;
/**
 * User ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Display name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * If Vacation Mode is enabled, this includes start and end dates for the vacation. If Vacation Mode is disabled, value is set to `null`.
 */
vacation: {
/**
 * Start time for vacation specified in RFC3339 format.
 */
start_time: string;
/**
 * End time for vacation specified in RFC3339 format.
 */
end_time: string;} | null;
}
export type CreateChannelStreamScheduleSegmentResponse = DataObjectResponse<CreateChannelStreamScheduleSegmentResponseData>;
export interface UpdateChannelStreamScheduleSegmentParams {
/**
 * User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * The ID of the streaming segment to update.
 * 
 * Maximum: 1
 */
id: string;
}
export interface UpdateChannelStreamScheduleSegmentBody {
/**
 * Start time for the scheduled broadcast specified in RFC3339 format.
 */
start_time?: string;
/**
 * Duration of the scheduled broadcast in minutes from the `start_time`.
 * 
 *  Default: 240.
 */
duration?: string;
/**
 * Game/Category ID for the scheduled broadcast.
 */
category_id?: string;
/**
 * Title for the scheduled broadcast.
 * 
 * Maximum: 140 characters.
 */
title?: string;
/**
 * Indicated if the scheduled broadcast is canceled.
 */
is_canceled?: boolean;
/**
 * The timezone of the application creating the scheduled broadcast using the IANA time zone database format.
 */
timezone?: string;
}
export interface UpdateChannelStreamScheduleSegmentResponseData {
/**
 * Scheduled events for this stream schedule.
 */
segments: Array<{
/**
 * The ID for the scheduled event.
 */
id: string;
/**
 * Scheduled start time for the scheduled event in RFC3339 format.
 */
start_time: string;
/**
 * Scheduled end time for the scheduled event in RFC3339 format.
 */
end_time: string;
/**
 * Title for the scheduled event.
 */
title: string;
/**
 * Used with recurring scheduled events. Specifies the date of the next recurring event in RFC3339 format if one or more specific events have been deleted in the series. Set to `null` otherwise.
 */
canceled_until: string | null;
/**
 * The category for the scheduled broadcast. Set to `null` if no category has been specified.
 */
category: {
/**
 * Game/category ID.
 */
id: string;
/**
 * Game/category name.
 */
name: string;} | null;
/**
 * Indicates if the scheduled event is recurring.
 */
is_recurring: boolean;}>;
/**
 * User ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Display name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * If Vacation Mode is enabled, this includes start and end dates for the vacation. If Vacation Mode is disabled, value is set to `null`.
 */
vacation: {
/**
 * Start time for vacation specified in RFC3339 format.
 */
start_time: string;
/**
 * End time for vacation specified in RFC3339 format.
 */
end_time: string;} | null;
}
export type UpdateChannelStreamScheduleSegmentResponse = DataObjectResponse<UpdateChannelStreamScheduleSegmentResponseData>;
export interface DeleteChannelStreamScheduleSegmentParams {
/**
 * User ID of the broadcaster who owns the channel streaming schedule. Provided `broadcaster_id` must match the `user_id` in the user OAuth token.
 * 
 * Maximum: 1
 */
broadcaster_id: string;
/**
 * The ID of the streaming segment to delete.
 */
id: string;
}
export interface SearchCategoriesParams {
/**
 * URl encoded search query
 */
query: string;
/**
 * Maximum number of objects to return.
 * Maximum: 100.
 * Default: 20.
 */
first?: number;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
}
export interface SearchCategoriesResponseData {
/**
 * Template URL for the game’s box art.
 */
box_art_url: string;
/**
 * Game/category name.
 */
name: string;
/**
 * Game/category ID.
 */
id: string;
}
export type SearchCategoriesResponse = DataListResponse<SearchCategoriesResponseData> & PaginatedCursorResponse;
export interface SearchChannelsParams {
/**
 * URl encoded search query
 */
query: string;
/**
 * Maximum number of objects to return.
 * Maximum: 100
 * Default: 20
 */
first?: number;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Filter results for live streams only.
 * Default: false
 */
live_only?: boolean;
}
export interface SearchChannelsResponseData {
/**
 * Channel language
 * (Broadcaster Language field from the Channels service). A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
broadcaster_language: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Display name of the broadcaster.
 */
display_name: string;
/**
 * ID of the game being played on the stream.
 */
game_id: string;
/**
 * Name of the game being played on the stream.
 */
game_name: string;
/**
 * Channel ID.
 */
id: string;
/**
 * Indicates if the channel is currently live.
 */
is_live: boolean;
/**
 * Tag IDs that apply to the stream. This array only contains strings when a channel is live. For all possibilities, see List of All Tags. Category Tags are not returned.
 */
tag_ids: string[];
/**
 * Thumbnail URL of the stream. All image URLs have variable width and height. You can replace {width} and {height} with any values to get that size image.
 */
thumbnail_url: string;
/**
 * Stream title.
 */
title: string;
/**
 * UTC timestamp. Returns an empty string if the channel is not live.
 */
started_at: string;
}
export type SearchChannelsResponse = DataListResponse<SearchChannelsResponseData> & PaginatedCursorResponse;
export interface GetSoundtrackCurrentTrackParams {
/**
 * The ID of the broadcaster that’s playing a Soundtrack track.
 */
broadcaster_id: string;
}
export interface GetSoundtrackCurrentTrackResponseData {
/**
 * The track that’s currently playing.
 */
track: {
/**
 * The album that includes the track.
 */
album: {
/**
 * The album’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * A URL to the album’s cover art.
 */
image_url: string;
/**
 * The album’s name.
 */
name: string;};
/**
 * The artists included on the track.
 */
artist: {
/**
 * The ID of the Twitch user that created the track. Is empty if a Twitch user didn’t create the track.
 */
creator_channel_id: string;
/**
 * The artist’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * The artist’s name. This can be the band’s name or the solo artist’s name.
 */
name: string;};
/**
 * The duration of the track, in seconds.
 */
duration: number;
/**
 * The track’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * The track’s title.
 */
title: string;};
/**
 * The source of the track that’s currently playing. For example, a playlist or station.
 */
source: {
/**
 * The type of content that `id` maps to. Possible values are: 
 * - PLAYLIST
 * - STATION
 */
content_type: {
/**
 * The playlist’s or station’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * A URL to the playlist’s or station’s image art.
 */
image_url: string;
/**
 * A URL to the playlist on Soundtrack. The string is empty if `content-type` is STATION.
 */
soundtrack_url: string;
/**
 * A URL to the playlist on Spotify. The string is empty if `content-type` is STATION.
 */
spotify_url: string;
/**
 * The playlist’s or station’s title.
 */
title: string;};};
}
export type GetSoundtrackCurrentTrackResponse = DataListResponse<GetSoundtrackCurrentTrackResponseData>;
export interface GetSoundtrackPlaylistParams {
/**
 * The ID of the Soundtrack playlist to get.
 */
id: string;
}
export interface GetSoundtrackPlaylistResponseData {
/**
 * A short description about the music that the playlist includes.
 */
description: string;
/**
 * The playlist’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * A URL to the playlist’s image art. Is empty if the playlist doesn't include art.
 */
image_url: string;
/**
 * The playlist’s title.
 */
title: string;
/**
 * The list of tracks in the playlist.
 */
tracks: {
/**
 * The album that includes the track.
 */
album: {
/**
 * The album’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * A URL to the album’s cover art.
 */
image_url: string;
/**
 * The album’s name.
 */
name: string;};
/**
 * The artists included on the track.
 */
artist: {
/**
 * The ID of the Twitch user that created the track. Is empty if a Twitch user didn’t create the track.
 */
creator_channel_id: string;
/**
 * The artist’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * The artist’s name. This can be the band’s name or the solo artist’s name.
 */
name: string;};
/**
 * The duration of the track, in seconds.
 */
duration: number;
/**
 * The track’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * The track’s title.
 */
title: string;};
}
export type GetSoundtrackPlaylistResponse = DataListResponse<GetSoundtrackPlaylistResponseData>;
export interface GetSoundtrackPlaylistsResponseData {
/**
 * A short description about the music that the playlist includes.
 */
description: string;
/**
 * The playlist’s ASIN (Amazon Standard Identification Number).
 */
id: string;
/**
 * A URL to the playlist’s image art. Is empty if the playlist doesn't include art.
 */
image_url: string;
/**
 * The playlist’s title.
 */
title: string;
}
export type GetSoundtrackPlaylistsResponse = DataListResponse<GetSoundtrackPlaylistsResponseData>;
export interface GetStreamKeyParams {
/**
 * User ID of the broadcaster
 */
broadcaster_id: string;
}
export interface GetStreamKeyResponseData {
/**
 * Stream key for the channel
 */
stream_key: string;
}
export type GetStreamKeyResponse = DataListResponse<GetStreamKeyResponseData>;
export interface GetStreamsParams {
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
before?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: number;
/**
 * Returns streams broadcasting a specified game ID. You can specify up to 100 IDs.
 */
game_id?: string;
/**
 * Stream language. You can specify up to 100 languages. A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
language?: string;
/**
 * Returns streams broadcast by one or more specified user IDs. You can specify up to 100 IDs.
 */
user_id?: string;
/**
 * Returns streams broadcast by one or more specified user login names. You can specify up to 100 names.
 */
user_login?: string;
}
export interface GetStreamsResponseData {
/**
 * Stream ID.
 */
id: string;
/**
 * ID of the user who is streaming.
 */
user_id: string;
/**
 * Login of the user who is streaming.
 */
user_login: string;
/**
 * Display name corresponding to `user_id`.
 */
user_name: string;
/**
 * ID of the game being played on the stream.
 */
game_id: string;
/**
 * Name of the game being played.
 */
game_name: string;
/**
 * Stream type: `"live"` or `""` (in case of error).
 */
type: string;
/**
 * Stream title.
 */
title: string;
/**
 * Number of viewers watching the stream at the time of the query.
 */
viewer_count: number;
/**
 * UTC timestamp.
 */
started_at: string;
/**
 * Stream language. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
language: string;
/**
 * Thumbnail URL of the stream. All image URLs have variable width and height. You can replace `{width}` and `{height}` with any values to get that size image
 */
thumbnail_url: string;
/**
 * Shows tag IDs that apply to the stream.
 */
tag_ids: string;
/**
 * Indicates if the broadcaster has specified their channel contains mature content that may be inappropriate for younger audiences.
 */
is_mature: boolean;
}
export type GetStreamsResponse = DataListResponse<GetStreamsResponseData> & PaginatedCursorResponse;
export interface GetFollowedStreamsParams {
/**
 * Results will only include active streams from the channels that this Twitch user follows. `user_id` must match the User ID in the bearer token.
 */
user_id: string;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 100.
 */
first?: number;
}
export interface GetFollowedStreamsResponseData {
/**
 * ID of the game being played on the stream.
 */
game_id: string;
/**
 * Name of the game being played.
 */
game_name: string;
/**
 * Stream ID.
 */
id: string;
/**
 * Stream language. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
language: string;
/**
 * UTC timestamp.
 */
started_at: string;
/**
 * Shows tag IDs that apply to the stream.
 */
tag_ids: string;
/**
 * Thumbnail URL of the stream. All image URLs have variable width and height. You can replace `{width}` and `{height}` with any values to get that size image
 */
thumbnail_url: string;
/**
 * Stream title.
 */
title: string;
/**
 * Stream type: `"live"` or `""` (in case of error).
 */
type: string;
/**
 * ID of the user who is streaming.
 */
user_id: string;
/**
 * Login of the user who is streaming.
 */
user_login: string;
/**
 * Display name corresponding to `user_id`.
 */
user_name: string;
/**
 * Number of viewers watching the stream at the time of the query.
 */
viewer_count: number;
}
export type GetFollowedStreamsResponse = DataListResponse<GetFollowedStreamsResponseData> & PaginatedCursorResponse;
export interface CreateStreamMarkerBody {
/**
 * ID of the broadcaster in whose live stream the marker is created.
 */
user_id: string;
/**
 * Description of or comments on the marker. Max length is 140 characters.
 */
description?: string;
}
export interface CreateStreamMarkerResponseData {
/**
 * RFC3339 timestamp of the marker.
 */
created_at: string;
/**
 * Description of the marker.
 */
description: string;
/**
 * Unique ID of the marker.
 */
id: string;
/**
 * Relative offset (in seconds) of the marker, from the beginning of the stream.
 */
position_seconds: number;
}
export type CreateStreamMarkerResponse = DataListResponse<CreateStreamMarkerResponseData>;
export interface GetStreamMarkersParams {
/**
 * ID of the broadcaster from whose stream markers are returned.
 */
user_id: string;
/**
 * ID of the VOD/video whose stream markers are returned.
 */
video_id: string;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
before?: string;
/**
 * Number of values to be returned when getting videos by user or game ID. Limit: 100. Default: 20.
 */
first?: string;
}
export interface GetStreamMarkersResponseData {
/**
 * ID of the marker.
 */
id: string;
/**
 * RFC3339 timestamp of the marker.
 */
created_at: string;
/**
 * Description of the marker.
 */
description: string;
/**
 * Relative offset (in seconds) of the marker, from the beginning of the stream.
 */
position_seconds: number;
/**
 * A link to the stream with a query parameter that is a timestamp of the marker's location.
 */
URL: string;
/**
 * ID of the user whose markers are returned.
 */
user_id: string;
/**
 * Display name corresponding to `user_id`.
 */
user_name: string;
/**
 * Login corresponding to `user_id`.
 */
user_login: string;
/**
 * ID of the stream (VOD/video) that was marked.
 */
video_id: string;
}
export type GetStreamMarkersResponse = DataListResponse<GetStreamMarkersResponseData> & PaginatedCursorResponse;
export interface GetBroadcasterSubscriptionsParams {
/**
 * User ID of the broadcaster. Must match the User ID in the Bearer token.
 */
broadcaster_id: string;
/**
 * Filters the list to include only the specified subscribers. To specify more than one subscriber, include this parameter for each subscriber. For example, &user_id=1234&user_id=5678. You may specify a maximum of 100 subscribers.
 */
user_id?: string | string[];
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results in a multi-page response. This applies only to queries without `user_id`. If a `user_id` is specified, it supersedes any cursor/offset combinations. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: string;
}
export interface GetBroadcasterSubscriptionsResponseData {
/**
 * User ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Display name of the broadcaster.
 */
broadcaster_name: string;
/**
 * If the subscription was gifted, this is the user ID of the gifter. Empty string otherwise.
 */
gifter_id: string;
/**
 * If the subscription was gifted, this is the login of the gifter. Empty string otherwise.
 */
gifter_login: string;
/**
 * If the subscription was gifted, this is the display name of the gifter. Empty string otherwise.
 */
gifter_name: string;
/**
 * Is true if the subscription is a gift subscription.
 */
is_gift: boolean;
/**
 * Name of the subscription.
 */
plan_name: string;
/**
 * Type of subscription (Tier 1, Tier 2, Tier 3).
 * 1000 = Tier 1, 2000 = Tier 2, 3000 = Tier 3 subscriptions.
 */
tier: string;
/**
 * ID of the subscribed user.
 */
user_id: string;
/**
 * Display name of the subscribed user.
 */
user_name: string;
/**
 * Login of the subscribed user.
 */
user_login: string;
/**
 * The total number of users that subscribe to this broadcaster.
 */
total: number;
/**
 * The current number of subscriber points earned by this broadcaster. Points are based on the subscription tier of each user that subscribes to this broadcaster. For example, a Tier 1 subscription is worth 1 point, Tier 2 is worth 2 points, and Tier 3 is worth 6 points. The number of points determines the number of emote slots that are unlocked for the broadcaster (see Subscriber Emote Slots).
 */
points: number;
}
export type GetBroadcasterSubscriptionsResponse = DataListResponse<GetBroadcasterSubscriptionsResponseData> & PaginatedCursorResponse;
export interface CheckUserSubscriptionParams {
/**
 * User ID of an Affiliate or Partner broadcaster.
 */
broadcaster_id: string;
/**
 * User ID of a Twitch viewer.
 */
user_id: string;
}
export interface CheckUserSubscriptionResponseData {
/**
 * User ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Display name of the broadcaster.
 */
broadcaster_name: string;
/**
 * Indicates if the subscription is a gift.
 */
is_gift: boolean;
/**
 * Login of the gifter (if `is_gift` is `true`).
 */
gifter_login: string;
/**
 * Display name of the gifter (if `is_gift` is `true`).
 */
gifter_name: string;
/**
 * Subscription tier. 1000 is tier 1, 2000 is tier 2, and 3000 is tier 3.
 */
tier: string;
}
export type CheckUserSubscriptionResponse = DataListResponse<CheckUserSubscriptionResponseData>;
export interface GetAllStreamTagsParams {
/**
 * The cursor used to get the next page of results. The `pagination` object in the response contains the cursor’s value.
 * 
 * The `after` and `tag_id` query parameters are mutually exclusive.
 */
after?: string;
/**
 * The maximum number of tags to return per page.
 * 
 * Maximum: 100. Default: 20.
 */
first?: number;
/**
 * An ID that identifies a specific tag to return. Include the query parameter for each tag you want returned. For example, `tag_id=123&tag_id=456`. You may specify a maximum of 100 IDs.
 */
tag_id?: string | string[];
}
export interface GetAllStreamTagsResponseData {
/**
 * An ID that identifies the tag.
 */
tag_id: string;
/**
 * A Boolean value that determines whether the tag is an automatic tag. An automatic tag is one that Twitch adds to the stream. You cannot add or remove automatic tags. The value is `true` if the tag is an automatic tag; otherwise, `false`.
 */
is_auto: boolean;
/**
 * A dictionary that contains the localized names of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized name.
 */
localization_names: Record<string, string>;
/**
 * A dictionary that contains the localized descriptions of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized description.
 */
localization_descriptions: Record<string, string>;
}
export type GetAllStreamTagsResponse = DataListResponse<GetAllStreamTagsResponseData> & PaginatedCursorResponse;
export interface GetStreamTagsParams {
/**
 * The user ID of the channel to get the tags from.
 */
broadcaster_id: string;
}
export interface GetStreamTagsResponseData {
/**
 * An ID that identifies the tag.
 */
tag_id: string;
/**
 * A Boolean value that determines whether the tag is an automatic tag. An automatic tag is one that Twitch adds to the stream. You cannot add or remove automatic tags. The value is `true` if the tag is an automatic tag; otherwise, `false`.
 */
is_auto: boolean;
/**
 * A dictionary that contains the localized names of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized name.
 */
localization_names: Record<string, string>;
/**
 * A dictionary that contains the localized descriptions of the tag. The key is in the form, <locale>-<country/region>. For example, us-en. The value is the localized description.
 */
localization_descriptions: Record<string, string>;
}
export type GetStreamTagsResponse = DataListResponse<GetStreamTagsResponseData>;
export interface ReplaceStreamTagsParams {
/**
 * The user ID of the channel to apply the tags to.
 */
broadcaster_id: string;
}
export interface ReplaceStreamTagsBody {
/**
 * A list of IDs that identify the tags to apply to the channel. You may specify a maximum of five tags.
 * 
 * To remove all tags from the channel, set `tag_ids` to an empty array.
 */
tag_ids?: string[];
}
export interface GetChannelTeamsParams {
/**
 * User ID for a Twitch user.
 */
broadcaster_id: string;
}
export interface GetChannelTeamsResponseData {
/**
 * User ID of the broadcaster.
 */
broadcaster_id: string;
/**
 * Login of the broadcaster.
 */
broadcaster_login: string;
/**
 * Display name of the broadcaster.
 */
broadcaster_name: string;
/**
 * URL for the Team background image.
 */
background_image_url: string;
/**
 * URL for the Team banner.
 */
banner: string;
/**
 * Date and time the Team was created.
 */
created_at: string;
/**
 * Date and time the Team was last updated.
 */
updated_at: string;
/**
 * Team description.
 */
info: string;
/**
 * Image URL for the Team logo.
 */
thumbnail_url: string;
/**
 * Team name.
 */
team_name: string;
/**
 * Team display name.
 */
team_display_name: string;
/**
 * Team ID.
 */
id: string;
}
export type GetChannelTeamsResponse = DataListResponse<GetChannelTeamsResponseData>;
export interface GetTeamsParams {
/**
 * Team name.
 */
name?: string;
/**
 * Team ID.
 */
id?: string;
}
export interface GetTeamsResponseData {
/**
 * Users in the specified Team.
 */
users: {
/**
 * User ID of a Team member.
 */
user_id: string;
/**
 * Login of a Team member.
 */
user_login: string;
/**
 * Display name of a Team member.
 */
user_name: string;};
/**
 * URL of the Team background image.
 */
background_image_url: string;
/**
 * URL for the Team banner.
 */
banner: string;
/**
 * Date and time the Team was created.
 */
created_at: string;
/**
 * Date and time the Team was last updated.
 */
updated_at: string;
/**
 * Team description.
 */
info: string;
/**
 * Image URL for the Team logo.
 */
thumbnail_url: string;
/**
 * Team name.
 */
team_name: string;
/**
 * Team display name.
 */
team_display_name: string;
/**
 * Team ID.
 */
id: string;
}
export type GetTeamsResponse = DataListResponse<GetTeamsResponseData>;
export interface GetUsersParams {
/**
 * User ID. Multiple user IDs can be specified. Limit: 100.
 */
id?: string | string[];
/**
 * User login name. Multiple login names can be specified. Limit: 100.
 */
login?: string | string[];
}
export interface GetUsersResponseData {
/**
 * User’s broadcaster type: `"partner"`, `"affiliate"`, or `""`.
 */
broadcaster_type: string;
/**
 * User’s channel description.
 */
description: string;
/**
 * User’s display name.
 */
display_name: string;
/**
 * User’s ID.
 */
id: string;
/**
 * User’s login name.
 */
login: string;
/**
 * URL of the user’s offline image.
 */
offline_image_url: string;
/**
 * URL of the user’s profile image.
 */
profile_image_url: string;
/**
 * User’s type: `"staff"`, `"admin"`, `"global_mod"`, or `""`.
 */
type: string;
/**
 * Total number of views of the user’s channel.
 */
view_count: number;
/**
 * User’s verified email address. Returned if the request includes the `user:read:email` scope.
 */
email: string;
/**
 * Date when the user was created.
 */
created_at: string;
}
export type GetUsersResponse = DataListResponse<GetUsersResponseData>;
export interface UpdateUserParams {
/**
 * User’s account description
 */
description?: string;
}
export interface GetUsersFollowsParams {
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: number;
/**
 * User ID. The request returns information about users who are being followed by the `from_id` user.
 */
from_id?: string;
/**
 * User ID. The request returns information about users who are following the `to_id` user.
 */
to_id?: string;
}
export interface GetUsersFollowsResponseData {
/**
 * Date and time when the `from_id` user followed the `to_id` user.
 */
followed_at: string;
/**
 * ID of the user following the `to_id` user.
 */
from_id: string;
/**
 * Login of the user following the `to_id` user.
 */
from_login: string;
/**
 * Display name corresponding to `from_id`.
 */
from_name: string;
/**
 * ID of the user being followed by the `from_id` user.
 */
to_id: string;
/**
 * Login of the user being followed by the `from_id` user.
 */
to_login: string;
/**
 * Display name corresponding to `to_id`.
 */
to_name: string;
/**
 * Total number of items returned.
 * - If only `from_id` was in the request, this is the total number of followed users.
 * - If only `to_id` was in the request, this is the total number of followers.
 * - If both `from_id` and `to_id` were in the request, this is 1 (if the "from" user follows the "to" user) or 0.
 */
total: number;
}
export type GetUsersFollowsResponse = DataListResponse<GetUsersFollowsResponseData> & PaginatedCursorResponse;
export interface GetUserBlockListParams {
/**
 * User ID for a Twitch user.
 */
broadcaster_id: string;
/**
 * Maximum number of objects to return. Maximum: 100. Default: 20.
 */
first?: number;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
}
export interface GetUserBlockListResponseData {
/**
 * User ID of the blocked user.
 */
user_id: string;
/**
 * Login of the blocked user.
 */
user_login: string;
/**
 * Display name of the blocked user.
 */
display_name: string;
}
export type GetUserBlockListResponse = DataListResponse<GetUserBlockListResponseData>;
export interface BlockUserParams {
/**
 * User ID of the user to be blocked.
 */
target_user_id: string;
/**
 * Source context for blocking the user. Valid values: `"chat"`, `"whisper"`.
 */
source_context?: string;
/**
 * Reason for blocking the user. Valid values: `"spam"`, `"harassment"`, or `"other"`.
 */
reason?: string;
}
export interface UnblockUserParams {
/**
 * User ID of the user to be unblocked.
 */
target_user_id: string;
}
export interface GetUserExtensionsResponseData {
/**
 * Indicates whether the extension is configured such that it can be activated.
 */
can_activate: boolean;
/**
 * ID of the extension.
 */
id: string;
/**
 * Name of the extension.
 */
name: string;
/**
 * Types for which the extension can be activated. Valid values: `"component"`, `"mobile"`, `"panel"`, `"overlay"`.
 */
type: string[];
/**
 * Version of the extension.
 */
version: string;
}
export type GetUserExtensionsResponse = DataListResponse<GetUserExtensionsResponseData>;
export interface GetUserActiveExtensionsParams {
/**
 * ID of the user whose installed extensions will be returned. Limit: 1.
 */
user_id?: string;
}
export interface GetUserActiveExtensionsResponseData {
/**
 * Contains data for video-component Extensions.
 */
component: Record<string, {
/**
 * Activation state of the extension, for each extension type (component, overlay, mobile, panel). If `false`, no other data is provided.
 */
active: boolean;
/**
 * ID of the extension.
 */
id: string;
/**
 * Name of the extension.
 */
name: string;
/**
 * Version of the extension.
 */
version: string;
/**
 * (Video-component Extensions only) X-coordinate of the placement of the extension.
 */
x: number;
/**
 * (Video-component Extensions only) Y-coordinate of the placement of the extension.
 */
y: number;
}>
/**
 * Contains data for video-overlay Extensions.
 */
overlay: Record<string, {
/**
 * Activation state of the extension, for each extension type (component, overlay, mobile, panel). If `false`, no other data is provided.
 */
active: boolean;
/**
 * ID of the extension.
 */
id: string;
/**
 * Name of the extension.
 */
name: string;
/**
 * Version of the extension.
 */
version: string;
}>
/**
 * Contains data for panel Extensions.
 */
panel: Record<string, {
/**
 * Activation state of the extension, for each extension type (component, overlay, mobile, panel). If `false`, no other data is provided.
 */
active: boolean;
/**
 * ID of the extension.
 */
id: string;
/**
 * Name of the extension.
 */
name: string;
/**
 * Version of the extension.
 */
version: string;
}>
}
export type GetUserActiveExtensionsResponse = DataObjectResponse<GetUserActiveExtensionsResponseData>;
export interface GetVideosParams {
/**
 * ID of the video being queried. Limit: 100. If this is specified, you cannot use any of the optional query parameters below.
 */
id: string | string[];
/**
 * ID of the user who owns the video. Limit 1.
 */
user_id: string;
/**
 * ID of the game the video is of. Limit 1.
 */
game_id: string;
/**
 * Cursor for forward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
after?: string;
/**
 * Cursor for backward pagination: tells the server where to start fetching the next set of results, in a multi-page response. The cursor value specified here is from the `pagination` response field of a prior query.
 */
before?: string;
/**
 * Number of values to be returned when getting videos by user or game ID. Limit: 100. Default: 20.
 */
first?: string;
/**
 * Language of the video being queried. Limit: 1. A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
language?: string;
/**
 * Period during which the video was created. Valid values: `"all"`, `"day"`, `"week"`, `"month"`. Default: `"all"`.
 */
period?: string;
/**
 * Sort order of the videos. Valid values: `"time"`, `"trending"`, `"views"`. Default: `"time"`.
 */
sort?: string;
/**
 * Type of video. Valid values: `"all"`, `"upload"`, `"archive"`, `"highlight"`. Default: `"all"`.
 */
type?: string;
}
export interface GetVideosResponseData {
/**
 * ID of the video.
 */
id: string;
/**
 * ID of the stream that the video originated from if the `type` is `"archive"`. Otherwise set to `null`.
 */
stream_id: string | null;
/**
 * ID of the user who owns the video.
 */
user_id: string;
/**
 * Login of the user who owns the video.
 */
user_login: string;
/**
 * Display name corresponding to `user_id`.
 */
user_name: string;
/**
 * Title of the video.
 */
title: string;
/**
 * Description of the video.
 */
description: string;
/**
 * Date when the video was created.
 */
created_at: string;
/**
 * Date when the video was published.
 */
published_at: string;
/**
 * URL of the video.
 */
url: string;
/**
 * Template URL for the thumbnail of the video.
 */
thumbnail_url: string;
/**
 * Indicates whether the video is publicly viewable. Valid values: `"public"`, `"private"`.
 */
viewable: string;
/**
 * Number of times the video has been viewed.
 */
view_count: number;
/**
 * Language of the video. A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”.
 */
language: string;
/**
 * Type of video. Valid values: `"upload"`, `"archive"`, `"highlight"`.
 */
type: string;
/**
 * Length of the video.
 */
duration: string;
/**
 * Array of muted segments in the video. If there are no muted segments, the value will be `null`.
 */
muted_segments: Array<{
/**
 * Duration of the muted segment.
 */
duration: number;
/**
 * Offset in the video at which the muted segment begins.
 */
offset: number;}> | null;
}
export type GetVideosResponse = DataListResponse<GetVideosResponseData> & PaginatedCursorResponse;
export interface DeleteVideosParams {
/**
 * ID of the video(s) to be deleted. Limit: 5.
 */
id: string | string[];
}
