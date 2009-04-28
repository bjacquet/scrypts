import unittest
import os
import sys
sys.path.append(os.getcwd())
import ods2dw


class TestFunctions(unittest.TestCase):
    

    def insertRules(self, inst, rules):
        for rule in rules:
            inst.addRule(rule[0], rule[1], rule[2])

    def setUp(self):
        self.dw = ods2dw.Ods2Dw()
        self.dw.addFile('tableODS.sql')

    def testCreateDWTable(self):
        self.insertRules(self.dw, ods2dw.ods2dw_changes)
        self.dw.createDWTable()

    def testCreateODSView(self):
        self.dw.createODSView()

    def testCreateSP(self):
        self.dw.createSP_PopulateDWTable()

    def testCreateDWView(self):
        self.dw.createDWView()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
#     unittest.main()
