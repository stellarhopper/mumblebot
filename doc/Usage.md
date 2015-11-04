# Table Of Contents #


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