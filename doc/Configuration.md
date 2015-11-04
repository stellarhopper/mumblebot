# Table Of Contents #


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
Default: `0`, the root channel.