from .core import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="/r/anime soulmate finder")

    parser.add_argument("-u", "--user",
                        help="your username and service", nargs=2,
                        metavar=("USERNAME", "SERVICE"), required=True)

    # https://stackoverflow.com/a/45602952
    # Comment source
    group = parser.add_argument_group(
        "comment sources",
        "source of comments, which will be processed"
    )
    mxg = group.add_mutually_exclusive_group(required=True)
    mxg.add_argument(
        "-c", "--stream",
        help="use the /r/anime comment stream as the comment source",
        action="store_const", const=DEFAULTS.STREAM_SUBREDDIT
    )
    mxg.add_argument(
        "-s", "--submission",
        help=("use the comments in a submission as the comment source. "
              "`SUBMISSION_ID` is the reddit submission id (6 letter "
              "alphanumeric code between the '/comments/' and the thread "
              "title in the comments url, e.g. "
              "/r/anime/comments/{{CODE}}/free_talk_fridays...)"),
        metavar="SUBMISSION_ID", type=str
    )
    mxg.add_argument(
        "-f", "--ftf",
        help=("use the comments in ftfs as the comment source. "
              "`LIMIT` specifies how many ftfs to use, working backwards "
              "from the current one (default: 1)"),
        metavar="LIMIT",
        nargs="?", const=DEFAULTS.FTF_LIMIT, type=int
    )

    # Verbose/quiet option
    group2 = parser.add_argument_group(
        "logging/print options",
        "controls the level of verbosity for this script"
    )
    mxg2 = group2.add_mutually_exclusive_group(required=False)
    mxg2.add_argument(
        "-v", "--verbose",
        help="be more talkative (print more about what's going on)",
        action="store_true",
        default=DEFAULTS.VERBOSE
    )
    mxg2.add_argument(
        "-q", "--quiet",
        help="quiet (silent) mode (only display errors)",
        action="store_true",
        default=DEFAULTS.QUIET
    )

    # Extra options
    group3 = parser.add_argument_group("extra options")
    group3.add_argument(
        "-b", "--search-comment-body",
        help=("search the comment body for a mal url if a user "
              "doesn't have a flair"),
        action="store_true",
        default=DEFAULTS.SEARCH_COMMENT_BODY
    )
    group3.add_argument(
        "-z", "--buffer-size",
        help=("buffer size of file to write to, in bytes. dictates how many "
              "bytes to hold in buffer before writing to file (default: 512)."
              " assume the average row to be written is around 30-35 bytes"),
        metavar="SIZE", default=DEFAULTS.BUFFER_SIZE, type=int
    )
    group3.add_argument(
        "-t", "--timeout",
        help=("terminate the script after a specified amount of time "
              "(in seconds), if the comment source hasn't already been "
              "fully processed by then (default: never)"),
        default=DEFAULTS.TIMEOUT, type=int
    )

    args = parser.parse_args()

    # Set pearson stuff up.
    pearson.init(tuple(args.user))

    # Choose either comment stream or comments from submission.
    if args.stream:
        comments = sources.comment_stream(args.stream)
    elif args.submission:
        comments = sources.submission(args.submission)
    elif args.ftf:
        comments = sources.ftfs(args.ftf)

    # Run it.
    main(comments, **vars(args))
