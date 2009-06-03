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
__date__ = "Wed Jun 03 16:04:56 2009"

import re
import sys
import ConfigParser

class Ods2Dw(object):
    """
    Ods2Dw([files[, rules]]) -> Ods2Dw object

    Creates SQL files to create tables, stored procedures, views and triggers.
    files, if given, is a list of SQL file names each with a single CREATE 
    Query.
    rules, if given, is a list of tuples. Each tuple represents a change to 
    be made on the columns of the CREATE Query. The tuple is formed by a 
    regular expression which finds the correct column, a string with the 
    original text to be replaced, and a string with the replacement text.
    """

    def __init__(self, files=None, rules=None):
        self._config = ConfigParser.ConfigParser()
        self._config.read('ods2dw.cfg')

        if files != None:
            self.addFiles(files)
        if rules != None:
            self.addRules(rules)

        self._ODSViewTemplate = self._config.get('Template', 'odsview')
        self._DWTableTemplate = self._config.get('Template', 'dwtable')
        self._SP_PopulateDWTTemplate = self._config.get('Template', 'dwsp')
        self._TR_PopulateDWHTemplate = self._config.get('Template', 'dwtr')
        self._DWHMTableTemplate = self._config.get('Template', 'dwhmtable')
        self._SP_ManagePartTemplate = self._config.get('Template', 'dwmngpart')

    def _get_dw_columns(self):
        """
        Property method for _dw_columns. Adds '[Dbatchdate]' to the end of 
        _ods_columns.
        """
        if self._ods_columns != '':
            return self._ods_columns + '[Dbatchdate]'
        else:
            return ''

    _files = list()
    _rules = list()
    _dw_columns = property(_get_dw_columns)
    _table_name = ''
    _ods_columns = ''
    _ods_col_descr = list()

    def addFile(self, file):
        """
        _files+file
        """
        self._files.append(file)

    def addFiles(self, files):
        """
        Add files to _files
        """
        for newfile in files:
            self.addFile(newfile)
    
    def removeFile(self, files):
        """
        Removes the specified files from _files
        """
        for newfile in files:
            self._files.remove(newfile)

    def clearFiles(self):
        """
        Removes all files from _files
        """
        self._files = list()

    def addRule(self, pattern, old, new):
        """
        _rules.append((re.compile(pattern), old, new))
        """
        self._rules.append((re.compile(pattern), old, new))

    def addRules(self, rules):
        """
        Add rules to _rules
        """
        for rule in rules:
            self.addRule(rule[0], rule[1], rule[2])

    def generateFiles(self):
        """
        For each file creates the view, table, stored procedure and trigger.
        """
        for newfile in self._files:
            self.parseODSTable(newfile)
            self.createODSView()
            self.createDWTable()
            self.createSP_PopulateDWTable()
            self.createDWHMTable()
            self.createDWTrigger()
            self.createSP_ManagePartition()


    def parseODSTable(self, file):
        """
        Reads a file and stores its table name and columns.

        Writes to variables:
         - _ods_columns
         - _ods_col_descr
         - _table_name
         - _table_number
         - _historic_table_name
        """
        fd = open(file, 'r')
        matchTable = None
        matchColumn = None
        self._ods_columns = ''
        self._ods_col_descr = list()

        for line in fd.readlines():
            if matchTable == None: # found table name
                matchTable = re.match(odstablename, line)
            else: # searching for columns
                matchColumn = re.match(odscolumns, line)
                if matchColumn != None: # found column
                    self._ods_col_descr.append(line.lstrip())
                    self._ods_columns = self._ods_columns \
                        + matchColumn.group(1) + ',\n'
                else: # no more columns
                    break

        self._table_name = matchTable.group(1)
        self._table_number = self._table_name[:3]
        self._historic_table_name = '%sHM_%s' %(self._table_number, 
                                                self._table_name[4:])
        fd.close()

    def createODSView(self):
        """
        createODSView() -> file

        Writes a file with the CREATE VIEW Query for the ODS Table.
        """
        ods_view_columns = ''
        for column in self._ods_columns.split():
            for columnType in dw_insert:
                columnChange = re.match(columnType[0], column)
                if columnChange != None:
                    column = columnType[1] % {'column': columnChange.group(1)}
                    break
            ods_view_columns = ods_view_columns + column + '\n'

        odsTemplate = open(self._ODSViewTemplate, 'r').read()
        odsvfilename = self._config.get('Filename', 'odsview', 1)
        newview = odsTemplate % {'tablename': self._table_name,
                                 'columns': ods_view_columns[:-1]}
        fd = open(odsvfilename % (self._table_name), 'w')
        fd.write(newview)
        fd.close()

    def createDWTable(self):
        """
        createDWTable() -> file

        Writes a file with the CREATE TABLE Query for the DW Table.
        """
        newcolumns = ''
        for column in self._ods_col_descr:
            for rule in self._rules:
                if rule[0].search(column):
                    column = re.sub(rule[1], rule[2], column)
                    break
            newcolumns += column

        dwTemplate = open(self._DWTableTemplate, 'r').read() 
        dwtfilename = self._config.get('Filename', 'dwtable', 1)
        newtable = dwTemplate % {'tablename': self._table_name,
                                 'columns': newcolumns[:-1]}
        fd = open(dwtfilename % (self._table_name), 'w')
        fd.write(newtable)
        fd.close()

    def createSP_PopulateDWTable(self):
        """
        createSP_PopulateDWTable() -> file

        Writes a file with the CREATE STORED PROCEDURE Query which populates 
        the DW Table with the ODS View.
        """
        spTemplate = open(self._SP_PopulateDWTTemplate, 'r').read()
        spdwfilename = self._config.get('Filename', 'dwsp', 1)

        ods_columns = ''
        matchColumn = None
        for column in self._ods_col_descr:
            matchColumn = re.match(odscolumns, column)
            if matchColumn != None:
                ods_columns = ods_columns + matchColumn.group(1) \
                    + ',\n'

        sp = spTemplate % {'table_name': self._table_name,
                           'dw_columns': self._dw_columns,
                           'ods_columns': ods_columns[:-1]}

        fdsp = open(spdwfilename % (self._table_name), 'w')
        fdsp.write(sp)
        fdsp.close()        

    def createDWTrigger(self):
        """
        createDWTrigger() -> file

        Writes a file with the CREATE TRIGGER Query which populates the DWHM 
        Table every time the DW Table is writen or updated.
        """
        dwh_columns = ''
        for column in self._dw_columns.splitlines():
            for change in dwh_change:
                if change[0].search(column):
                    column = re.sub(change[1], change[2], column)
                    break
            dwh_columns += column + '\n'

        dwTemplate = open(self._TR_PopulateDWHTemplate, 'r').read()
        dwhfilename = self._config.get('Filename', 'dwtr', 1)
        newtrigger = dwTemplate % {'table_name': self._table_name,
                                   'table_number': self._table_number,
                                   'historic_table_name':
                                       self._historic_table_name,
                                   'dw_columns': self._dw_columns,
                                   'dwh_columns' : dwh_columns}
        fd = open(dwhfilename % (self._table_number, self._table_number), 'w')
        fd.write(newtrigger)
        fd.close()

    def createDWHMTable(self):
        """
        createDWHMTable() -> file

        Writes a file with the CREATE TABLE Query for DW Historic Monthly Table.
        """
        newcolumns = ''
        for column in self._ods_col_descr:
            for rule in self._rules:
                if rule[0].search(column):
                    column = re.sub(rule[1], rule[2], column)
                    break
            newcolumns += column

        dwTemplate = open(self._DWHMTableTemplate, 'r').read() 
        dwtfilename = self._config.get('Filename', 'dwhmtable', 1)
        newtable = dwTemplate % {'historic_table_name':
                                     self._historic_table_name,
                                 'columns': newcolumns[:-1]}
        fd = open(dwtfilename % (self._historic_table_name), 'w')
        fd.write(newtable)
        fd.close()

    def createSP_ManagePartition(self):
        """
        createSP_ManagePartition() -> file

        Writes a file with the CREATE STORED PROCEDURE Query which manages 
        the Creation, Deletion and Updating of the Partitions for the DW 
        Historic Monthly Table.
        """
        dwTemplate = open(self._SP_ManagePartTemplate, 'r').read()
        dwfilename = self._config.get('Filename', 'dwmngpart', 1)
        newsp = dwTemplate % {'table_number': self._table_number,
                              'table_name': self._table_name[4:]}
        fd = open(dwfilename % (self._table_number), 'w')
        fd.write(newsp)
        fd.close()

odstablename = r"CREATE TABLE \[ods\]\.\[ODST([0-9]{3}\_[a-zA-Z0-9]+)\]"
odscolumns = r"\t?(\[([CDFGIV][a-z0-9]+|S[A-Z0-9]+)\]).* NULL"

ods2dw_changes = [
    ('^[ \t]*\[G[a-zA-Z0-9]*\]\ *\[char\]', 
     ' \[char\]', 
     ' [nvarchar]'),
    ('^[ \t]*\[D[a-zA-Z0-9]+\][ \t]+\[decimal\]\(7, 0\)', 
     ' \[decimal\]\(7, 0\)', 
     ' [datetime]'),
    ('^[ \t]*\[F[a-zA-Z0-9]+\][ \t]+\[char\][ \t]*\(1\)',
     ' \[char\]\(1\)',
     ' [bit]'),
    ('[ \t\.a-zA-Z0-9]*\[ods\]\.\[ODS',
     '\[ods\]\.\[ODS',
     '[dw].[DW'),
    ('^[ \t]*\)[ \t]*ON[ \t]*\[PRIMARY\][ \t]*$',
     '\)[ \t]*ON',
     '\t,[Dbatchdate] [datetime] NULL\n) ON'),
]

dw_insert = [
    ('^[ \t]*(\[G[a-zA-Z0-9]+\]),$',
     'rtrim(ltrim(%(column)s)) as %(column)s,'),
    ('^[ \t]*(\[D[a-zA-Z0-9]+\]),$',
     'dbo.f_Datetime(%(column)s) as %(column)s,'),
    ('^[ \t]*(\[F[a-zA-Z0-9]+\]),$',
     'CASE WHEN %(column)s = \'Y\' THEN 1 ELSE 0 END as %(column)s,'),
]

dwh_change = [
    (re.compile('\[?Dbatchdate\]?'),
     '\[Dbatchdate\]',
     'dbo.f_GetMonth((select Dbatchdate from dw.DWT000_SP))')
]


if __name__ == '__main__':
    changer = Ods2Dw(files=sys.argv[2:], rules=ods2dw_changes)
    if sys.argv[1] == '1':
        changer.generateFiles()
    elif sys.argv[1] == '2':
        changer.parseODSTable(changer._files[0])
        changer.createDWHMTable()
        changer.createDWTrigger()
        changer.createSP_ManagePartition()
