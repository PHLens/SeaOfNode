import unittest
import logging
import time

#def run_tests(argv=UNITTEST_ARGS):
#    if TEST_IN_SUBPROCESS:
#        suite = unittest.TestLoader().loadTestsFromModule(__main__)
#        test_cases = []
#
#        def add_to_test_cases(suite_or_case):
#            if isinstance(suite_or_case, unittest.TestCase):
#                test_cases.append(suite_or_case)
#            else:
#                for element in suite_or_case:
#                    add_to_test_cases(element)
#
#        add_to_test_cases(suite)
#        failed_tests = []
#        for case in test_cases:
#            test_case_full_name = case.id().split('.', 1)[1]
#            exitcode = shell([sys.executable] + argv + [test_case_full_name])
#            if exitcode != 0:
#                failed_tests.append(test_case_full_name)
#
#        assert len(failed_tests) == 0, "{} unit test(s) failed:\n\t{}".format(
#            len(failed_tests), '\n\t'.join(failed_tests))
#    else:
#        unittest.main(argv=argv)

def testinfo(pre_message="\nTest case:", post_message="Test Time:"):
    def loader(func):
        def wrapper(*args, **kwargs):
            logging.info("\033[1;35m Current func: {}, {}. \033[0m" \
                         .format(type(args[0]).__name__, \
                         func.__name__))
            st_time = time.time()
            func(*args, **kwargs)
            logging.info("\033[1;30m Test time: %0.3f s. \033[0m" \
                         %(time.time() - st_time))
        return wrapper
    return loader

def graph_to_png(dot_file):
    import pydot
    graphs = pydot.graph_from_dot_file(dot_file)
    graphs[0].write_png("graph.png")