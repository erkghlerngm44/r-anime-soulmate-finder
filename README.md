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
* PRAW
* Requests

For the lazy:

    $ pip install -r requirements.txt


## Usage

    # Using the comment stream as the source of comments
    $ python3 -m soulmate_finder MAL_USERNAME --stream

    # Or using a submission as the source of comments
    $ python3 -m soulmate_finder MAL_USERNAME --submission SUBMISSION_ID
    
    # Or using all ftfs this year as the source of comments
    $ python3 -m soulmate_finder MAL_USERNAME --ftf

Optional flags

    # Search the comment body for a MAL link if the user has no flair. See Example 2
    $ python3 -m soulmate_finder MAL_USERNAME --submission SUBMISSION_ID --search-comment-body

    # Be more verbose. Best to use this with --stream
    $ python3 -m soulmate_finder MAL_USERNAME --stream --verbose


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
