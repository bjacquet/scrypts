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

from chatyrequesthandler import ChatyRequestHandler
from threading import Thread


class ChatyServer(SocketServer.ThreadingTCPServer, Thread):
    """The server class."""

    def __init__(self, server_address, RequestHandlerClass):
        Thread.__init__(self)
        self.setDaemon(True)
        self.c=SocketServer.ThreadingTCPServer.__init__(self, server_address,
                                                        RequestHandlerClass)
        self._users = dict()
        self._rooms = dict()
        
    def run(self):
        self.serve_forever()

    def delete_user(self, user):
        if user in self._users:
            del(self._users[user])

        for room in self._rooms:
            if user in self._rooms[room]:
                self.part_room(user, room)

    def add_user(self, user, wfile):
        if user in self._users:
            return False
        self._users[user] = wfile
        return True

    def join_room(self, user, room):
        if room in self._rooms:
            self._rooms[room].append(user)
        else:
            self._rooms[room] = [user]

    def part_room(self, user, room):
        if user in self._rooms[room]:
            self._rooms[room].remove(user)
            if len(self._rooms[room]) == 0:
                del(self._rooms[room])

    def msg_room(self, from_user, to_room, msg):
        if to_room not in self._rooms or from_user not in self._rooms[to_room]:
            return False

        message = 'GOTROOMMSG %(username)s %(chatroom)s %(message)s\r\n' % \
            {'username': from_user,
             'chatroom': to_room,
             'message': msg}

        for user in self._rooms[to_room]:
            if user == from_user:
                continue
            wfile = self._users[user]
            wfile.write(message)
        return True

    def msg_user(self, from_user, to_user, msg):
        if to_user not in self._users:
            return False

        message = 'GOTUSERMSG %(username)s %(message)s\r\n' % \
            {'username': from_user,
             'message': msg}

        wfile = self._users[to_user]
        wfile.write(message)
        return True


if __name__=='__main__':
    import sys
    if len(sys.argv) < 3:
        print 'Usage: %s [hostname] [port number]' % sys.argv[0]
        sys.exit(1)
    hostname = sys.argv[1]
    port = int(sys.argv[2])

    server = ChatyServer((hostname, port), ChatyRequestHandler)
    server.start()

    done = False
    while not done:
        command = sys.stdin.readline().strip()
        if command == 'quit':
            done = True
            sys.exit(1)
