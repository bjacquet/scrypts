import re
import string


class Ods2Dw(object):
    """
    """

    _rules = list()
    _files = list()
    _ODSViewTemplate = 'createODSVTemplate.sql'
    _DWViewTemplate = 'createDWVTemplate.sql'

    def __init__(self, files=None, rules=None):
        """
        """

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

    def replaceLines(self):
        for file in self._files:
            newlines = ''
            fd = open(file, 'r')
            for line in fd.readlines():
                for rule in self._rules:
                    if rule[0].search(line):
                        line= re.sub(rule[1], rule[2], line)
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
        table_name = ''
        columns = ''
        odsTemplate = open(self._ODSViewTemplate, 'r').read()
        
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
                        columns = columns + '\t' + matchColumn.group(1) + ',\n'
                    else: # no more columns
                        break

            table_name = matchTable.group(1)

            fd.close()
            table_name = matchTable.group(1)
            newview = odsTemplate % {'tablename': table_name,
                                     'columns': columns}
            fdv = open('createODSV%s.sql' % (table_name), 'w')
            fdv.write(newview)
            fdv.close()

odstablename = r"^CREATE TABLE \[ods\]\.\[ODST([0-9]{3}\_[a-zA-Z0-9]+)\]"
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
]


def insertRules(inst, rules):
    for rule in rules:
        inst.addRule(rule[0], rule[1], rule[2])

def createDWtable():
    dw = Ods2Dw()    
    dw.addFile('tableODS.sql')
    insertRules(dw, ods2dw_changes)
    dw.replaceLines()

def createODSView():
    dw = Ods2Dw()
    dw.addFile('tableODS.sql')
    dw.createODSView()
    

if __name__ == '__main__':
    pass
