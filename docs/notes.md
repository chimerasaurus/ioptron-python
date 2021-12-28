# Notes

These are notes from writing this wrapper that are useful.

## Time
The docs use the following note on calculating dates/times:

                This command sets the current UTC Time. The number equals (JD(current UTC Time) – J2000) *
                8.64e+7. Note: JD(current UTC time) means Julian Date of current UTC time. The resolution is 1
                milliseconds.

I found this a little confusing based on how it is worded.

As it turns out, the times being used are just J2000 to the millisecond level. 

For example, when I ran a `:GUT#` command, I got the following respondse:

                -48000693900019792#

Taking the 5th to end digit, you get `0693900019792`. Trimming the leading 0, which looks to be padding, when
you convert time time into milliseconds since J2000, you get `2021-12-27    18:00:18.792`.

The date conversions work the same way the other way (UTC in MS -> J2000).
