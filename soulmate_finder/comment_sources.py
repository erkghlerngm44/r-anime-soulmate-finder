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
    subreddit = reddit.subreddit("anime")

    # Manually look up for FTFs because it seems the search function misses
    # some of them out sometimes. Dunno why, probably something on their side.
    # The search function is rubbish anyway so it's hardly surprising...
    # TODO: better var names
    d = datetime.date.today()
    e = datetime.date(d.year, 1, 1)

    comments = []

    # TODO: check this works properly
    # TODO: There has to be a better way of doing this...
    # TODO: Clean this up
    while d > e:
        # Friday check. Friday = index 4
        # TODO: Make this easier to understand
        if d.weekday() % 7 == 4:
            # Tis a friday. Form the title
            # "Free Talk Fridays - Week of MONTH DATE, YEAR"
            ftf_title = d.strftime("Free Talk Fridays - Week of %B %d, %Y")

            # Try not to make Reddit and Pushshift's servers angry
            time.sleep(2)

            done = False
            # WHY CAN'T YOU JUST WORK, REDDIT SEARCH, YOU PILE OF SHITE
            while not done:
                try:
                    print("Retrieving comment ids for FTF: {}...".format(ftf_title))

                    ftf = subreddit.search(ftf_title)
                    ftf = list(ftf)[0]

                    # Add comment ids to the comments list
                    comments += _retrieve_comment_ids(ftf.id)
                except:
                    print(
                        "ERR: Failed to retrieve comment ids for FTF: {}. "
                        "Retrying in 30 seconds."
                        .format(ftf_title)
                    )
                    time.sleep(30)
                else:
                    done = True

        # Decrease the day
        d -= datetime.timedelta(days=1)

    # Sorry, reddit servers
    return reddit.info(comments)
