#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) 2009 by "Bruno Jacquet (bruno.jacquet@gmail.com)"
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Bruno Jacquet (bruno.jacquet@gmail.com)"
__date__ = "Mon Jul  6 00:38:40 2009"


import psycopg2 as dbapi


def connect(dbname, host='localhost', user='postgres', password='postgres'):
    """Establishes a connection with the database."""
    try:
        connStr = "host=%s dbname=%s user=%s password=%s" % \
            (host, dbname, user, password)
        conn = dbapi.connect(connStr)
    except StandardError, err:
        print 'Unable to connect:\n', err
        return None

    return Ableton(conn)


class AbletonDB(object):
    """Database class."""
    conn = None
    cursor = None
    userID = None

    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()
        self.conn = None
        self.cursor = None
        self.userID = None
        
    def select(self, table, schema='ableton', columns="*", where=None):
        """Performs a SELECT query"""
        query = """SELECT %s FROM %s."%s" """ % (columns, schema, table)

        if where is not None:
            query += """ WHERE %s""" % where

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except StandardError, err:
            print 'Unable to execute:\n', err
            return None

        return rows

    def delete(self, table, schema='ableton', where=None):
        """Performs a DELETE query"""
        query = """DELETE FROM %s."%s" """ % (schema, table)

        if where is not None:
            query += """ WHERE %s""" % where
        
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except StandardError, err:
            print 'Unable to execute:\n', err
            return None

    def insert(self, table, columns, values, schema='ableton'):
        """Performs an INSERT query"""
        query = """INSERT INTO %s."%s" (%s) VALUES (%s) """ \
            % (schema, table, columns, values)
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except StandardError, err:
            print 'Unable to execute:\n', err

    def exec_function(self, func, schema='ableton', args=None, commit=False):
        """Executes a function"""
        query = """SELECT %s.%s(%s)""" % (schema, func, args)
        try:
            self.cursor.execute(query)
            if commit:
                self.conn.commit()
        except StandardError, err:
            print 'Unable to execute:\n', err
            return None

        return self.cursor.fetchone()

    def sign_in(self, username, password):
        """Signs in a new user."""
        retval = self.exec_function('new_temp_user',
                                    args = "'%s', '%s'" % (username, password),
                                    commit = True)

        if retval[0]:
            print 'New user accepted. Needs email confirmation.'
            return True
        else:
            print 'User not accepted.'
            return False

    def confirm_username(self, username, password):
        """Confirms the new user's email"""
        retval = self.exec_function('new_user', 
                                    args = "'%s'" % username, 
                                    commit = True)
        if retval[0]:
            print 'Email confirmed. User created.'
        else:
            print 'Email not valid.'
            return False

        return self.login(username, password)

    def login(self, username, password):
        """Login the user"""
        row = self.select('Users', 
                          columns='user_id, password',
                          where="""email='%s'""" % username)

        if row == []:
            print "Bad credentials"
            return False

        userID = row[0][0]

        if password == row[0][1]:
            self.delete('WrongLogins', where = """user_id=%s""" % userID)
            self.userID = userID
            return True

        attempts = self.exec_function('wrong_login', args=userID, commit=True)

        if attempts[0] > 0:
            print "%s attempts left" % attempts[0]
            return False

        print 'Account blocked temporarily. Try again later.'
        return False

    def logout(self):
        """Log out the user"""
        self.close()

    def insert_content(self, value, allow_user_type='public'):
        """Inserts new user content"""
        if self.userID is None:
            print 'Need to login to insert content.'
            return False

        user_type_id=self.select('UserTypes',
                                 columns = 'type_id',
                                 where="description='%s'"%allow_user_type)[0][0]

        self.insert('Contents',
                    """"value", owner_id, allow_user_type""",
                    """'%s', %i, %i""" % (value, self.userID, user_type_id))
        return True

    def get_content(self, content_id):
        """Retrieves content"""
        user_id = None
        if self.userID is None:
            user_id = self.select('Users',
                                  columns = 'user_id',
                                  where = "email=''")[0][0]
        else:
            user_id = self.userID

        retval = self.exec_function('get_content',
                                    args="%i, %i" % (content_id, user_id))[0]
        
        return retval[2:-2] # cuts the "( and )"


if __name__ == '__main__':
    pass
