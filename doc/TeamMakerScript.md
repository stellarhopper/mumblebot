# Table Of Contents #


# About #
This is the script that got this whole project started.  The problem: How to separate N players M ways reasonably randomly, if there's no way to verify whether the person who says he's rolling dice is actually rolling dice.

When teammaker starts, it (using perl's `rand`) comes up with a string and a seed.  It then tells the channel the string and the md5 digest of the seed concatenated with that string.

# Usage #
`!teammaker help`: Prints a help message

`!teammaker N teams`: Splits players up into N teams

`!teammaker kill-9!`: Terminates the script

Each player should send teammaker a word or phrase.  When everybody who's going to be sorted into teams has sent teammaker a word, someone should send `!teammaker N teams` (replacing N with a number).  Teammaker will then hash everybody's word with the salt, and use that to split the players into teams.  Finally, the salt is sent, for anybody who wants to verify it hasn't changed.