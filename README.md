# firefox-strings
Ad-hoc python code to create stats for Firefox string stats

The code is executed in steps:

1. last_month.py
2. monthly_update.py
3. aggregate.py

last_month queries the changetracker db from mozext to get the last push in a month, with date and hex revision.

monthy_update inquires the hg repo to see which strings are new, taking into account hg copies,
and counts both strings and words. It stores its data on a per-file bases. It also stores how many strings
and words we had in total.

aggregate aggregates that to a yearly report for words, strings, new and total.
