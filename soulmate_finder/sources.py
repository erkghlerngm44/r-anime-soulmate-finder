import logging
import time

import praw
import requests

from . import const


logger = logging.getLogger(__package__)


def _pushshift_request(*path, method="GET", **kws):
    path = "/".join(s.strip("/") for s in path)

    url = "{base_url}/{path}".format(base_url=const.PUSHSHIFT.BASE_URL, path=path)

    resp = requests.request(method, url, **kws)

    return resp.json()["data"]


def _retrieve_comment_ids(submission_id):
    # https://www.reddit.com/r/redditdev/comments/5to97v/slug/ddoeedj/
    comments = requests.request(
        "GET",
        const.PUSHSHIFT_ENDPOINTS.COMMENT_IDS.format(submission=submission_id)
    )

    data = comments.json()["data"]

    # See if endpoint returns fullnames. If so, it's fine, if not, we'll have
    # to add the "t1_" (comment type prefix) to each one, and make sure we
    # return it as a list, as `reddit.info` really doesn't like generators.
    if data[0].startswith("t1_"):  # assume if okay for one, it's okay for all
        return data

    return ["t1_" + x for x in data]


def _retrieve_submissions(**params):
    """
    https://goo.gl/mHn7P3

    :param q: The search keyword(s) or phrase
    :param subreddit: Restrict to a specific subreddit
    :param limit: Return up to limit comments
    :param sort: Sort by comment ids in descending or ascending order
    :param after: Show only comments older than epoch date. The API also
        understands m,h,d (i.e. 4h to search the previous 4 hours, etc.)
    """
    # I love pushshift
    submissions = requests.request(
        "GET",
        const.PUSHSHIFT_ENDPOINTS.SUBMISSION_SEARCH,
        params=params
    )
    return submissions.json()["data"]


def _create_reddit_instance():
    return praw.Reddit("reddit", user_agent=const.REDDIT_USER_AGENT)


def comment_stream(subreddit=const.DEFAULTS.STREAM_SUBREDDIT):
    reddit = _create_reddit_instance()

    return reddit.subreddit(subreddit).stream.comments()


def submission(submission_id):
    reddit = _create_reddit_instance()

    comments = _retrieve_comment_ids(submission_id)

    return reddit.info(comments)


def ftfs(limit=const.DEFAULTS.FTF_LIMIT):
    reddit = _create_reddit_instance()

    ftfs = _retrieve_submissions(q="Free Talk Fridays", subreddit="anime",
                                 limit=limit, sort="desc")

    # TODO: Generator?
    comments = []

    for ftf in ftfs:
        # Don't make Pushshift servers angry
        time.sleep(5)

        logger.info("Retrieving comment ids for FTF: {} ({})"
                    .format(ftf["title"], ftf["id"]))

        comments.extend(_retrieve_comment_ids(ftf["id"]))

    logger.debug("Received {} comments".format(len(comments)))

    # Sorry, reddit servers
    return reddit.info(comments)


# Aliases
stream = comment_stream
