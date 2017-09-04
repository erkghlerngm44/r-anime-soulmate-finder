# Changelog


## v4.0.0 (2017-09-04)
* Make the `__version__` available in `__main__`
* Add the `--quiet` flag, that'll hide all warnings and below
* Don't use all FTFs this year by default, allow the number be specified, and
  default to 5 if no preference
* Add the `SUBMISSION_ID` metavar for `--submission`
* Extract more constants and add those to `const.py`
* Change PushShift's `/reddit/get/comment_ids` endpoint to the working one
* Use specific dependency versions in `requirements.txt`
* Better file handling
  * Write to file every 8-10 rows, instead of every row, which should speed up the script,
    and make it more efficient
  * Reduce the number of read/write open/close operations done on `affinities.csv`
  * Remove `file` global, as it's no longer needed
* Add `unicodecsv` as a dependency to handle bytes <=> str conversions in csv operations
* Re-add the "total affinities calculated" message that was removed in v3.0.0
* **???**


## v3.0.0 (2017-08-03)
* Write the affinity values straight to the file, and sort it once all the values
  have been retrieved, to make the script less memory intensive
* Split `soulmate_finder.py` into separate files, under the `soulmate_finder`
  directory
* Have the version somewhere in the script
* Use Pushshift's API to get the FTF submissions, instead of manually searching for
  them ourselves
* Show why affinity can't be calculated if `MALAffinityException` is raised, and
  `verbose` is `True`
* Use the `logging` module instead of `print` statements
* Get rid of `vprint` and use `logging.debug` instead
* Show the FTF id on the "retrieving comment ids" message
* Add a debug message to show how many comments will be processed, if using `--ftf`
* Cleanup the readme
* Add `affinities.csv`, and `env/`, `venv/` to the gitignore
* Make all .py files PEP8 compliant, and set up Travis to check if this is the case


## v2.3.1 (2017-07-07)
* PRAW 5 support
  * Isn't breaking this script as far as I can see, so should probably be fine


## v2.3.0 (2017-06-22)
* `malaffinity` v2 support
* Better exception handling
* Always show the `MALRateLimitExceeded` message if it comes up
  * This was previously not shown by default unless the `--verbose` flag 
    was used


## v2.2.0 (2017-05-23)
* Add option to use all FTFs this year as the comment source


## v2.1.0 (2017-05-09)
* Only display the "Processing User" message for users not already processed
  * Displaying it for already processed users was pointless and too time taxing
* Make the unnecessary stdout calls optional and disabled by default
  * This can be activated using the `--verbose` flag


## v2.0.0 (2017-05-07)
* Rename project from `affinity-gatherer` to `r-anime-soulmate-finder`
* Rename `affinity_gatherer.py` to `soulmate_finder.py` and update all docs
* Use `--` for long positional args (that were at `-` already)
* Create short `-` positional args
* Add ability to search the comment body for a MAL URL via a `kwarg` 
  argument and positional argument
* Rename `praw.ini` to `praw.ini.example` and add `praw.ini` to `.gitignore`
* Also, create a `.gitignore`
* Display message if user already processed


## v1.1.0 (2017-04-09)
* Use [`MALAffinity`](https://github.com/erkghlerngm44/malaffinity)
  for affinity calculations


## v1.0.0 (2017-03-18)
* Init
