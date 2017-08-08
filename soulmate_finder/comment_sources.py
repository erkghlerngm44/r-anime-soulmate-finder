import datetime
import logging
import time

import praw
import requests


logger = logging.getLogger(__package__)


def _retrieve_comment_ids(submission_id):
    # https://www.reddit.com/r/redditdev/comments/5to97v/slug/ddoeedj/
    comments = requests.request(
        "GET",
        "http://apiv2.pushshift.io/reddit/get/comment_ids/{}"
        .format(submission_id)
    )
    return comments.json()["data"]


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
        "https://apiv2.pushshift.io/reddit/submission/search/",
        params=params
    )
    return submissions.json()["data"]


def _create_reddit_instance():
    return praw.Reddit("reddit")


def get_comment_stream():
    reddit = _create_reddit_instance()

    return reddit.subreddit("anime").stream.comments()


def get_comments_from_submission(submission_id):
    reddit = _create_reddit_instance()

    comments = _retrieve_comment_ids(submission_id)

    return reddit.info(comments)


def get_comments_from_ftfs():
    reddit = _create_reddit_instance()

    # FIXME: This is so misplaced
    # TODO: MAKE THIS LESS SHIT
    d = datetime.date.today()
    e = datetime.date(d.year, 1, 1)

    threshold = time.mktime(e.timetuple())
    # Force to int because reasons
    threshold = int(threshold)

    ftfs = _retrieve_submissions(q="Free Talk Fridays", subreddit="anime",
                                 limit=60, sort="desc", after=threshold)

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
