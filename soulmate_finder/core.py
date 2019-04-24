#!/usr/bin/env python3


import argparse
import logging
import re
import time

import aniffinity
import unicodecsv as csv

from . import const
from . import sources
DEFAULTS = const.DEFAULTS


# Version
__version__ = const.VERSION


# Set up the logger
logging.basicConfig(format=const.LOGGING_FORMAT, level=logging.INFO)
logger = logging.getLogger(__package__)


regex = re.compile(const.REGEX, re.I)


# Affinity stuff
pearson = aniffinity.Aniffinity(round=const.ROUND_AFFINITIES_TO)


def handle_comment(comment, writer, search_comment_body=DEFAULTS.SEARCH_COMMENT_BODY):
    """
    :param comment: praw.models.Comment comment
    :param writer: csv.DictWriter writer
    :param bool search_comment_body: search comment body for mal url
        if no flair?
    """
    # We can't take the easy option of passing `**extra_options` to this
    # as well, as it'd have to look up the `search_comment_body` value in
    # the dict every time it processes a comment, which isn't very efficient
    # and will slow the script down.
    author_name = comment.author.name

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
            # FIXME: Need something here, maybe a URL regex match
            # text = comment.body

        else:
            logger.debug("- Skipping...")
            return

    if not re.match(r"https?://", text):
        logger.debug("- Can't find URL. Skipping...")
        return

    # Halt so the service doesn't get angry if we make too many calls
    # to their server in a short amount of time.
    time.sleep(const.WAIT_BETWEEN_REQUESTS)

    # Two attempts, then give up. Adjust max tries here.
    # TODO: Better way of doing this?
    success = False

    for _ in range(2):
        try:
            affinity, shared = pearson.calculate_affinity(text)

        except aniffinity.exceptions.RateLimitExceededError:
            logger.warning("- Service is blocking us. "
                           "Halting for a few seconds...")
            time.sleep(const.RETRY_AFTER_FAILED_REQUEST)
            continue

        except aniffinity.exceptions.AniffinityException as e:
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

    # We don't need to worry about `aniffinity.InvalidUserError` here,
    # because, if it were going to be raised, it would have been raised in the
    # code above, caught appropriately, and this bit wouldn't be executed.
    username, service = aniffinity.resolver.resolve_user(text)
    username = "{}:{}".format(service, username)

    logger.debug("- Calculated affinity: {}%".format(affinity))

    return writer.writerow({
        "reddit": author_name,
        "username": username,
        "affinity": affinity,
        "shared": shared
    })


def main(comments, **extra_opts):
    """
    :param comments: comments that can be iterated over
    :param bool buffer_size: file buffer size in bytes
    :param bool quiet: be more quiet. mutually exclusive with `verbose`
    :param bool search_comment_body: search comment body for mal url
        if no flair?
    :param int timeout: timeout after n seconds if comment source hasn't
        already been depleted
    :param bool verbose: be more talkative. mutually exclusive with `quiet`
    """
    # Assign default values if options not specified
    buffer_size = extra_opts.get("buffer_size", DEFAULTS.BUFFER_SIZE)
    search_comment_body = extra_opts.get("search_comment_body",
                                         DEFAULTS.SEARCH_COMMENT_BODY)
    timeout = extra_opts.get("timeout", DEFAULTS.TIMEOUT)

    # Logging level change, either to print more out, print less out,
    # or do nothing, based on `verbose` and `quiet` var values
    quiet = extra_opts.get("quiet", DEFAULTS.QUIET)
    verbose = extra_opts.get("verbose", DEFAULTS.VERBOSE)

    # Set logging level to `DEBUG` if verbose flag specified
    if quiet:
        logger.setLevel(logging.ERROR)
    elif verbose:
        logger.setLevel(logging.DEBUG)

    processed = set()

    # Open the affinities file if it exists.
    file = open("affinities.csv", "a+b", buffering=buffer_size)
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
        file.flush()

    start_time = time.time()

    try:
        for comment in comments:
            if (time.time() - start_time) >= timeout:
                # Timeout exceeded. Stop processing any more comments
                logger.info("Timeout exceeded. Not processing any more comments.")
                break

            if not comment.author or comment.author.name in processed:
                continue

            processed.add(comment.author.name)

            handle_comment(comment, writer, search_comment_body)

    except KeyboardInterrupt:
        logger.info("\n\n" + "KeyboardInterrupt.")

    except Exception as e:
        logger.error("Error: {}".format(e))
        logger.exception(e)

    else:
        # Will only run if using comments from a submission or FTFs.
        # If processing from comment stream, KeyboardInterrupt
        # is the only way out.
        logger.info("\n\n" + "Processed all users.")

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
