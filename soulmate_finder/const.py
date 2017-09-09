VERSION = "4.0.0"

class DEFAULTS:  # noqa: E302
    BUFFER_SIZE = 512
    FTF_LIMIT = 5
    QUIET = False
    SEARCH_COMMENT_BODY = False
    VERBOSE = False

HEADERS = ["reddit", "mal", "affinity", "shared"]  # noqa: E305

LOGGING_FORMAT = "%(message)s"

class PUSHSHIFT_ENDPOINTS:  # noqa: E302
    COMMENT_IDS = "https://api.pushshift.io/reddit/submission/comment_ids/{submission}"  # noqa: E501
    SUBMISSION_SEARCH = "https://api.pushshift.io/reddit/submission/search/"

REGEX = "myanimelist\.net/(?:profile|animelist)/([a-z0-9_-]+)"  # noqa: E305

ROUND_AFFINITIES_TO = 2

REDDIT_USER_AGENT = "script:/r/anime soulmate finder v{}".format(VERSION)

WAIT_BETWEEN_REQUESTS = 2
RETRY_AFTER_FAILED_REQUEST = 5
