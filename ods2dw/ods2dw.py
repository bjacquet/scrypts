import re
import string
import sys
import ConfigParser

class Ods2Dw(object):
    """
    """
    _files = list()
    _rules = list()

    def __init__(self, files=None, rules=None):
        self._config = ConfigParser.ConfigParser()
        self._config.read('ods2dw.cfg')

        if files != None:
            self.addFiles(files)
        if rules != None:
            self.addRules(rules)

        self._ODSViewTemplate = self._config.get('Template', 'odsview')
        self._DWViewTemplate = self._config.get('Template', 'dwview')
        self._SP_PopulateDWTTemplate = self._config.get('Template', 'dwsp')

    def _get_dw_columns(self):
        if self._ods_columns != '':
            return self._ods_columns + '\t[Dbatchdate]\n'
        else:
            return ''

    _dw_columns = property(_get_dw_columns)
    _table_name, _ods_columns = '', ''


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
                               'columns': self._dw_columns}

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


odstablename = r"CREATE TABLE \[ods\]\.\[ODST([0-9]{3}\_[a-zA-Z0-9]+)\]"
odscolumns = r"\t(\[[CDFGIV][a-z0-9]+\]).* NULL"

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
     '\trtrim(ltrim(%(column)s)),'),
    ('^[ \t]*(\[D[a-zA-Z0-9]+\]),$',
     '\tdbo.f_Datetime(%(column)s),'),
    ('^[ \t]*(\[F[a-zA-Z0-9]+\]),$',
     '\tCASE WHEN %(column)s = \'Y\' THEN 1 ELSE 0 END,'),
]


if __name__ == '__main__':
    changer = Ods2Dw(files=sys.argv[1:], rules=ods2dw_changes)
    changer.createODSView()
    changer.createDWTable()
    changer.createSP_PopulateDWTable()
    changer.createDWView()

