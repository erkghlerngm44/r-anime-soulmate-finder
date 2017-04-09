#!/usr/bin/env python3


import argparse
import csv
import os
import re
import time

import malaffinity
import praw
import requests


wait_between_requests = 2
retry_after_failed_request = 5

regex = "myanimelist\.net/(?:profile|animelist)/([a-z0-9_-]+)"
regex = re.compile(regex, re.I)


# Set the pearson stuff up.
# Too lazy to rename everything and update docs. Sorry
pearson = malaffinity.MALAffinity(round=2)


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

    try:
        affinity, shared = pearson.calculate_affinity(username)

    except malaffinity.MALRateLimitExceededError:
        print("- MAL's blocking us. Halting for a few seconds...")
        time.sleep(retry_after_failed_request)

        try:
            affinity, shared = pearson.calculate_affinity(username)
        except:
            print("- Still no affinity. [](#yuishrug)")
            return

    except:
        print("- Affinity can't be calculated. Skipping...")
        return

    affinities[author_name] = {
        "reddit": author_name,
        "mal": username,
        "affinity": affinity,
        "shared": shared
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
        headers = ["reddit", "mal", "affinity", "shared"]

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
