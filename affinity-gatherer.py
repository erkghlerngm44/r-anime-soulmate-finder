#!/usr/bin/env python3


import argparse
import copy
import csv
import os
import re
import time

import bs4
import praw
import requests
import scipy
import scipy.stats


wait_between_requests = 2
retry_after_failed_request = 5

regex = "myanimelist\.net/(?:profile|animelist)/([a-z0-9_-]+)"
regex = re.compile(regex, re.I)


# mal_pearson module squished into a class.
class Pearson:
    _url = "https://myanimelist.net/malappinfo.php"
    scores = {}

    def _retrieve_list(self, username, status="all", type="anime"):
        params = {
            "u": username,
            "status": status,
            "type": type
        }

        resp = requests.request("GET", self._url, params=params).content

        return bs4.BeautifulSoup(resp, "html.parser")

    def init(self, base_user):
        """
        Get the base user's list and create the 'base scores'
        dict that other people's scores will be compared to.
        """

        ownlist   = self._retrieve_list(base_user)
        all_anime = ownlist.findAll("anime")

        for anime in all_anime:
            id = anime.series_animedb_id.string
            id = int(id)

            score = anime.my_score.string
            score = int(score)

            if score > 0:
                self.scores[id] = [score]

    def pearson(self, username):
        """
        Get the r of the base user's scores and someone elses.

        Will return 'r' in the range -1 <= r <= 1, where -1 is
        negative correlation and 1 is perfect correlation.

        Multiplying 'r' by 100 and rounding to 1dp will
        give you the MAL affinity.
        """

        # Create a copy of the scores.
        scores_copy = copy.deepcopy(self.scores)

        theirlist = self._retrieve_list(username)
        all_anime = theirlist.findAll("anime")

        if not len(all_anime):
            return None

        for anime in all_anime:
            id = anime.series_animedb_id.string
            id = int(id)

            score = anime.my_score.string
            score = int(score)

            if score > 0:
                if id in scores_copy:
                    scores_copy[id].append(score)

        # Forced to list so no errors when deleting keys.
        for key in list(scores_copy.keys()):
            if not len(scores_copy[key]) == 2:
                del scores_copy[key]

        # Handle cases where the shared score is <= 10, so affinity can not be
        # accurately calculated. Should return NaN if this is the case.
        if len(scores_copy) <= 10:
            return scipy.nan

        scores1 = []
        scores2 = []

        for key in scores_copy:
            arr = scores_copy[key]

            scores1.append(arr[0])
            scores2.append(arr[1])

        pearson = scipy.stats.pearsonr(scores1, scores2)

        return pearson[0]


# Set the pearson stuff up.
pearson = Pearson()


def create_reddit_instance():
    return praw.Reddit("reddit")

def get_comment_stream():
    reddit = create_reddit_instance()

    return reddit.subreddit("anime").stream.comments()

def get_comments_from_submission(submission_id):
    reddit = create_reddit_instance()

    # https://www.reddit.com/r/redditdev/comments/5to97v/slug/ddoeedj/
    comments = requests.request(
        "GET",
        "http://apiv2.pushshift.io/reddit/get/comment_ids/{}"
            .format(submission_id)
    )
    comments = comments.json()
    comments = comments["data"]

    return reddit.info(comments)


def handle_comment(comment):
    if not comment.author:
        return

    author_name = comment.author.name

    if author_name in processed:
        return

    processed.add(author_name)

    print("Processing User: {}".format(author_name))

    flair_text = comment.author_flair_text

    if not flair_text:
        print("- No flair text. Skipping...")
        return

    match = regex.search(flair_text)

    if not match:
        print("- Can't find MAL username. Skipping...")
        return

    username = match.group(1)

    # Halt so MAL doesn't get angry if we make too many calls to their
    # server in a short amount of time.
    time.sleep(wait_between_requests)

    affinity = pearson.pearson(username)

    if not affinity:
        print("- No affinity. Halting for a few seconds...")
        time.sleep(retry_after_failed_request)
        affinity = pearson.pearson(username)

        if not affinity:
            # MAL account the user specified probably doesn't exist.
            print("- Still no affinity. [](#yuishrug)")
            return

    # NaN affinity check.
    if affinity != affinity:
        print("- NaN affinity. Shared count is too low. Skipping...")
        return

    affinity *= 100
    affinity = round(affinity, 2)

    affinities[author_name] = {
        "reddit": author_name,
        "mal": username,
        "affinity": affinity
    }

    print("- Calculated affinity: {}%".format(affinity))

    return


def main(comments):
    global processed
    global affinities

    processed  = set()
    affinities = {}

    # Open the affinities file if it exists.
    if os.path.isfile("affinities.csv"):
        with open("affinities.csv", "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                user = row["reddit"]
                processed.add(user)

                affinities[user] = row

    start_time = time.time()

    while True:
        try:
            for comment in comments:
                handle_comment(comment)
            # Will only get called if using comments from a submission.
            # If processing from comment stream, KeyboardInterrupt
            # is the only way out.
            print("\n\n" + "Processed all users. Breaking loop...")
            break

        except KeyboardInterrupt:
            print("\n\n" + "KeyboardInterrupt. Breaking loop...")
            break

        except Exception as e:
            print("Error: {}".format(e))
            time.sleep(30)

    end_time = time.time()

    runtime = round(end_time - start_time)

    # Is "affinities" a word?
    print("Script runtime: {} seconds".format(runtime))
    print("Total affinities calculated: {}".format( len(affinities) ))

    print("\n" + "Dumping to file...")

    # Nicely write data to CSV.
    with open("affinities.csv", "w") as file:
        headers = ["reddit", "mal", "affinity"]

        writer = csv.DictWriter(file, fieldnames=headers, lineterminator="\n")
        writer.writeheader()

        affinities_sorted = sorted(
            affinities.items(),
            key = lambda x: float( x[1]["affinity"] ),
            reverse = True
        )

        for user, data in affinities_sorted:
            writer.writerow(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Affinity Gatherer")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-stream",
        help="use the comment stream as the comment source",
        action="store_true"
    )
    group.add_argument(
        "-submission",
        help="use the comments in a submission as the comment source"
    )

    parser.add_argument("mal_username")

    args = parser.parse_args()

    # Set pearson stuff up.
    pearson.init(args.mal_username)

    # Choose either comment stream or comments from submission.
    if args.stream:
        comments = get_comment_stream()
    elif args.submission:
        comments = get_comments_from_submission(args.submission)

    # Run it.
    main(comments)
