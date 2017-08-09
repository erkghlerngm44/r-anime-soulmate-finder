#!/usr/bin/env python3


import argparse
import csv
import logging
import os
import re
import time

import malaffinity

from . import const
from .comment_sources import (
    get_comment_stream,
    get_comments_from_ftfs,
    get_comments_from_submission
)


# Version
__version__ = const.version


# Set up the logger
logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__package__)


regex = re.compile(const.REGEX, re.I)


# Set the pearson stuff up.
# Too lazy to rename everything and update docs. Sorry
pearson = malaffinity.MALAffinity(round=2)


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
    logger.info("Processing User: {}".format(author_name))

    text = comment.author_flair_text

    if not text:
        logger.debug("- No flair text.")

        # Search the comment body if the var is True
        if search_comment_body and comment.body:
            # Just set text to the comment body to avoid having to
            # rewrite this whole section
            logger.debug("- Searching comment body...")
            text = comment.body

        else:
            logger.debug("- Skipping...")
            return

    match = regex.search(text)

    if not match:
        logger.debug("- Can't find MAL username. Skipping...")
        return

    username = match.group(1)

    # Halt so MAL doesn't get angry if we make too many calls to their
    # server in a short amount of time.
    time.sleep(const.WAIT_BETWEEN_REQUESTS)

    # Two attempts, then give up. Adjust max tries here.
    # TODO: Better way of doing this?
    success = False

    for _ in range(2):
        try:
            affinity, shared = pearson.calculate_affinity(username)

        except malaffinity.exceptions.MALRateLimitExceededError:
            logger.warning("- MAL's blocking us. "
                           "Halting for a few seconds...")
            time.sleep(const.RETRY_AFTER_FAILED_REQUEST)
            continue

        except malaffinity.exceptions.MALAffinityException as e:
            logger.debug("- Affinity can't be calculated (`{}`). Skipping..."
                         .format(e))
            break

        except Exception as e:
            logger.error("- Exception caught: `{}`. Skipping...".format(e))
            break

        else:
            success = True
            break

    # Failed for some reason
    if not success:
        return

    writer.writerow({
        "reddit": author_name,
        "mal": username,
        "affinity": affinity,
        "shared": shared
    })
    # Flush so progress is saved... progressively?
    file.flush()

    logger.debug("- Calculated affinity: {}%".format(affinity))

    return


def main(comments):
    global processed
    processed = set()

    headers = ["reddit", "mal", "affinity", "shared"]

    # Open the affinities file if it exists.
    if os.path.isfile("affinities.csv"):
        with open("affinities.csv", "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                user = row["reddit"]
                processed.add(user)
    else:
        # Create the file now
        with open("affinities.csv", "w") as f:
            w = csv.DictWriter(f, fieldnames=headers, lineterminator="\n")
            w.writeheader()

    # Now open the file up for appending, and make the `DictWriter` a global
    # so `handle_comment` can access it.
    # TODO: GET RID OF THE BLOODY GLOBALS
    global file
    global writer

    file = open("affinities.csv", "a")
    writer = csv.DictWriter(file, fieldnames=headers, lineterminator="\n")

    start_time = time.time()

    while True:
        try:
            for comment in comments:
                handle_comment(comment)
            # Will only get called if using comments from a submission.
            # If processing from comment stream, KeyboardInterrupt
            # is the only way out.
            logger.info("\n\n" + "Processed all users. Breaking loop...")
            break

        except KeyboardInterrupt:
            logger.info("\n\n" + "KeyboardInterrupt. Breaking loop...")
            break

        except Exception as e:
            logger.error("Error: {}".format(e))
            time.sleep(30)

    # Kill the file so we can open it later
    file.close()

    end_time = time.time()

    runtime = round(end_time - start_time)

    # Is "affinities" a word?
    logger.info("Script runtime: {} seconds".format(runtime))
    # TODO: Check we can still do this with the new method
    # print("Total affinities calculated: {}".format( len(affinities) ))

    logger.info("\n" + "Sorting file...")

    # Sort the affinities and write to file
    with open("affinities.csv", "r") as f:
        reader = csv.DictReader(f)
        sorted_data = sorted(
            reader,
            key=lambda d: float(d["affinity"]),
            reverse=True
        )

    with open("affinities.csv", "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=reader.fieldnames,
            lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(sorted_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="/r/anime soulmate finder")

    parser.add_argument("mal_username")

    # Comment source
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-c", "--stream",
        help="use the comment stream as the comment source",
        action="store_true"
    )
    group.add_argument(
        "-s", "--submission",
        help="use the comments in a submission as the comment source",
        metavar="SUBMISSION_ID"
    )
    group.add_argument(
        "-f", "--ftf",
        help=("use the comments in ftfs as the comment source. "
              "`LIMIT` specifies how many ftfs to use, working backwards "
              "from the current one (default 10)"),
        metavar="LIMIT",
        nargs="?", const=10
    )

    # Verbose/quiet option
    group2 = parser.add_mutually_exclusive_group(required=False)
    group2.add_argument(
        "-v", "--verbose",
        help="be more verbose (print more about what's going on)",
        action="store_true",
        default=False
    )
    group2.add_argument(
        "-q", "--quiet",
        help="quiet (silent) mode (only display errors)",
        action="store_true",
        default=False
    )

    # Extra options
    parser.add_argument(
        "-b", "--search-comment-body",
        help="search the comment body for a mal url if a user "
             "doesn't have a flair",
        action="store_true",
        default=False
    )

    args = parser.parse_args()

    # Set pearson stuff up.
    pearson.init(args.mal_username)

    # Set logging level to `DEBUG` if verbose flag specified
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)

    # Choose either comment stream or comments from submission.
    if args.stream:
        comments = get_comment_stream()
    elif args.submission:
        comments = get_comments_from_submission(args.submission)
    elif args.ftf:
        comments = get_comments_from_ftfs(args.ftf)

    # Change the extra options globals
    search_comment_body = args.search_comment_body

    # Run it.
    main(comments)
