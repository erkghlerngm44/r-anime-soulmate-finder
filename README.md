[![forthebadge](http://forthebadge.com/images/badges/fuck-it-ship-it.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/just-plain-nasty.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)


# r-anime-soulmate-finder

/r/anime soulmate finder / affinity gatherer.

Why? I honestly don't know.

As for why this is in a repo and not a gist, I honestly don't know that as well.

Credit to TheEnigmaBlade for their 
[soulmate finder script](https://gist.github.com/TheEnigmaBlade/24205c62280b056fde3d),
which gave me a few ideas and the code for parts of this script.


## What do?

Processes comments from a chosen comment source, finds the comment author's
MAL username (if they've specified it in their flair), retrieve their list,
calculate affinity and store the result. Dump results into a .csv when done,
or when you want to stop.


## Setup

**If the below sounds like jargon to you, or you're too lazy to set this up,
  read [this](https://gist.github.com/erkghlerngm44/0f79394803ead5f336e173fef877b44b).
  It should set this all up for you.**

1. Download/fork/clone/whatever this repo.

2. [Create a Reddit client](https://www.reddit.com/prefs/apps) and put your
   `client_id`, `client_secret`, as well as a unique `user_agent`
   ([guidelines](https://github.com/reddit/reddit/wiki/API)) under the
   `reddit` config in `praw.ini`. An example file can be found at
   `praw.ini.example`.

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
    $ soulmate_finder.py MAL_USERNAME --stream

    # Or using a submission as the source of comments
    $ soulmate_finder.py MAL_USERNAME --submission SUBMISSION_ID
    
    # Or using all ftfs this year as the source of comments
    $ soulmate_finder.py MAL_USERNAME --ftf

Optional flags

    # Search the comment body for a MAL link if the user has no flair. See Example 2
    $ soulmate_finder.py MAL_USERNAME --submission SUBMISSION_ID --search-comment-body

    # Be more verbose. Best to use this with --stream
    $ soulmate_finder.py MAL_USERNAME --stream --verbose

### For the crazy, insane people:
Importing the script and manually configuring it.

    >>> import soulmate_finder as soulmate


    # Get your scores loaded
    >>> soulmate.pearson.init("MAL_USERNAME")

    # OPTIONAL: Check if everything went okay
    >>> soulmate.pearson._base_scores
    {5680: [10], 7791: [10], 9617: [10], ...}


    # OPTIONAL: Search the comment body for a MAL link if the user has no flair
    >>> soulmate.search_comment_body = True
    # OPTIONAL: More verbosity
    >>> soulmate.verbose = True


    # Getting the CommentForest class for your chosen source of comments

    # If you're using the comment stream...
    >>> comments = soulmate.get_comment_stream()

    # Or if you're using a submission...
    >>> comments = soulmate.get_comments_from_submission("SUBMISSION_ID")

    # Or if you're using FTFs...
    >>> comments = soulmate.get_comments_from_ftfs()


    # Feed it into the main function and watch it go!
    >>> soulmate.main(comments)

Please don't actually do this. The sane method is nicer.


## Examples

Obviously replace `erkghlerngm44` with your own username. 
Example threads provided if you want to use them.

### Example 1
**You have a big thread, say one of the 
  FTFs ([example](https://redd.it/69bcny)) and you want to see what your affinity 
  with the users on there are**

    $ soulmate_finder.py erkghlerngm44 --submission 69bcny
    
### Example 2
**You have a soulmate finder or a roast me thread ([example](https://redd.it/69ar1d))
  and you want to see what your affinity with the users on there are**

    $ soulmate_finder.py erkghlerngm44 --submission 69ar1d --search-comment-body
    
This is useful in these type of threads because some people don't put their MAL in 
their flair.

This could also be used in FTF if there was a MAL trend going on, but there's no point
in using this anywhere else. You'd just be wasting your time.

### Example 3
**You want to see what your affinity with all of the users who have commented in the FTFs
this year is like**

    $ soulmate_finder.py erkghlerngm44 --ftfs

### Example 4
**You don't have a thread in mind - you just want to see what your affinity with the
  people commenting in general right now is like**

    $ soulmate_finder.py erkghlerngm44 --stream
    
**NOTE:** You might want to consider using the `--verbose` flag here. It looks cooler,
plus you're probably not in a hurry if you're using this.


## Converting the CSV into a Reddit-Friendly table
Type the `code` bits exactly into the terminal, and only press [ENTER] when instructed,
unless you know what you're doing

1. `cp affinities.csv affinities.txt` [ENTER]
2. `vim affinities.txt` [ENTER]
3. `:%s/,/|/g` [ENTER]
4. `:%s/_/\\_/g` [ENTER]
5. `gg`
6. `o`
7. `:--|:--|:-:|:-:`
8. Press the [ESC] key
9. `:wq` [ENTER]

Check `affinities.txt` for your Reddit-Friendly table!


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
  
### Comments from all FTFs this year
* Basically the same as "comments from a submission", but collects all comments
  from previous FTFs this year and sends that off to be processed.

* Will make ~20 calls to the Pushshift and Reddit API when started up, with a 
  2 second timeout between requests.
  
* Obviously, it will process every comment in those FTFs, so expect it to take
  considerably longer than any other method.


## More Notes
* CTRL+C terminates the script and saves all the calculations to `affinity.csv`,
  which will be created in the same directory as the main script.

* When using `--search-comment-body`, the comment body will only be searched if
  the comment author doesn't have a MAL flair.
  
  This obviously has its flaws, but I really don't want to rewrite that section. Sorry.

* Method used to calculate affinity has been tested on a 
  [modified version](https://github.com/erkghlerngm44/malaffinity-tests) of this script, 
  and in all cases, the affinity calculated using this method matched the affinity 
  that comes up when I visit any of the users' profile.
  
  To see the code behind this, go to 
  [erkghlerngm44/malaffinity](https://github.com/erkghlerngm44/malaffinity).


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
