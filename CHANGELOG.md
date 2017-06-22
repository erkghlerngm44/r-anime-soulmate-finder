# Changelog


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
