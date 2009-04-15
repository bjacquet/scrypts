import re
import string


class Ods2Dw(object):
    """
    """

    _rules = list()
    _files = list()

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

            fd = open(file, 'w')
            fd.write(newlines)
            fd.close()


def main():
    pass

if __name__ == '__main__':
    pass
