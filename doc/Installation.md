# Table Of Contents #



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
Mumblebot ships with the version of `Mumble.proto` that it expects.  Alternatively, you can grab the latest version from [Mumble's github repo](https://github.com/mumble-voip/mumble/raw/master/src/Mumble.proto).  It _should_ be backwards-compatible.