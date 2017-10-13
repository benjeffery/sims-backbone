import unittest

from test_location import TestLocation
from test_sample import TestSample


def my_suite():
    suite = unittest.TestSuite()
    result = unittest.TestResult()
    suite.addTest(unittest.makeSuite(TestLocation))
    suite.addTest(unittest.makeSuite(TestSample))
    runner = unittest.TextTestRunner()
    print(runner.run(suite))

my_suite()
