VERSION = "4.0.0"

class DEFAULTS:  # noqa: E302
    FTF_LIMIT = 5
    VERBOSE = False
    QUIET = False
    SEARCH_COMMENT_BODY = False

HEADERS = ["reddit", "mal", "affinity", "shared"]

LOGGING_FORMAT = "%(message)s"

REGEX = "myanimelist\.net/(?:profile|animelist)/([a-z0-9_-]+)"

ROUND_AFFINITIES_TO = 2

WAIT_BETWEEN_REQUESTS = 2
RETRY_AFTER_FAILED_REQUEST = 5

class PUSHSHIFT_ENDPOINTS:  # noqa: E302
    COMMENT_IDS = "https://api.pushshift.io/reddit/submission/comment_ids/{submission}"  # noqa: E501
    SUBMISSION_SEARCH = "https://apiv2.pushshift.io/reddit/submission/search/"
