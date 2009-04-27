import re
import string
import ConfigParser

class Ods2Dw(object):
    """
    """

    def __init__(self, files=None, rules=None):
        self._config = ConfigParser.ConfigParser()
        self._config.read('ods2dw.cfg')

        self._rules = list()
        self._files = list()
        self._ODSViewTemplate = self._config.get('Ods2Dw', 'odsviewtemplate')
        self._DWViewTemplate = self._config.get('Ods2Dw', 'dwviewtemplate')
        self._SP_PopulateDWTTemplate = self._config.get('Ods2Dw', 'spdwtemplate')

    def _get_dw_columns(self):
        if self._ods_columns != '':
            return self._ods_columns + '\t[Dbatchdate]\n'
        else:
            return ''

    _dw_columns = property(_get_dw_columns)    
    _table_name, _ods_columns = '', ''

    def addFile(self, *files):
        for file in files:
            self._files.append(file)
    
    def removeFile(self, *files):
        for file in files:
            self._files.remove(file)

    def clearFiles(self):
        self._files = list()

    def addRule(self, pattern, old, new):
        self._rules.append((re.compile(pattern), old, new))

    def addRules(self, *rules):
        for rule in rules:
            self._rules.append(rule)

    def createDWTable(self):
        for file in self._files:
            newlines = ''
            fd = open(file, 'r')
            for line in fd.readlines():
                for rule in self._rules:
                    if rule[0].search(line):
                        line = re.sub(rule[1], rule[2], line)
                        break
                newlines += line
            fd.close()
 
            fd = open(re.sub('((ods)?|(ODS)?)\.sql', 
                             'DW.sql', 
                             file),
                      'w')
            fd.write(newlines)
            fd.close()

    def createODSView(self):
        odsTemplate = open(self._ODSViewTemplate, 'r').read()
        odsvfilename = self._config.get('Ods2Dw', 'odsvfilename', 1)
        
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

    def createSP_PopulateDWTable(self):
        spTemplate = open(self._SP_PopulateDWTTemplate, 'r').read()
        spdwfilename = self._config.get('Ods2Dw', 'spdwfilename', 1)

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
            newsp = spTemplate % {'table_name': self._table_name,
                                  'columns': self._dw_columns}
            fdsp = open(spdwfilename % (self._table_name), 'w')
            fdsp.write(newsp)
            fdsp.close()

    def createDWView(self):
        dwTemplate = open(self._DWViewTemplate, 'r').read()
        dwvfilename = self._config.get('Ods2Dw', 'dwvfilename', 1)
        
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
                                    'columns': self._dw_columns}
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


if __name__ == '__main__':
    pass
