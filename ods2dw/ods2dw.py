import re
import string
import sys
import ConfigParser

class Ods2Dw(object):
    """
    """

    def __init__(self, files=None, rules=None):
        self._config = ConfigParser.ConfigParser()
        self._config.read('ods2dw.cfg')

        if files != None:
            self.addFiles(files)
        if rules != None:
            self.addRules(rules)

        self._ODSViewTemplate = self._config.get('Template', 'odsview')
        self._DWViewTemplate = self._config.get('Template', 'dwview')
        self._DWTableTemplate = self._config.get('Template', 'dwtable')
        self._SP_PopulateDWTTemplate = self._config.get('Template', 'dwsp')
        self._TR_PopulateDWHTemplate = self._config.get('Template', 'dwtr')

    def _get_dw_columns(self):
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
        self._files.append(file)

    def addFiles(self, files):
        for file in files:
            self.addFile(file)
    
    def removeFile(self, files):
        for file in files:
            self._files.remove(file)

    def clearFiles(self):
        self._files = list()

    def addRule(self, pattern, old, new):
        self._rules.append((re.compile(pattern), old, new))

    def addRules(self, rules):
        for rule in rules:
            self.addRule(rule[0], rule[1], rule[2])

    def generateFiles(self):
        for file in self._files:
            self.parseODSTable(file)
            self.createODSView_2()
            self.createDWTable_2()
            self.createSP_PopulateDWTable_2()
            self.createDWView_2()

    def parseODSTable(self, file):
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
        fd.close()

    def createODSView_2(self):
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

    def createODSView(self):
        odsTemplate = open(self._ODSViewTemplate, 'r').read()
        odsvfilename = self._config.get('Filename', 'odsview', 1)
        
        for file in self._files:
            fd = open(file, 'r')
            matchTable = None
            matchColumn = None
            for line in fd.readlines():
                if matchTable == None: # found table name
                    matchTable = re.match(odstablename, line)
                else: # searching for columns
                    matchColumn = re.match(odscolumns, line)
                    if matchColumn != None: # found column
                        self._ods_columns = self._ods_columns + '\t' \
                            + matchColumn.group(1) + ',\n'
                    else: # no more columns
                        break

            self._table_name = matchTable.group(1)
            fd.close()
            newview = odsTemplate % {'tablename': self._table_name,
                                     'columns': self._ods_columns}
            fdv = open(odsvfilename % (self._table_name), 'w')
            fdv.write(newview)
            fdv.close()

    def createDWTable_2(self):
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

    def createDWTable(self):
        dwtfilename = self._config.get('Filename', 'dwtable', 1)
        for file in self._files:
            newlines = ''
            matchTable = None
            fd = open(file, 'r')
            for line in fd.readlines():
                if matchTable == None: # found table name
                    matchTable = re.match(odstablename, line)
                for rule in self._rules:
                    if rule[0].search(line):
                        line = re.sub(rule[1], rule[2], line)
                        break
                newlines += line

            self._table_name = matchTable.group(1)
            fd.close()
            fd = open(dwtfilename % (self._table_name), 'w')
            fd.write(newlines)
            fd.close()

    def createSP_PopulateDWTable_2(self):
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
        
    def createSP_PopulateDWTable(self):
        spTemplate = open(self._SP_PopulateDWTTemplate, 'r').read()
        spdwfilename = self._config.get('Filename', 'dwsp', 1)

        for file in self._files:
            fd = open(file, 'r')
            matchTable = None
            matchColumn = None
            for line in fd.readlines():
                if matchTable == None: # found table name
                    matchTable = re.match(odstablename, line)
                else: # searching for columns
                    matchColumn = re.match(odscolumns, line)
                    if matchColumn != None: # found column
                        self._ods_columns = self._ods_columns + '\t' \
                            + matchColumn.group(1) + ',\n'
                    else: # no more columns
                        break

            fd.close()
            self._table_name = matchTable.group(1)
            sp = spTemplate % {'table_name': self._table_name,
                               'dw_columns': self._dw_columns,
                               'ods_columns': self._ods_columns}

            select = False
            newsp = ''
            for line in sp.splitlines(): 
                if not select:
                    newsp = newsp + line + '\n'
                    if line == 'SELECT':
                        select = True
                    continue

                column = None
                for columnType in dw_insert:
                    column = re.match(columnType[0], line)
                    if column != None:
                        line = columnType[1] % {'column': column.group(1)}
                        break
                newsp = newsp + line + '\n'

            fdsp = open(spdwfilename % (self._table_name), 'w')
            fdsp.write(sp)
            fdsp.close()

    def createDWView_2(self):
        dwTemplate = open(self._DWViewTemplate, 'r').read()
        dwvfilename = self._config.get('Filename', 'dwview', 1)
        newview = dwTemplate % {'tablename': self._table_name,
                                'columns': self._ods_columns[:-1]}
        fd = open(dwvfilename % (self._table_name), 'w')
        fd.write(newview)
        fd.close()

    def createDWView(self):
        dwTemplate = open(self._DWViewTemplate, 'r').read()
        dwvfilename = self._config.get('Filename', 'dwview', 1)
        
        for file in self._files:
            fd = open(file, 'r')
            matchTable = None
            matchColumn = None
            for line in fd.readlines():
                if matchTable == None: # found table name
                    matchTable = re.match(odstablename, line)
                else: # searching for columns
                    matchColumn = re.match(odscolumns, line)
                    if matchColumn != None: # found column
                        self._ods_columns = self._ods_columns + '\t' \
                            + matchColumn.group(1) + ',\n'
                    else: # no more columns
                        break

            self._table_name = matchTable.group(1)
            fd.close()
            newview = dwTemplate % {'tablename': self._table_name,
                                    'columns': self._ods_columns}
            fdv = open(dwvfilename % (self._table_name), 'w')
            fdv.write(newview)
            fdv.close()

    def createDWTrigger(self):
        dwh_columns = ''
        for column in self._dw_columns.splitlines():
            for change in dwh_change:
                if change[0].search(column):
                    column = re.sub(change[1], change[2], column)
                    break
            dwh_columns += column + '\n'

        table_number = self._table_name[:3]
        historic_table_name = '%sHM_%s' % (table_number, self._table_name[4:])
        dwTemplate = open(self._TR_PopulateDWHTemplate, 'r').read()
        dwhfilename = self._config.get('Filename', 'dwtr', 1)
        newtrigger = dwTemplate % {'table_name': self._table_name,
                                   'table_number': table_number,
                                   'historic_table_name': historic_table_name,
                                   'dw_columns': self._dw_columns,
                                   'dwh_columns' : dwh_columns}
        fd = open(dwhfilename % (table_number, table_number), 'w')
        fd.write(newtrigger)
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
        changer.createODSView()
        changer.createDWTable()
        changer.createSP_PopulateDWTable()
        changer.createDWView()
    elif sys.argv[1] == '2':
        changer.generateFiles()
    elif sys.argv[1] == '3':
        changer.parseODSTable(changer._files[0])
        changer.createDWTrigger()
