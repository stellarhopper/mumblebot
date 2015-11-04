# Table Of Contents #


**NB: mumblebot is still very much in development, and isn't really even alpha code yet.  Use it at your own risk.** (and if you do, submit bug reports, please)

# Introduction #
Mumblebot is an attempt to create a bot that will sit on a Mumble server and respond to messages, much like an IRC bot.  The original motivation to write mumblebot came from a discussion on how to split 

&lt;I&gt;

N

&lt;/I&gt;

 players into 

&lt;I&gt;

M

&lt;/I&gt;

 teams in somewhat of a random fashion, without having to trust someone's coin flipping or dice rolling or whatever.  The problem was solved with the [TeamMaker script](TeamMakerScript.md).

# QuickStart #
Install [protobuf](http://code.google.com/p/protobuf/) if you don't already have it installed.

Either unpack the [latest tarball TODO: link](http://google.com) or [checkout the source](https://code.google.com/p/mumblebot/source/checkout).  In the directory it creates run the following command to connect mumblebot to your server:
```
./mumblebot  --server=<your server> --scriptdir=`pwd`/scripts 
```
You'll have to replace `<your server>` with your server's IP address or hostname, of course.

If all went as planned, you should find a new user on your server named mumblebot.  If something went wrong, have a look at mumblebot's options:
```
./mumblebot -h
```
More details about each option can be found in [Configuration](Configuration.md).

Once you've got it all set up nicely, have a look at [Installation](Installation.md) for more information on how to install mumblebot.

# Windows #
Mumblebot will _probably_ work under Windows.  You'll probably have to specify every dicterory explicitly, and the `scriptwd` and `scriptdir` options may not work quite like the documentation says they should.  Alternatively, you can grab a copy of [OpenBSD](http://www.openbsd.org) and install it in a VM.

# Problems? #
If you have issues with mumblebot, you can (sometimes) find the author hanging out on `#mumble` on `irc.freenode.net` under the nick `MagisterQuis`.  Failing that submit an issue to the [issue tracker](https://code.google.com/p/mumblebot/issues/).