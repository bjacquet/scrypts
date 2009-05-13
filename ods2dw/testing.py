import unittest
import os
import sys
sys.path.append(os.getcwd())
import ods2dw


class TestFunctions(unittest.TestCase):

    def setUp(self):
        self.dw = ods2dw.Ods2Dw(files=['sample.txt'],
                                rules=ods2dw.ods2dw_changes)

    def testCreateDWTable(self):
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
