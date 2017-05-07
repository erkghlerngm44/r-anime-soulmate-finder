[![forthebadge](http://forthebadge.com/images/badges/fuck-it-ship-it.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/just-plain-nasty.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)


# affinity-gatherer

/r/anime affinity gatherer.

Why? I honestly don't know.

As for why this is in a repo and not a gist, I honestly don't know that as well.


## What do?

Processes comments from a chosen comment source, finds the comment author's
MAL username (if they've specified it in their flair), retrieve their list,
calculate affinity and store the result. Dump results into a .csv when done,
or when you want to stop.


## Setup

1. Download/fork/clone/whatever this repo.
2. [Create a Reddit client](https://www.reddit.com/prefs/apps) and put your
   `client_id`, `client_secret`, as well as a unique `user_agent`
   ([guidelines](https://github.com/reddit/reddit/wiki/API)) under the
   `reddit` config in `praw.ini`.
3. Install dependencies (see ["Dependencies"](#dependencies) below).
4. Run script (see ["Usage"](#usage) below).


## Dependencies

* MALAffinity
* PRAW 4
* Requests

For the lazy:

    $ pip install -r requirements.txt

You might run into issues when installing `MALAffinity`, specifically with
Scipy and Numpy. If this is the case, follow the instructions 
[here](https://github.com/erkghlerngm44/malaffinity#dependencies).


## Usage

### For the normal, sane people:
Running the script from the command line.

    # Using the comment stream as the source of comments
    $ affinity_gatherer.py --stream MAL_USERNAME

    # Or using a submission as the source of comments
    $ affinity_gatherer.py --submission SUBMISSION_ID MAL_USERNAME


### For the crazy, insane people:
Importing the script and manually configuring it.

    >>> import affinity_gatherer as affinity

    # Get your scores loaded
    >>> affinity.pearson.init("MAL_USERNAME")

    # OPTIONAL: Check if everything went okay
    >>> affinity.pearson._base_scores
    {5680: [10], 7791: [10], 9617: [10], ...}


    # Getting the CommentForest class for your chosen source of comments

    # If you're using the comment stream...
    >>> comments = affinity.get_comment_stream()

    # Or if you're using a submission...
    >>> comments = affinity.get_comments_from_submission("SUBMISSION_ID")


    # Feed it into the main function and watch it go!
    >>> affinity.main(comments)

Please don't actually do this. The sane method is nicer.


## Source-specific notes

### Comment Stream
* All comments posted in the subreddit after the script is run are processed.
* When you've had enough and want to stop it, Press `CTRL+C` (`^C`) to
  stop the program. If you don't stop it, it'll keep running forever and ever.
* Probably a bad idea to run this when the sub's less active. You won't get
  that many results if this is the case.

### Comments from a Submission
* This is especially useful if being run in a big thread, like FTF or
  one of the "Find your MAL soulmate" ones.
* Comment IDs are collected through the [Pushshift API](https://pushshift.io/).

  This method allows all comments in a thread to be retrieved faster than PRAW's 
  `reddit.submission(id="SUBMISSION").comments.replace_more(limit=None)`,
  at a rate of 100 comments per second. This script takes longer than that
  to process each comment, so don't expect it to end that quickly.

  **NOTE**: The [Legendary FTF](https://redd.it/5p0gfb) took ~300 seconds
  (5 minutes) to process, so expect similar times for threads with
  the same amount of comments.
* The script will exit when there are no more comments left to process in the
  specified thread. If the script needs to be terminated before that,
  press `CTRL+C` (`^C`)


## More Notes
* CTRL+C terminates the script and saves all the calculations to `affinity.csv`,
  which will be created in the same directory as the main script.
* Method used to calculate affinity has been tested on a 
  [modified version](https://github.com/erkghlerngm44/malaffinity-tests) of this script, 
  and in all cases, the affinity calculated using this method matched the affinity 
  that comes up when I visit any of the users' profile.
  
  To see the code behind this, go to 
  [erkghlerngm44/malaffinity](https://github.com/erkghlerngm44/malaffinity).


## FAQ

#### Q: Why wasn't this called something snazzy like "/r/anime soulmate finder"?
Well, I was planning on doing so, then I had my hopes and dreams crushed when I ran
this script, so I gave up on the idea and went with a duller name.

#### Q: It's broken!
~~Have you tried turning it off and on again?~~

[Send me a message](https://www.reddit.com/message/compose/?to=erkghlerngm44) 
and I'll have a look.

#### Q: Your code/documentation/taste is shit!
![[](#yuishrug)](https://i.imgur.com/gEOKk0P.jpg "Sorry.")
