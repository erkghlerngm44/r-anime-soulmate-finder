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


def _retrieve_submissions(query, subreddit, limit=100):
    # I love pushshift
    params = {
        "q": query,
        "subreddit": subreddit,
        "sort": "desc",
        "limit": limit
    }

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

    ftfs = _retrieve_submissions("Free Talk Fridays",
                                 subreddit="anime", limit=60)

    comments = []

    for ftf in ftfs:
        # Don't use FTFs that were made before the start of the year
        if ftf["created_utc"] < threshold:
            continue

        # Don't make Pushshift servers angry
        time.sleep(5)

        logger.info("Retrieving comment ids for FTF: {} ({})"
                    .format(ftf["title"], ftf["id"]))

        comments.extend(_retrieve_comment_ids(ftf["id"]))

    # Sorry, reddit servers
    return reddit.info(comments)
