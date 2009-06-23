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
import SocketServer



class ClientError(Exception):
    """An exception thrown because the client gave bad input to the server."""
    pass


class ChatyRequestHandler(SocketServer.StreamRequestHandler):
    """Handles the user interaction with the server"""

    def handle(self):
        """Handles the client connection."""

        self.nickname = None
        
        done = False
        while not done:
            try:
                done = self._processInput()
            except ClientError, error:
                self._privateMessage(str(error))
            except socket.error:
                done = True


    def finish(self):
        """Removes the client from the server list and terminates the 
connection. Called automatically when handle() returns."""
        self.server.delete_user(self.nickname)
        self.request.shutdown(2)
        self.request.close()

    def _processInput(self):
        """Reads a line from the client input and acts according."""
        done = False
        line = self._readline()
        command, arg = self._parseCommand(line)
        if command:
            done = command(arg)
        else:
            print 'some kind of error'
        return done

    def _parseCommand(self, input):
        """Try to parse a string as a command to the server. If it' an
implemented command returns the corresponding method and its arguments..
"""
        commandMethod, arg = None, None
        if input:
            command_and_arg = input.split(' ', 2)
            command = command_and_arg[0]
            arg = command_and_arg[1:]
            commandMethod = getattr(self, command, None)
            if not commandMethod:
                raise ClientError, 'ERROR command %s unknown\r\n' % command
        return commandMethod, arg

    def _privateMessage(self, message):
        """Send a message to the client."""
        self.wfile.write(message)

    def _readline(self):
        """Reads the client input."""
        return self.rfile.readline()

if __name__=='__main__':
    pass
