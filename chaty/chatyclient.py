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
from threading import Thread


class ChatyClient:
    """A client for the ChatyServer"""

    def __init__(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._output = self._socket.makefile('wb', 0)

        self.run()

    def run(self):
        toServer = self.InputToServer(self._output)
        toServer.start()

        newText = True
        while newText:
            newText = self._socket.recv(1024)
            if newText:
                print newText
        toServer.done = True


    class InputToServer(Thread):
        """Reads user input and sends it to server."""
        
        def __init__(self, output):
            """Make this thread a daemon thread, so that if the Python
interpreter needs to quit it won't be held up waiting for this thread to die."""
            Thread.__init__(self)
            self.setDaemon(True)
            self._output = output
            self.done = False

        def run(self):
            while not self.done:
                text = sys.stdin.readline().strip()
                if text:
                    self._output.write(text + '\r\n')


if __name__=='__main__':
    import sys

    if len(sys.argv) != 3:
        print 'Usage: %s [host] [port]' % sys.argv[0]
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])

    ChatyClient(hostname, port)
