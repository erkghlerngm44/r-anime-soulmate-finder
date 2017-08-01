import datetime
import time

import praw
import requests


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

    ftfs = _retrieve_submissions("Free Talk Fridays", subreddit="anime")

    comments = []

    for ftf in ftfs:
        # Don't make Pushshift servers angry
        time.sleep(5)

        print("Retrieving comment ids for FTF: {}".format(ftf["title"]))

        comments.extend(_retrieve_comment_ids(ftf["id"]))

    # Sorry, reddit servers
    return reddit.info(comments)
