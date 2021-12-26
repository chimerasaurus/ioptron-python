# ioptron-python

This is a prototype Pythoh library for working with iOptron mounts.

I am writing this to get experience with how the mount works and communicates over Serial. This is a heavy work in progress and is not intended for (real) use yet.
Commands have been implemented in a way ignoring how they may be put together, though I have done some research on that topic 
[here](https://docs.google.com/document/d/1Y0HqoRofPWVJb1jJ7mnwwWQPyfe0tdnYJl2PxAiOCdg/edit#heading=h.bx0imo96b59x).

All of this is being developed only against my CEM70-NUC. I am trying to write this in a way that would make it useful to other iOptron mounts with minor changes.

My goal in writing this is to eventually package it up and use it as a library for an Alpaca endpoint.
