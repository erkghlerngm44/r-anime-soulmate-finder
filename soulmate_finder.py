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

verbose = False
search_comment_body = False


regex = "myanimelist\.net/(?:profile|animelist)/([a-z0-9_-]+)"
regex = re.compile(regex, re.I)


# Set the pearson stuff up.
# Too lazy to rename everything and update docs. Sorry
pearson = malaffinity.MALAffinity(round=2)


def vprint(message, end="\n"):
    if verbose:
        print(message, end=end)
    return


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

    # stdout's too time taxing. Might as well save some
    # time and only display this only when this script comes across
    # a user that hasn't already been processed.
    print("Processing User: {}".format(author_name))

    text = comment.author_flair_text

    if not text:
        vprint("- No flair text.", end=" ")

        # Search the comment body if the var is True
        if search_comment_body and comment.body:
            # Just set text to the comment body to avoid having to
            # rewrite this whole section
            vprint("Searching comment body...")
            text = comment.body

        else:
            vprint("Skipping...")
            return

    match = regex.search(text)

    if not match:
        vprint("- Can't find MAL username. Skipping...")
        return

    username = match.group(1)

    # Halt so MAL doesn't get angry if we make too many calls to their
    # server in a short amount of time.
    time.sleep(wait_between_requests)

    # Two attempts, then give up. Adjust max tries here.
    # TODO: Better way of doing this?
    for _ in range(2):
        try:
            affinity, shared = pearson.calculate_affinity(username)

        except malaffinity.MALRateLimitExceededError:
            vprint("- MAL's blocking us. Halting for a few seconds...")
            # TODO: Fix unnecessary waiting on two failed requests.
            time.sleep(retry_after_failed_request)

        except:
            vprint("- Affinity can't be calculated. Skipping...")
            return

        else:
            break

    affinities[author_name] = {
        "reddit": author_name,
        "mal": username,
        "affinity": affinity,
        "shared": shared
    }

    vprint("- Calculated affinity: {}%".format(affinity))

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
    parser = argparse.ArgumentParser(description="/r/anime soulmate finder")

    # Comment source
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-c", "--stream",
        help="use the comment stream as the comment source",
        action="store_true"
    )
    group.add_argument(
        "-s", "--submission",
        help="use the comments in a submission as the comment source"
    )

    # Extra options
    parser.add_argument(
        "-b", "--search-comment-body",
        help="search the comment body for a mal url as well as the user's flair",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="be more verbose (print more about what's going on)",
        action="store_true"
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

    # Change the extra options globals
    verbose = args.verbose
    search_comment_body = args.search_comment_body

    # Run it.
    main(comments)
