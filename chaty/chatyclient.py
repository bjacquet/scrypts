#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Bruno Jacquet (bruno.jacquet@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import socket

class MirrorClient:
    """A client for the mirror server."""

    def __init__(self, server, port):
        """Connect to the giver server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))

    def mirror(self, string):
        """Sends the given string to the server, and prints the response."""
        if string[-1] != '\n':
            string += '\r\n'
        self.socket.send(string)

        #Read server response
        buf = []
        input = ''
        while not '\n' in input:
            try:
                input = self.socket.recv(1024)
                buf.append(input)
            except socket.error:
                break
        return ''.join(buf)[:-1]

    def close(self):
        self.socket.send('\r\n') #Close the connection
        self.socket.close()


if __name__=='__main__':
    import sys
    if len(sys.argv) <  5:
        print 'Usage: %s [client type] [host] [port] [message]' % sys.argv[0]
        sys.exit(1)
    hostname = sys.argv[2]
    port = int(sys.argv[3])
    message = sys.argv[4]

    if sys.argv[1] == '1':
        m = MirrorClient(hostname, port)
        print m.mirror(message)
        m.close()
