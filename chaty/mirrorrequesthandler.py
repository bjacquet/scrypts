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


import SocketServer


class MirrorRequestHandler(SocketServer.StreamRequestHandler):
    """Handles one request to mirror a message"""

    def handle(self):
        """Read from StreamRequestHandler's provided rfile member, which 
        contains the input from the client. Mirror the text and write it to 
        the wfile member, which contains the output to be sent to the client."""
        line = True
        while line:
            line = self.rfile.readline().strip()
            if line:
                self.wfile.write(line[::-1] + '\n')

if __name__=='__main__':
    pass
