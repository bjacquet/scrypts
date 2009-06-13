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

class MirrorServer:
    """Receives text on a line-by-line basis and sends back a reversion of the
    same text."""

    def __init__(self, port):
        """Binds the server to the giben port."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(port)
        self.socket.listen(5)

    def run(self):
        """Handles incoming requests."""
        while True:
            request, client_address = self.socket.accept()
            input = request.makefile('rb', 0)
            output = request.makefile('wb', 0)
            line = True
            try:
                while line:
                    line = input.readline().strip()
                    if line:
                        output.write(line[::-1] + '\r\n')
                    else:
                        #A blank line terminates the connection.
                        request.shutdown(2) #Shut down both reads and writes.
            except socket.error:
                #Client disconnected.
                pass


if __name__=='__main__':
    import sys
    if len(sys.argv) < 3:
        print 'Usage: %s [server type] [hostname] [port number]' % sys.argv[0]
        sys.exit(1)

    if sys.argv[1] == '1':
        hostname = sys.argv[2]
        port = int(sys.argv[3])
        MirrorServer((hostname, port)).run()

