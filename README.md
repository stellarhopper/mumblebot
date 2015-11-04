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
If you have issues with mumblebot, you can (sometimes) find the author hanging out on `#mumble` on `irc.freenode.net` under the nick `MagisterQuis`.  Failing that submit an issue to the [issue tracker](https://code.google.com/p/mumblebot/issues/).  * Unable to join servers with certrequired=True
  * Only one Token (i.e. password) can be sent
  * If the username is in use, mumblebot dies
  * non-ascii characters aren't handled well# Table Of Contents #


# Introduction #

Mumblebot may be configured straight from the command line or with a configuration file.  Any option specified on the command line may be specified in the config and vice versa.  Options specified on the command line take precedence over options specified in the config file.  See [Usage](Usage.md) or run `mumblebot -h` for a concise list of configurable options.

The configuration file may be specified using `--config` on the command line, for example:
```
mumblebot --config /etc/mumblebot.conf
```
See [the config file section of the Installation wiki page](https://code.google.com/p/mumblebot/wiki/Installation#The_config_file) for more details.

A sample config files ships with mumblebot.

# File Format #

The config file consists of lines containing an option and its argument, separated by whitespace.  Blank lines and lines starting with a `#` are ignored.  The options are case sensitive.

Options which don't require an argument on the command line usually require True as the argument in the config file.

# Options #

The following options may be specified in the config file:

## server ##
The server to which to connect.  This may be specified as an IPv4 address, an IPv6 address, or a hostname.
```
server mumble.foo.com
server 192.168.1.24
server 2601:a:4400:9f:149c:baff:fe58:f963
```
There is no default for this option.

## port ##
The port on the server to which to connect
```
port 64738
```
Default: 64738

## srcip ##
If the host running mumblebot has more than one IP address, this specifies the local IP address to use.
```
srcip 192.168.1.15
srcip 2601:a:4400:9f:d861:6251:6745:71b0
```
Default: the system default

## srcport ##
The port from which to connect.
```
srcport 1337
```
Default: a random port chosen by the OS.

## timeout ##
How long, in seconds, to wait for a connection to the server before giving up.
```
timeout 10
```
Default: 10 seconds

## syslog ##
Log to syslog instead of stdout/stderr.  This is handy for running mumblebot in the background.
```
syslog True
```
Default: False, which prints log messages to stdout/stderr.

## debug ##
Outputs messages useful for debugging.  If everything is working, this can print quite a bit of output.  You probably shouldn't use this with `syslog True`.
```
debug True
```
Default: False

## username ##
The username to use on the server.  This is how mumblebot will appear to other users on the server.
```
username AwesomeBot
```
Default: `mumblebot`

## password ##
The password needed to connect to the server.  Allows you to put your bot on passworded servers.  This is stored in plaintext in the config, so make sure the config file isn't world-readable (`chmod go-r`) if you use this option.
```
password supersecretpassword
```
Default: no password

## certfile ##
An SSL certificate to send to the server.  If the private key is stored in the certificate, `keyfile` is not necessary.

A self-signed certificate and key may be generated with openssl `req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mysitename.key -out mysitename.crt`.
```
certfile /etc/mumblebot.d/mumblebot.cert
```
Default: no certificate

## keyfile ##
The private key which corresponds to `certfile`.  If the key is stored in the file given by `certfile`, this is not necessary.

A self-signed certificate and key may be generated with openssl `req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mysitename.key -out mysitename.crt`.
```
keyfile: /etc/mumblebot.d/mumblebot.key
```
Default: no key

## printusers ##
Print a list of users on the server, disconnect, and exit.  Specify a timeout (in seconds) to wait for new user data to become available.  This may be run with `printchannels`.  If `syslog True` is set, the list of users will be sent to syslog.  Users are printed with their session ID and the channel they're in in square brackets before their username.
```
printusers 1
```
Default: Connect normally, don't print a list of users.  This may be specified on the command line without a timeout to use the default timeout of 1 second.  A timeout must be specified in the config file.

## printchannels ##
Print a list of channels on the server, disconnect and exit.  Specify a timeout (in seconds) to wait for new channel data to become available.  This may be run with `printusers`.  If `syslog True` is set, the list of channels will be sent to syslog.  Channels are printed with their channel IDs in square brackets before the channel name.
```
printchannels 1
```
Default: Connect normally, don't print a list of users.  This may be specified on the command line without a timeout to use the default timeout of 1 second.  A timeout must be specified in the config file.

## trigger ##
If a message mumblebot can see starts with this character, mumblebot will send the message along with the sender username, session ID, and channel to the script named the first word in the message.  See [Usage](Usage.md) for more details.
```
trigger !
```
Default: `!`

## scriptwd ##
Scripts are started with the given directory as their working directory.  Every script is started with this working directory, so if scripts need to be started in different directories, it may be necessary to write wrappers.
```
scriptwd /tmp
```
Default: `/`

## scriptdir ##
The directory containing a the scripts executed by mumblebot.  This may either be given as a path relative to the directory specified with `scriptwd` or as an absolute path.
```
scriptdir /etc/mumblebot.d
```
Default: `/etc/mumblebot.d`

## channel ##
The channel on the server mumblebot will attempt to join.  This may be specified as a channel ID (see `printchannels`, above), or a Unix-style path (`/rootchannel/channel/subchannel`).
```
channel /PlanetaryAnnihilation/RedTeam
channel 16
```
Default: `0`, the root channel.# Table Of Contents #


# About #
The purpose of echo is to provide an example of how to read messages from mumblebot in a script.  If a user sends it a message, it'll send the message right back

# Usage #
`!echo message`

`message` will be sent back to the channel# Table Of Contents #



# TL;DR #
There is no one correct way to install mumblebot.  The following guidelines simply put files where mumblebot expects them by default.

```sh

cp mumblebot /usr/local/bin
chmod u+x /usr/local/bin/mumblebot
cp -r ./mumblebot.d /etc
chmod u+x /etc/mumblebot.d/*
mkdir -p $(python -m site --user-site)
cp ./Mumble_pb2.py $(python -m site --user-site)
cp mumblebot.conf /etc```

# Dependencies #

Mumblebot requires Python 2.7 (but may run on older versions) and Google's [protobuf](http://code.google.com/p/protobuf/).  The following (growing) table has installation commands for various operating systems and Linux distributions:

| **OS** | **Command** | **Notes** |
|:-------|:------------|:----------|
| OpenBSD | `pkg_add -iv python protobuf` | Choose Python 2.7 |
| Gentoo | `emerge dev-libs/protobuf` |           |

If your OS/Distro isn't listed here, add a comment or file an issue with the proper command to install Python and protobuf.

# Mumblebot #

Mumblebot can go anywhere you'd like.  `/usr/local/bin` is a good choice.  Depending on your system, you may need to `chmod u+x /usr/local/bin/mumblebot`.

# The scripts #

The scripts should all be kept in the same directory.  By default, mumble will look in `/etc/mumble.d`, but this can be anywhere as long as it is specified in the config file or the command line.  Depending on your system, you may need to `chmod u+x /etc/mumblebot.d/*`.

# The config file #

A config file isn't strictly necessary, but mumblebot will search for a config file named `mumblebot.conf` in the following places, in order:
  * The current working directory
  * The user's home directory
  * `/etc`
  * `/usr/local/etc`
The config file's name can be overridden on the command line, as can the full path to the file.  See [Configuration](Configuration.md) for more details about this file.

# Protobuf #

Included with the source is a file named `Mumble_pb2.py` which mumblebot will need to be able to find.  You can put this in file anywhere Python looks for modules.  See [the Python documentation](http://docs.python.org/2/tutorial/modules.html#the-module-search-path) for details.  If you're not putting mumblebot in `/usr/local/bin`, putting `Mumble_pb2.py` in the same directory as mumblebot should work.  A user's site-specific python module path can be found by running `python -m site --user-site`.

It's possible the version of `Mumble_pb2.py` that ships with mumblebot may not work on your system.  If so recompiling `Mumble.proto` is probably a good idea.  The following command will compile a new `Mumble_pb2.py` from `Mumble.proto`:
```bash

protoc --python_out=. Mumble.proto```
Mumblebot ships with the version of `Mumble.proto` that it expects.  Alternatively, you can grab the latest version from [Mumble's github repo](https://github.com/mumble-voip/mumble/raw/master/src/Mumble.proto).  It _should_ be backwards-compatible.<font color='red' size='5'>NB: This is very alpha software.  Use at your own risk!</font> (and submit bug reports)

# What it Is #
Mumblebot is a small program which sits on a Mumble server and provides an interface between the Mumble server and user-defined scripts, much like an IRC bot.

# What it Does #
On its own, next to nothing.  The power of mumblebot comes with the ability to execute external scripts on user input.  You can write scripts in any language to interact with users on the server.  The whole project started in an attempt to split users into teams transparently and fairly.  You could also use it for automated announcements, a knowledge store, stats, or whatever you'd like.

In addition to that, mumblebot can connect to a server and retrieve a list of channels and/or users.

# Development #
mumblebot is being developed on OpenBSD.  It may run on other systems.  With enough chanting and incense, it may even run on Windows.  Feel free to give it a try.

See the [About](About.md) page for more information.

---
  * [About](About.md)
  * [Installation](Installation.md)
  * [Configuration](Configuration.md)
  * [Usage](Usage.md)
  * Scripts
    * [Echo](EchoScript.md)
    * [TeamMaker](TeamMakerScript.md)
  * [Planned features](TODO.md)
  * [Known limitations](BUGS.md)# Table Of Contents #


# About #
This is the script that got this whole project started.  The problem: How to separate N players M ways reasonably randomly, if there's no way to verify whether the person who says he's rolling dice is actually rolling dice.

When teammaker starts, it (using perl's `rand`) comes up with a string and a seed.  It then tells the channel the string and the md5 digest of the seed concatenated with that string.

# Usage #
`!teammaker help`: Prints a help message

`!teammaker N teams`: Splits players up into N teams

`!teammaker kill-9!`: Terminates the script

Each player should send teammaker a word or phrase.  When everybody who's going to be sorted into teams has sent teammaker a word, someone should send `!teammaker N teams` (replacing N with a number).  Teammaker will then hash everybody's word with the salt, and use that to split the players into teams.  Finally, the salt is sent, for anybody who wants to verify it hasn't changed.This is taken from the #TODO: lines in the code.

  * Generate certificate for auth
  * Make better.  Thanks clientkill
  * config special word for pwd
  * debug message for adding user
  * Handle non-ascii characters
  * multiple tokens
  * Add numbers (or something) to username when username is already in use
  * work on a better way to receive error messages from scripts
  * Implement tokens
  * Timeout on rx of auth message if !mumble server
  * Set list of entities to which to send: sender.add\_id/chan
  * search for zero-length triggered messages
  * send all messages to a specified script
  * error checking
  * Install script
  * standard -h for script, help script: find scriptdir -type x -type f, !help foo -> script -h# Table Of Contents #


# Usage Statement #
<pre>usage: mumblebot [-h] [-c CONFIGFILE] [-s SERVER] [-p PORT] [--srcip SRCIP]<br>
[--srcport SRCPORT] [--timeout TIMEOUT] [--syslog] [-d]<br>
[-u USERNAME] [--password PASSWORD] [--certfile CERTFILE]<br>
[--keyfile KEYFILE] [--printusers [TIMEOUT]]<br>
[--printchannels [TIMEOUT]] [--trigger TRIGGER]<br>
[--scriptwd SCRIPTWD] [--scriptdir SCRIPTDIR]<br>
[--channel CHANNEL]<br>
<br>
Extensible bot for Mumble<br>
<br>
optional arguments:<br>
-h, --help            show this help message and exit<br>
-c CONFIGFILE, --config CONFIGFILE<br>
Specifies the config file. Arguments given on the<br>
command line take precedence over the config file. If<br>
this is not specified, the config file will be looked<br>
for in the following locations: ., /home/stuart, /etc,<br>
/usr/local/etc. Every long option which may specified<br>
on the command line may be specified in the config<br>
file, separated by its value by whitespace.<br>
-s SERVER, --server SERVER<br>
The mumble server to which to connect.<br>
-p PORT, --port PORT  The port to which to connect on the mumble server.<br>
--srcip SRCIP         The IP address from which to connect. The default is<br>
usually fine.<br>
--srcport SRCPORT     The port from which to connect. The default is usually<br>
fine.<br>
--timeout TIMEOUT     The amout of time to wait for a connection to be<br>
established. The default (10s) is usually fine.<br>
--syslog              Log to syslog instead of standard out/error.<br>
-d, --debug           Log messages useful for debugging.<br>
-u USERNAME, --username USERNAME<br>
The username to use on the server.<br>
--password PASSWORD   An optional password to send to the server.<br>
--certfile CERTFILE   An optional ssl certificate to send to the server. If<br>
this includes the key as well, KEYFILE need not be<br>
specified.<br>
--keyfile KEYFILE     An optional ssl key that matches the CERTFILE. If the<br>
key is included in the CERTFILE, this need not be<br>
specified.<br>
--printusers [TIMEOUT]<br>
Print a list of users on the server. An optional time<br>
may be specified to limit how long to wait for new<br>
users to appear. The default (1s) is usually fine.<br>
--printchannels [TIMEOUT]<br>
Print a list of channels on the server. An optional<br>
time may be specified to limit how long to wait for<br>
new channel data to become available. The default (1s)<br>
is usually fine.<br>
--trigger TRIGGER     If a message starts with this character, it'll send<br>
the message to the script named the first word in the<br>
message (or silently ignore it if there's no script).<br>
The default (an exclamation mark) is usually fine.<br>
--scriptwd SCRIPTWD   The working directory for the scripts. The default (/)<br>
is usually fine.<br>
--scriptdir SCRIPTDIR<br>
The directory containing the scripts to run. The<br>
default (/etc/mumblebot.d) is usually fine. This is<br>
relative to SCRIPTWD if not absolute.<br>
--channel CHANNEL     The channel to join. This may either be given as a<br>
Unix-style path (/rootchannel/channel/subchannel) or a<br>
channel ID number (which may be retrieved with<br>
printchannels). The default is the root channel.</pre>


# Scripts #
Mumblebot takes the following actions when it sees a message that starts with its trigger (`!` by default):
  1. Mumblebot splits the message into the name of the script and the message to be sent to the script.  The message is split at the first block of whitespace.
  1. If the script isn't already running, mumblebot starts the script.
  1. Mumblebot sends a message to the script in the following format: `[uN:cN]\t<sender_name>\n<message>\n`. Where uN is a literal `u` followed by the sender's session ID and cN is a literal `c` followed by the sender's channel ID.  The message may be an empty string.  See the [echo script source](https://code.google.com/p/mumblebot/source/browse/trunk/src/mumblebot.d/echo) for an example on how to parse this.
  1. When the script sends output, mumblebot sends it to its channel.

Scripts communicate with mumblebot via their stdin and stdout.  Anything printed to stderr is redirected to stdout (handy for scripts that crash).

From a user's point of view, they send a command, prepended by the trigger character to mumble bot (or mumblebot's channel), plus whatever other information the command (i.e. script) needs.  For example, to echo text back to the channel, a user might send `!echo I am testing mumblebot.`

# --printusers and --printchannels #
If either or both of these are given, instead of executing normally, mumblebot will join the server, get a list of users and/or channels, print them to stdout or send them to syslog, and exit.

Channels will be printed in the following format
```
<I>YYYY-MM-DD HH:MM:SS.nnnnnn: [cN]\t<channel_name>
```
Users are printed in a similar format:
```
<I>YYYY-MM-DD HH:MM:SS.nnnnnn: [uN:cN]\t<user_name>
```
As in the messages sent to scripts, `uN` and `cN` are a literal `u` and `c` followed by a session ID and channel ID, respectively.