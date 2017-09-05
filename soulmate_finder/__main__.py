#!/usr/bin/env python3


import argparse
import logging
import re
import time

import malaffinity
import unicodecsv as csv

from . import const
from .comment_sources import (
    get_comment_stream,
    get_comments_from_ftfs,
    get_comments_from_submission
)
DEFAULTS = const.DEFAULTS


# Version
__version__ = const.VERSION


# Set up the logger
logging.basicConfig(format=const.LOGGING_FORMAT, level=logging.INFO)
logger = logging.getLogger(__package__)


regex = re.compile(const.REGEX, re.I)


# Set the pearson stuff up.
# Too lazy to rename everything and update docs. Sorry
pearson = malaffinity.MALAffinity(round=const.ROUND_AFFINITIES_TO)


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

    logger.debug("- Calculated affinity: {}%".format(affinity))

    return writer.writerow({
        "reddit": author_name,
        "mal": username,
        "affinity": affinity,
        "shared": shared
    })


def main(comments):
    # TODO: GET RID OF THE BLOODY GLOBALS
    global processed
    global writer

    processed = set()

    # Open the affinities file if it exists.
    file = open("affinities.csv", "a+b", buffering=256)
    writer = csv.DictWriter(file, fieldnames=const.HEADERS,
                            lineterminator="\n")

    if file.tell():
        # File not empty, retrieve already calculated affinities
        # and store usernames
        file.seek(0)
        # TODO: Do we really need to do this?
        reader = csv.DictReader(file)

        for row in reader:
            user = row["reddit"]
            processed.add(user)
    else:
        # File empty, write headers in
        writer.writeheader()

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

    # Just in case there's still some in the buffer
    file.flush()

    end_time = time.time()

    runtime = round(end_time - start_time)

    logger.info("Script runtime: {} seconds".format(runtime))
    logger.info("Sorting file...")

    # Seek to the start and read off the file to get all affinities
    # and sort them
    file.seek(0)
    reader = csv.DictReader(file)
    sorted_data = sorted(reader, key=lambda d: float(d["affinity"]),
                         reverse=True)

    # Kill the file so we can reopen it later and overwrite it all
    file.close()

    with open("affinities.csv", "wb") as file:
        writer = csv.DictWriter(file, fieldnames=const.HEADERS,
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted_data)

    logger.info("Total affinities calculated: {}".format(len(sorted_data)))


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
              "from the current one (default 5)"),
        metavar="LIMIT",
        nargs="?", const=DEFAULTS.FTF_LIMIT
    )

    # Verbose/quiet option
    group2 = parser.add_mutually_exclusive_group(required=False)
    group2.add_argument(
        "-v", "--verbose",
        help="be more verbose (print more about what's going on)",
        action="store_true",
        default=DEFAULTS.VERBOSE
    )
    group2.add_argument(
        "-q", "--quiet",
        help="quiet (silent) mode (only display errors)",
        action="store_true",
        default=DEFAULTS.QUIET
    )

    # Extra options
    parser.add_argument(
        "-b", "--search-comment-body",
        help="search the comment body for a mal url if a user "
             "doesn't have a flair",
        action="store_true",
        default=DEFAULTS.SEARCH_COMMENT_BODY
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
