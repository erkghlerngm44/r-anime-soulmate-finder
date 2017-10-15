# r-anime-soulmate-finder

[![GitHub release](https://img.shields.io/github/release/erkghlerngm44/r-anime-soulmate-finder.svg)](https://github.com/erkghlerngm44/r-anime-soulmate-finder/releases)
[![Github commits (since latest release)](https://img.shields.io/github/commits-since/erkghlerngm44/r-anime-soulmate-finder/latest.svg)]()
[![PyUp](https://pyup.io/repos/github/erkghlerngm44/r-anime-soulmate-finder/shield.svg)](https://pyup.io/repos/github/erkghlerngm44/r-anime-soulmate-finder/)
[![license](https://img.shields.io/github/license/erkghlerngm44/r-anime-soulmate-finder.svg)](/LICENSE)

/r/anime soulmate finder / affinity gatherer.

Why? I honestly don't know.

Credit to TheEnigmaBlade for their 
[soulmate finder script](https://gist.github.com/TheEnigmaBlade/24205c62280b056fde3d),
which gave me a few ideas and the code for parts of this script.


## What do?

Processes comments from a [chosen comment source](#comment-sources), finds the
comment author's MAL username (if they've specified it in their flair), retrieve
their list, calculate affinity and store the result. Dump results into a .csv
when done, or when you want to stop.


## Setup

**If the below sounds like jargon to you, or you're too lazy to set this up,
  read [this](https://gist.github.com/erkghlerngm44/0f79394803ead5f336e173fef877b44b).
  It should set this all up for you.**

1. Download/fork/clone/whatever this repo.

2. [Create a Reddit client](https://www.reddit.com/prefs/apps) and put your
   `client_id` and `client_secret` under the `reddit` config in `praw.ini`.
   An example file can be found at `praw.ini.example`.

3. Install dependencies (see ["Dependencies"](#dependencies) below).

4. Run script (see ["Usage"](#usage) below).


## Dependencies

* MALAffinity
* PRAW
* Requests
* UnicodeCSV

For the lazy:

    $ pip install -r requirements.txt


## Usage

```shell
$ python3 -m soulmate_finder --help
usage: __main__.py [-h] (-c | -s SUBMISSION_ID | -f [LIMIT]) [-v | -q] [-b]
                   [-z SIZE]
                   mal_username

/r/anime soulmate finder

positional arguments:
  mal_username

optional arguments:
  -h, --help            show this help message and exit

comment sources:
  source of comments, which will be processed

  -c, --stream          use the comment stream as the comment source
  -s SUBMISSION_ID, --submission SUBMISSION_ID
                        use the comments in a submission as the comment
                        source. `SUBMISSION_ID` is the reddit submission id (6
                        letter alphanumeric code between the '/comments/' and
                        the thread title in the comments url, e.g.
                        /r/anime/comments/{{CODE}}/free_talk_fridays...)
  -f [LIMIT], --ftf [LIMIT]
                        use the comments in ftfs as the comment source.
                        `LIMIT` specifies how many ftfs to use, working
                        backwards from the current one (default: 5)

logging/print options:
  controls the level of verbosity for this script

  -v, --verbose         be more talkative (print more about what's going on)
  -q, --quiet           quiet (silent) mode (only display errors)

extra options:
  -b, --search-comment-body
                        search the comment body for a mal url if a user
                        doesn't have a flair
  -z SIZE, --buffer-size SIZE
                        buffer size of file to write to, in bytes. dictates
                        how many bytes to hold in buffer before writing to
                        file (default: 512). assume the average row to be
                        written is around 30-35 bytes
```

**NOTE: The `python3` part may be different for you, depending on your OS and/or Python install.
  The variants (IIRC) are `py`, `python`, `python3` and `py -3`. Try each, only specifying the argument
  `--version` at the end, until your terminal tells you it's using `Python 3.x.x`, then use that in place
  of `python3`.**


## Comment Sources

Every comment from your chosen comment source gets processed, and for each comment, the
author's "flair text" (which contains their MAL Profile/AnimeList URL) is extracted,
and affinity with that MAL user is calculated.

There are currently three comment sources that can be used:

### A Thread/Submission

A `SUBMISSION_ID` is passed when specifying this option, and all comments in that
submission are processed.

Invocation:

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --submission SUBMISSION_ID
```

If you are running this on a "Find your MAL soulmate" thread (or something similar),
where, sometimes, users do not put the URL to their MAL profile in their flair, you
may want to run this with the `--search-comment-body` (`-b`) argument, so the comment
body is searched if there is no MAL URL in their flair.

This can be done as follows:

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --submission SUBMISSION_ID --search-comment-body
```

### The Comment Stream

Comments get processed as they are posted onto the subreddit, in near-real-time.

Invocation:

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --stream
```

**NOTE: As the stream never ends, you'll have to Press CTRL+C when you want to stop processing
  users, otherwise the script will keep going on forever**

If you are using this option, you're probably not in a rush, and so might want to use the
`--verbose` (`-v`) argument, so you can see what the script is doing as it does it. This
isn't enabled by default, as printing is time-taxing.

This can be done as follows:

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --stream --verbose
```

### Past Free Talk Friday (FTF) Threads

Comments from past FTFs are processed.

Invocation:

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --ftf
```

The above will process comments from the 5 most recent FTFs. A `LIMIT` can be passed as well,
so you can specify how many FTFs you want to process (working backwards from the current one).

This can be done as follows (to use the 10 most recent FTFs):

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --ftf 10
```

If you are using this option, you may want to have the script process the comments as fast as
possible, so as to reduce the script runtime. You may want to consider using the ``--quiet``
(`-q`) argument, so only errors get printed out.

This can be done as follows:

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --ftf --quiet
```

Note that a `LIMIT` still can be passed after the `--ftf` if needed.

Also note that the "buffer size" can also be changed.

> A small buffer size means the script writes to file more, which means if the script
  abruptly closes, you won't lose a lot of affinities, but it'll make the script run a
  lot slower. Conversely, a high buffer size means the script will write to file less,
  which is helpful when you want to process a lot of users quickly, but you'll lose a
  lot of progress if the script closes abruptly.

The default is 512 bytes. Assume the average row that will get written per user is around 32 bytes.
With the default, progress will be saved to file every 16 rows or so (512 / 32 == 16).

This can be changed as follows:

```shell
$ python3 -m soulmate_finder YOUR_MAL_USERNAME --ftf --buffer-size 2048  # ~ every 64 rows
```


## FAQ

#### Q: I'm seeing references to `affinity-gatherer` in places here. What's that?
I originally had the idea to name this `soulmate-finder` as it is right now,
but after running this script, 
[my kokoro broke](https://github.com/erkghlerngm44/affinity-gatherer/blob/v1.1.0/README.md#q-why-wasnt-this-called-something-snazzy-like-ranime-soulmate-finder)
and I gave up on the idea.

I then got over it, accepted that I had shit taste and renamed everything to `soulmate-finder`

#### Q: It's broken!
~~Have you tried turning it off and on again?~~

[Send me a message](https://www.reddit.com/message/compose/?to=erkghlerngm44) 
and I'll have a look.

#### Q: Your code/documentation/taste is shit!
![[](#yuishrug)](https://i.imgur.com/gEOKk0P.jpg "Sorry.")
