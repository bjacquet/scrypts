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
        line = self._readline().strip()
        command, arg = self._parseCommand(line)
        if command:
            done = command(arg)
            self._privateMessage('OK\r\n')
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
            command = command_and_arg[0].lower()
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
        return self.rfile.readline().strip()

    def logout(self, arg=None):
        """Client disconnecting.
Makes handle() to terminate."""
        self.server.delete_user(self.nickname)
        return True

    def login(self, arg=None):
        """Nickname registration."""
        nickname = arg[0]
        if nickname is None:
            raise ClientError, 'ERROR no nickname given\r\n'

        if not self.server.add_user(nickname, self.wfile):
            raise ClientError, 'ERROR nickname already in use\r\n'

        self.nickname = nickname

    def join(self, arg=None):
        """Join chatroom."""
        if arg is None or len(arg[0]) < 2 or arg[0][0] != '#':
            raise ClientError, 'ERROR chatroom name invalid\r\n'

        self.server.join_room(self.nickname, arg[0])

    def part(self, arg=None):
        """Leave chatroom."""
        if arg is None or len(arg[0]) < 2 or arg[0][0] != '#':
            raise ClientError, 'ERROR chatroom name invalid\r\n'

        self.server.part_room(self.nickname, arg[0])

    def msg(self, arg=None):
        """Message from client to client/chatroom."""
        if arg is None or len(arg) < 2:
            raise ClientError, 'ERROR no message to send\r\n'

        user_or_room, msg = arg

        if user_or_room[0] == '#':
            if not self.server.msg_room(self.nickname, user_or_room, msg):
                raise ClientError, 'ERROR user not in chatroom\r\n'
        else:
            if not self.server.msg_user(self.nickname, user_or_room, msg):
                raise ClientError, 'ERROR user not connected\r\n'


if __name__=='__main__':
    pass
