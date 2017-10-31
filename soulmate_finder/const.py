VERSION = "5.0.0.dev0"


class DEFAULTS:
    BUFFER_SIZE = 512
    FTF_LIMIT = 1
    QUIET = False
    SEARCH_COMMENT_BODY = False
    TIMEOUT = 9e999  # (inf)
    VERBOSE = False

HEADERS = ["reddit", "mal", "affinity", "shared"]

LOGGING_FORMAT = "%(message)s"

class PUSHSHIFT_ENDPOINTS:
    COMMENT_IDS = "https://api.pushshift.io/reddit/submission/comment_ids/{submission}"
    SUBMISSION_SEARCH = "https://api.pushshift.io/reddit/submission/search/"

REDDIT_USER_AGENT = "script:/r/anime soulmate finder v{}".format(VERSION)

REGEX = "myanimelist\.net/(?:profile|animelist)/([a-z0-9_-]+)"

ROUND_AFFINITIES_TO = 2

WAIT_BETWEEN_REQUESTS = 2
RETRY_AFTER_FAILED_REQUEST = 5
