# ioptron-python

This is a prototype Python library for working with iOptron mounts.

I am writing this to get experience with how the mount works and communicates over Serial. This is a heavy work in progress and is not intended for (real) use yet.
Commands have been implemented in a way ignoring how they may be put together, though I have done some research on that topic 
[here](https://docs.google.com/document/d/1Y0HqoRofPWVJb1jJ7mnwwWQPyfe0tdnYJl2PxAiOCdg/edit#heading=h.bx0imo96b59x).

All of this is being developed only against my CEM70-NUC. I am trying to write this in a way that would make it useful to other iOptron mounts with minor changes.

My goal in writing this is to eventually package it up and use it as a library for an Alpaca endpoint.

## Requirements
Some of this is written in a way that requires Python > 3.7. There are also Python requirements in the `requirements.txt` file.

## Running
You will need to have your `PYTHONPATH` set up to run these right now, since it's not properly modularized.

## Citations and sources

This project has used parts of other OSS projects, or has implemented ideas shown in them, including: 

* [python-lx200](https://github.com/telescopio-montemayor/python-lx200)
* [onstep-python](https://github.com/kbahey/onstep-python)

This project uses the following open specifications:

* [iOptron® Mount RS-232 Command Language](https://www.ioptron.com/v/ASCOM/RS-232_Command_Language2014V310.pdf)
