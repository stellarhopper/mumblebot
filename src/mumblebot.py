#mumblebot.py
#by MagisterQuis

# Imported modules
import argparse
import Mumble_pb2
import os
import platform
#import queue #2TO3 Change this
import Queue
import re
import socket
import ssl
import struct
import subprocess
import sys
import threading
import time

#Global config dict, defaults go here
config = {
    "port":             64738,
    "srcip":            "",
    "srcport":          0,
    "timeout":          10,
    "config":           "mumblebot.conf",
    "debug":            False,
    "syslog":           False,
    "username":         "mumblebot",
    "password":         "",
    "printusers":       False,
    "printchannels":    False,
    "trigger":          "!",
    "scriptdir":        "/etc/mumblebot.d",
    "scriptwd":         "/",
    "channel":          "/",
}

#Protocol message type to class mappings.  This could be done better
msgtype = (Mumble_pb2.Version,
           Mumble_pb2.UDPTunnel,
           Mumble_pb2.Authenticate,
           Mumble_pb2.Ping,
           Mumble_pb2.Reject,
           Mumble_pb2.ServerSync,
           Mumble_pb2.ChannelRemove,
           Mumble_pb2.ChannelState,
           Mumble_pb2.UserRemove,
           Mumble_pb2.UserState,
           Mumble_pb2.BanList,
           Mumble_pb2.TextMessage,
           Mumble_pb2.PermissionDenied,
           Mumble_pb2.ACL,
           Mumble_pb2.QueryUsers,
           Mumble_pb2.CryptSetup,
           Mumble_pb2.ContextActionModify,
           Mumble_pb2.ContextAction,
           Mumble_pb2.UserList,
           Mumble_pb2.VoiceTarget,
           Mumble_pb2.PermissionQuery,
           Mumble_pb2.CodecVersion,
           Mumble_pb2.UserStats,
           Mumble_pb2.RequestBlob,
           Mumble_pb2.ServerConfig,
           Mumble_pb2.SuggestConfig
)
#The other way around.  Again, could be done better
msgnum = {}
for i in range(len(msgtype)): msgnum[msgtype[i].__name__] = i

#Version of mumble to send to the server: (major, minor, revision).
#This gets packed in a goofy manner
version = (1,2,0)

#Logging functions
have_syslog = True
logmsg = lambda x: x
errmsg = logmsg
debugmsg = logmsg
try:
    #Try to use syslog
    import syslog
except ImportError as e:
    #If we don't have syslog, use stdin/out/err until we have a logfile
    have_syslog = False
#Logging lock
loglock = threading.Lock()

#Config file locations
config_locations = (
    ".",
    os.environ["HOME"],
    "/etc",
    "/usr/local/etc",
)
    
#Start here
def main():
    #Set the log functions
    update_logging()
    #Parse command-line arguments
    changed = parse_arguments()
    #Parse config file
    parse_config(changed)
    #Enqueued messages will be sent back to the server
    txqueue = Queue.Queue()
    #txqueue = queue.Queue() #2TO3
    #Connect to server
    try:
        socket = connect_to_server()
    except ssl.SSLError as e:
        print "Unable to connect.  Are you banned?: " + str(e)
        return -1
    #TODO: debug message for adding user
    #TODO: Handle non-ascii characters
    #Make thread for sending, give it a pipe
    sender = Sender(socket)
    sender.start()
    #Make thread for listening, spawn subprocesses for each module
    receiver = Receiver(socket, sender)
    receiver.start()
    #Busy loop to wait for keyboard to terminate us
    try:
        import time
        while sender.is_alive() and receiver.is_alive():
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    sender.stop()
    sender.join()
    socket.close()






#Parse the arguments on the command line
def parse_arguments():
    global config
    #Argparser
    parser = argparse.ArgumentParser(description="Extensible bot for Mumble")
    #Command-line options
    parser.add_argument("-c", "--config", metavar="CONFIGFILE", help="Specifies the config file.  Arguments given on the command line take precedence over the config file.  If this is not specified, the config file will be looked for in the following locations: %s"%", ".join([str(p) for p in config_locations]))
    parser.add_argument("-s", "--server", help="The mumble server to which to connect.")
    parser.add_argument("-p", "--port", type=int, help="The port to which to connect on the mumble server.")
    parser.add_argument("--srcip", help="The IP address from which to connect.  The default is usually fine.")
    parser.add_argument("--srcport", help="The port from which to connect.  The default is usually fine.")
    parser.add_argument("--timeout", help="The amout of time to wait for a connection to be established.  The default (10s) is usually fine.")
    parser.add_argument("--syslog", action="store_true", help="Log to syslog instead of standard in/out/error.")
    parser.add_argument("-d", "--debug", action="store_true", help="Log messages useful for debugging.")
    parser.add_argument("-u", "--username", help="The username to use on the server.")
    parser.add_argument("--password", help="An optional password to send to the server.")
    parser.add_argument("--printusers", metavar="TIMEOUT", nargs='?', const=1, type=float, help="Print a list of users on the server.  An optional time may be specified to limit how long to wait for new users to appear.  The default (1s) is usually fine.")
    parser.add_argument("--printchannels", metavar="TIMEOUT", nargs='?', const=1, type=float, help="Print a list of channels on the server.  An optional time may be specified to limit how long to wait for new channel data to become available.  The default (1s) is usually fine.")
    parser.add_argument("--trigger", help="If a message starts with this character, it'll send the message to the script named the first word in the message (or silently ignore it if there's no script).  The default (an exclamation mark) is usually fine.")
    parser.add_argument("--scriptdir", help="The directory containing the scripts to run.  The default (/etc/mumblebot.d) is usually fine.")
    parser.add_argument("--scriptwd", help="The working directory of each script.  The default (/) is usually fine.")
    parser.add_argument("--channel", help="The channel to join.  This may either be given as a Unix-style path (/rootchannel/channel/subchannel) or a channel ID number (which may be retrieved with printchannels).  The default is the root channel.")
    #Get the options from the command line
    options = vars(parser.parse_args())
    #Save the options
    changed = [] #List of changed options
    for o in options:
        if options[o] is not None: 
            config[o] = options[o]
            changed.append(o)
    #Update logging functions
    update_logging()
    return changed

#Try to find the config file.  If it exists, open it and parse it
def parse_config(changed):
    global config
    #Open the config file
    f = open_config()
    #If it's not found, log and exit
    if f is None:
        debugmsg("Unable to open config file ({}).".format(config["config"]))
        return None
    #Read each line of the file
    for line in f:
        #Remove whitespace
        line = line.strip()
        #Ignore comments
        if line[0] == '#': continue
        #Split the line into keys and values
        key, value = line.split(None, 1)
        #Ignore it if set by the command line
        if key in changed: continue
        #Add it to the config if it's not set already
        config[key] = value
    #Update logging functions
    update_logging()
    #Log it
    logmsg("Read config from {}".format(f.name))
    #Print out options, if debugging
    for o in config:
        debugmsg("Option {}: {}".format(o, config[o]))
    

def open_config():
    f = None
    #If the config files starts with a /, assume it's an absolute path
    if config["config"][0] == "/":
        try:
            f = open(config["config"], "r")
            return f
        except IOError as e:
            f = None
    #Cycle through the default locations
    for l in config_locations:
        try:
            f = open(os.path.join(l, config["config"]))
            return f
        except IOError as e:
            #TODO: Debug to stderr flag
            f = None
        try:
            f = open(os.path.join(l, "."+config["config"]))
            return f
        except:
            f = None
    #If we're here, we couldn't find a file to open
    return f


#Makes a socket to the server and handshakes
def connect_to_server():
    #Make sure we have a server and port
    if "server" not in config:
        errmsg("No hostname or IP address given.  Unable to proceed.")
        sys.exit(1)
    #Connect to the server
    try:
        s = socket.create_connection((config["server"], config["port"]),
                                     config["timeout"], (config["srcip"], 
                                                         config["srcport"]))
    except socket.error as msg:
        errmsg("Unable to connect to {}:{} - {}.".format(config["server"], 
                                                         config["port"], msg))
        exit(1)
    sslsocket = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1,
                                ciphers="AES256-SHA")
#TODO: add support for keyfile
    logmsg("Connected to {}:{}".format(config["server"], config["port"]))
    #Set the socket back to blocking
    sslsocket.setblocking(1)
    return sslsocket

#Thread to send messages to server
class Sender(threading.Thread):
    socket = None
    txqueue = None
    _running = False
    sendlock = None
    pingdata = None
    pingthread = None
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.txqueue = Queue.Queue()
        self.sendlock = threading.Lock()
        self.pingdata = Mumble_pb2.Ping()
        self.pingdata.resync = 0
    #Wait for messages, send them to the server, expects messages to be
    #ready to put on the wire
    def run(self):
        debugmsg("Sender starting")
        #Send back our version info
        clientversion = Mumble_pb2.Version()
        clientversion.version = struct.unpack(">I", struct.pack(">HBB", *version))[0]

        #TODO: Unpack received version
        clientversion.release = ""#mumblebot-0.0.1"
        clientversion.os = ""#platform.system()
        clientversion.os_version = ""#platform.release()
        self.send(clientversion)
        debugmsg("Sent version info")
        #Send auth info
        authinfo = Mumble_pb2.Authenticate()
        authinfo.username = config["username"]
        if config["password"]: 
            authinfo.password = config["password"]
        else:
            authinfo.password = "penis"
        self.send(authinfo)
        debugmsg("Authenticated as %s with password %s"%(authinfo.username, 
                                                         authinfo.password))
        #TODO: Implement tokens
        #TODO: Timeout on rx of auth message if !mumble server
        #Start the pinger
        self.pingthread = threading.Thread(target=self.send_pings)
        self.pingthread.daemon = True
        self.pingthread.start()
        #Flag to keep running.
        self._running = True
        while self._running:
            #Make sure we're still in business
            msg = self.txqueue.get()
            #Die if we're meant to
            if msg is None and not self._running:
                return
            #Number of bytes sent
            count = 0
            #Keep sending 'till we're done
            res = msg
            while len(res) > 0:
                #Lop of the bits we don't need to send
                count = self.socket.send(res)
                res = res[count:]
    #Special case to send a chat message
    def send_chat_message(self):
        #TODO: Finish this
        return
    #Send keepalive pings
    def send_pings(self):
        debugmsg("Pinger starting")
        while True:
            self.send(self.pingdata)
            time.sleep(5)
    #Send a message to the series of tubes
    def send(self, msg):
        #Type code
        type = msgnum[msg.__class__.__name__]
        #Format as a series of bytes
        msg = msg.SerializeToString()
        #Size of messages
        size = len(msg)
        #Pack the header
        hdr = struct.pack(">HL", type, size)
        #Send it out
        #TODO: Get a list of usernames/channels  Store as a dict? keys look like paths
        self.sendlock.acquire()
        self.txqueue.put(hdr+msg)
        self.sendlock.release()
    #Stop thread
    def stop(self):
        debugmsg("Stopping Sender")
        self._running = False
        self.txqueue.put(None)

#TODO: Set list of entities to which to send: sender.add_id/chan

#Thread that handles receiving messages
class Receiver(threading.Thread):
    socket = None
    sender = None
    _running = False
    rxbytes = None #DEBUG
    #Keep ahold of the channels and users on the server
    channels = {}
    orphans = {} #Orphaned channels, same format as above
    users = {} 
    channellock = None
    current_channel = None
    #Variables relevant to printing channels/users
    channelwait = None
    userwait = None
    channeltimer = None
    usertimer = None
    userevent = None
    #Text messages
    msgsplitter = None
    pipes = {}
    #Threads for scripts
    def __init__(self, socket, sender):
        threading.Thread.__init__(self)
        self.sender = sender
        self.socket = socket
        self.daemon = True
        self.channellock = threading.Lock()
        #TODO: add timestamps to debug messages printed to console
        #TODO: Add a timeout for channel message, print the list on timeout
        if config["printchannels"]:
            self.channelwait = float(config["printchannels"])
        if config["printusers"]:
            self.userwait = float(config["printusers"])
            self.userevent = threading.Event()
            self.userevent.clear()
        #Regex to split text message
        self.messagesplitter = re.compile(r"%s(\S+)\s+(\S.*)"
                                          %config["trigger"])
    #Wait for messages, act on them as appropriate
    def run(self):
        debugmsg("Receiver starting")
        #Flag to keep running
        _running = True
        #Start 
        while _running:
            #Get the six header bytes
            header = self.recvsize(6)
            #Unpack the header
            (type, size) = struct.unpack(">HL", header)
            data = self.recvsize(size)
            #TODO: make sure we get the whole message
            typename = msgtype[type].__name__
            debugmsg("Got {}-byte {} message".format(size, typename))
            #Handle each message, this is going to get inefficient.
            try:
                {"Version":         self.onVersion,
                 "ChannelState":    self.onChannelState,
                 "UserState":       self.onUserState,
                 "TextMessage":     self.onTextMessage,
                }[typename](data)
            except KeyError as ke:
                debugmsg("{} message unhandled".format(typename))

    def onVersion(self, data):
        serverversion = Mumble_pb2.Version()
        #CamelCase, ReaLly?
        serverversion.ParseFromString(data)
        (major, minor, revision) = struct.unpack('>HBB', 
            struct.pack('>I', serverversion.version))
        logmsg("Server {}.{}.{} {} ({}: {})".format(major, minor, revision,
                                                    serverversion.release,
                                                    serverversion.os,
                                                    serverversion.os_version))
        #TODO: Timestamp and mark logmessages

    def onChannelState(self, data):
        #If we're still collecting channels, reset the timeout
        if self.channelwait is not None and self.channeltimer is not None:
            self.channeltimer.cancel()
            self.channeltimer = None
        #If we're just printing channels, start the timer
        if self.channelwait is not None and self.channeltimer is None:
            self.channeltimer = threading.Timer(self.channelwait,
                                                self.printchannels)
            self.channeltimer.start()

        #Unroll the data
        channelstate = Mumble_pb2.ChannelState()
        channelstate.ParseFromString(data)
        #Lock the channel tree
        self.channellock.acquire()
        #Root channel
        if channelstate.channel_id == 0:
            #If it's the first time we've seen it
            if 0 not in self.channels:
                self.channels[0] = Channel()
                self.channels[0].name = channelstate.name
            #If not, update the name
            else:
                self.channels[0].name = channelstate.name
        #Regular channels, new channel
        elif channelstate.channel_id not in self.channels:
            t = Channel()
            t.name = channelstate.name
            t.parent = channelstate.parent
            #Check for a list of orphans for which this is the parent
            if channelstate.channel_id in self.orphans:
                for c in self.orphans[channelstate.channel_id]:
                    if c not in t.children:
                        t.children.add(c)
            #If the parent is there, add it to the parent's children
            if channelstate.parent in self.channels:
                self.channels[channelstate.parent].children. \
                        add(channelstate.channel_id)
            #If not, add it to the list of orphans for that child
            else:
                if t.channel_id not in self.orphans:
                    self.orphans[t.parent] = []
                self.orphans[t.parent].add(self.channel_id)
            #Add the channel to the list
            self.channels[channelstate.channel_id] = t
            debugmsg("Added new channel %s [%i:%i]"%(t.name, t.parent,
                                                     channelstate.channel_id))
        #If we have the channel, update it
        else:
            #Update the name
            if channelstate.name and \
               (self.channels[channelstate.channel_id] != channelstate.name):
                oldname = self.channels[channelstate.channel_id].name
                self.channels[channelstate.channel_id].name = channelstate.name
                debugmsg("Changed channel %i's name from %s to %s"%(
                    channelstate.channel_id, oldname, channelstate.name))
            #Update the parent
            if self.channels[channelstate.channel_id].parent != \
               channelstate.parent:
                #Remove the channel from the old parent's list of children
                oldpid = self.channels[channelstate.channel_id].parent
                self.channels[oldpid].children. \
                    remove(channelstate.channel_id)
                #Add it to the new parent's list of children, if we can
                if channelstate.parent in self.channels:
                    self.channels[channelstate.parent].children. \
                        add(channelstate.channel_id)
                #Failing that, it's an orphan
                else:
                    #TODO: Add comment
                    self.orphans.add(channelstate.channel_id)
                debugmsg("Changed channel %i's (%s) parent from %i to %i" 
                         %(channelstate.channel_id, 
                           self.channels[channelstate.channel_id].name,
                           oldpid, channelstate.parent))
        #Join the right channel when we learn about it
        to_join = None
        #If we're meant to be in root, join it
        if config["channel"] == "/" and 0 in self.channels:
            to_join = 0
        #If we're given a channel number, join it when we get it
        elif config["channel"].isdigit() and \
                int(config["channel"]) in self.channels:
            to_join = int(config["channel"])
        #If we're given a path, join it
        elif config["channel"][0] == "/" and len(config["channel"]) > 1 and \
                0 in self.channels:
            #Get a list of channel bits.
            #Sucks if there's a / in the channel name
            channel_path = filter(None, config["channel"].split("/")[1:])
            #If the first part is the name of the root channel, remove it
            if channel_path[0] == self.channels[0].name:
                channel_path = channel_path[1:]
            #We're at where in the tree.  If there's no more path to descend,
            #return the name of the channel we're in.  Else, descend deeper.
            #Failing that, return None
            def _traverse_tree(self, channel_path, where):
                #We've found the last element
                if len(channel_path) == 0:
                    return where
                #If not, see if the next element is a known child
                else:
                    for p in self.channels[where].children:
                        #When we've found the child, recurse
                        if self.channels[p].name == channel_path[0]:
                            return _traverse_tree(self, channel_path[1:], p)
            #Find the id of the channel to join
            to_join = _traverse_tree(self, channel_path, 0)
        #If we're not already there, join the channel
        if to_join is not None and to_join != self.current_channel:
            userstate = Mumble_pb2.UserState()
            userstate.channel_id = to_join
            self.sender.send(userstate)
            self.current_channel = to_join
            logmsg("Joining [c%i] %s"%(to_join, self.channels[to_join].name))
        self.channellock.release()

    def onUserState(self, data):
        #If we're still collecting users, reset the timeout
        if self.userwait is not None and self.usertimer is not None:
            self.usertimer.cancel()
            self.usertimer = None
        #If we're just printing users, start the timer
        if self.userwait is not None and self.usertimer is None:
            self.usertimer = threading.Timer(self.userwait, self.printusers)
            self.usertimer.start()
        #Unroll the data
        userstate = Mumble_pb2.UserState()
        userstate.ParseFromString(data)
        #Make sure the user is in the list
        self.users[userstate.session] = (userstate.channel_id, userstate.name,
                                        userstate.session)

    #Handle messages
    def onTextMessage(self, data):
        textmessage = Mumble_pb2.TextMessage()
        textmessage.ParseFromString(data)
        debugmsg("Message: %s from [%i] %s"%(textmessage.message,
                                             textmessage.actor,
                                             self.users[textmessage.actor][1]))
        #If the message doesn't start with the trigger, we don't care about it.
        if not data.startswith(config["trigger"]):
            return
        #Extract the important bits
        m = self.msgsplitter.match(data)
        #Give up if someone goofed
        if not m: return
        #Script to invoke
        script = m.group(1)
        #Sanatize script name
        script = re.sub(r"[^A-Za-z0-9._]", '', script)
        #Text of the message
        text = m.group(2)
        #TODO: Implement joining a channel
        sender = self.users[textmessage.actor]
        #If the script has died, restart it
        if self.pipes[script].is_dead():
            debugmsg("%s found dead"%script)
            del d[script]
        #Start the script if need be
        if script not in self.pipes:
            try:
                self.pipes[script] = Script(self.sender, script)
            #This happens if the script doesn't exist or isn't executable
            except OSError as e:
                debugmsg("Unable to start %s: %s"%(script, str(e)))
        #Send the message to the script
        self.pipes[script].message(self.users[textmesage.actor], text)

    #Receive a specified number of bytes
    def recvsize(self, size):
        buf = ""
        while len(buf) < size:
            tmp = ""
            tmp = self.socket.recv(size - len(buf))
            buf += tmp
        return buf

    #Print channel list
    def printchannels(self):
        #Get a lock on the channel list
        self.channellock.acquire()
        #Depth-first traversal
        self._printchannel(0, "")
        #Release the list
        self.channellock.release()
        #If the users are to be printed, wait for them
        if config["printusers"]:
            self.userevent.wait()
        #Users have been printed.  Die.
        self.stop()
    #Print a channel's children, recursively, depth-first.  Pass in a channel
    #number and the name of the previous channel path
    def _printchannel(self, channel, parentname):
        name = parentname + "/" + self.channels[channel].name
        logmsg("[c%s]\t%s"%(channel, name))
        for c in self.channels[channel].children:
            self._printchannel(c, name)

    #Print a list of the known users
    def printusers(self):
        #Print the userlist
        for u in self.users:
            logmsg("[u%i:c%i] %s"%(u, self.users[u][0], self.users[u][1]))
        #If channels are to be printed, signal that to end the program
        if config["printchannels"]:
            self.userevent.set()
        #If not, die
        else:
            self.stop()


    #Stop this thread and all subthreads
    def stop(self):
        self.sender.stop()
        #TODO: finish this

#Channel tree
class Channel:
    parent = None
    children = None
    name = ""
    def __init__(self):
        self.children = set()

#A thread representing a connection to a script
class Script(threading.Thread):
    process = None
    sender = None
    scriptname = ""
    def __init__(self, sender, script):
        #TODO: kill these threads before shutting down
        threading.Thread.__init__(self)
        self.scriptame = os.path.join(config["scriptdir"], script)
        self.process = subprocess.Popen(scriptname, stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        cwd=config["scriptwd"])
        logmsg("Started %s"%scriptname)
    #A loop to read output from the process and send it to the tubes
    def run(self):
        while self.proces.poll() is None:
            self.sender.send_chat_message(self.process.readline())
            #TODO: error checking
    #Send a message to the process.  User is the user tuple for the user
    #That sent the message the bot picked up on
    def message(self, user, message):
        self.process.stdin.write("[u%i:c%i] %s\n%s"%(user[2], user[0], user[1],
                                                     message))
    #Kill the script, if it doesn't listen to sigterm, oh well
    def kill(self):
        self.process.terminate()
        self.sender.send_chat_message(self.process.communicate())
        debugmsg("Killed %s"%scriptname)
    #True if the process is dead
    def is_dead(self):
        if self.process.poll() is None:
            return False
        else:
            return True




#Logging functions
def update_logging():
    global errmsg
    global logmsg
    global debugmsg

    #If we're logging to syslog
    if have_syslog and config["syslog"]:
        errmsg = _err_to_syslog
        logmsg = _log_to_syslog
        if config["debug"]:
            debugmsg = _debug_to_syslog
        else:
            debugmsg = _noop
            #If we don't have syslog, use stdin/out/err
    else:
        errmsg = _err_to_stderr
        logmsg = _log_to_stdout
        if config["debug"]:
            debugmsg = _debug_to_stdout
        else:
            debugmsg = _noop

def _err_to_stderr(msg):
    #2TO3 Change this when protoc works on python 3
    with loglock:
        print >>sys.stderr, msg.encode('utf-8')
def _log_to_stdout(msg):
    with loglock:
        print(msg.encode('utf-8'))
def _debug_to_stdout(msg):
    with loglock:
        print(msg.encode('utf-8'))
def _err_to_syslog(msg):
    syslog.syslog(syslog.LOG_ERR, msg)
def _log_to_syslog(msg):
    syslog.syslog(syslog.LOG_INFO, msg)
def _debug_to_syslog(msg):
    syslog.syslog(syslog.LOG_DEBUG, msg)
def _noop(msg):
    return




if __name__ == "__main__":
    main()
