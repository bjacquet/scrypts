import unittest
import os
import sys
sys.path.append(os.getcwd())
import ods2dw


class TestFunctions(unittest.TestCase):
    

    def insertRules(self, inst, rules):
        for rule in rules:
            inst.addRule(rule[0], rule[1], rule[2])

    def testCreateDWTable(self):
        dw = ods2dw.Ods2Dw()
        dw.addFile('tableODS.sql')
        self.insertRules(dw, ods2dw.ods2dw_changes)
        dw.createDWTable()

    def testCreateODSView(self):
        dw = ods2dw.Ods2Dw()
        dw.addFile('tableODS.sql')
        dw.createODSView()

    def testCreateSP(self):
        dw = ods2dw.Ods2Dw()
        dw.addFile('tableODS.sql')
        dw.createSP_PopulateDWTable()

    def testCreateDWView(self):
        dw = ods2dw.Ods2Dw()
        dw.addFile('tableODS.sql')
        dw.createDWView()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
#     unittest.main()
