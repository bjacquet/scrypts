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
from mirrorrequesthandler import MirrorRequestHandler
from threading import Thread


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
        if self._users.get(user):
            del(self._users[user])

        for room in self._rooms:
            if self._rooms[room].__contains__(user):
                self.part_room(user, room)

    def add_user(self, user, wfile):
        if self._users.get(user):
            return False
        self._users[user] = wfile
        return True

    def join_room(self, user, room):
        if self._rooms.get(room):
            self._rooms[room].append(user)
        else:
            self._rooms[room] = [user]

    def part_room(self, user, room):
        if self._rooms[room].__contains__(user):
            self._rooms[room].remove(user)

    def msg_room(self, from_user, to_room, msg):
        if not self._rooms.get(to_room) or \
                not self._rooms[to_room].__contains__(from_user):
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
        if not self._users.get(to_user):
            return False

        message = 'GOTUSERMSG %(username)s %(message)s\r\n' % \
            {'username': from_user,
             'message': msg}

        wfile = self._users[to_user]
        wfile.write(message)
        return True


if __name__=='__main__':
    import sys
    if len(sys.argv) < 4:
        print 'Usage: %s [server type] [hostname] [port number]' % sys.argv[0]
        sys.exit(1)
    hostname = sys.argv[2]
    port = int(sys.argv[3])

    if sys.argv[1] == '1':
        MirrorServer((hostname, port)).run()
    elif sys.argv[1] == '2':
        SocketServer.TCPServer((hostname, port), RequestHandler).serve_forever()
    elif sys.argv[1] == '3':
        server=SocketServer.ThreadingTCPServer((hostname, port),
                                               MirrorRequestHandler)
        server.serve_forever()
    elif sys.argv[1] == '4':
        server = ChatyServer((hostname, port), ChatyRequestHandler)
        server.start()

        done = False
        while not done:
            command = sys.stdin.readline().strip()
            if command == 'quit':
                done = True
                sys.exit(1)
