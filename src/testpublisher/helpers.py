import xml.etree.ElementTree as ET

# def parse_xml(file_path):
#     tree = ET.parse(file_path)
#     suite = tree.getroot()
    
#     test_plans = []
#     test_suites = []
#     test_cases = []

#     suite_name = suite.attrib['name'].split('.')[-1].split('-')[0]
#     suite_tests = int(suite.attrib['tests'])
#     suite_errors = int(suite.attrib['errors'])
#     suite_failures = int(suite.attrib['failures'])
#     test_suites.append({'name': suite_name, 'tests': suite_tests, 'errors': suite_errors, 'failures': suite_failures})

#     # for suite in suite.findall('testsuite'):
#     #     print(suite.findall('testcase'))
    
#     for case in suite.findall('testcase'):
#         case_name = case.attrib['name']
#         case_time = float(case.attrib['time'])
#         failure = case.find('failure')
#         case_status = 'failed' if failure is not None else 'passed'
#         test_cases.append({'name': case_name, 'time': case_time, 'status': case_status})
    
#     test_plans.append({'suites': test_suites, 'cases': test_cases})
    
#     return test_plans

def parse_xml(file_path):
    test_plans = []

    tree = ET.parse(file_path)
    tree_suite = tree.getroot()

    found_suites = tree_suite.findall('testsuite')
    if len(found_suites) == 0:
        found_suites = [tree_suite]

    for suite in found_suites:
        test_suites = []
        test_cases = []

        suite_name = suite.attrib['name'].split('.')[-1].split('-')[0]
        suite_tests = int(suite.attrib['tests'])
        suite_errors = int(suite.attrib['errors'])
        suite_failures = int(suite.attrib['failures'])
        test_suites.append({'name': suite_name, 'tests': suite_tests, 'errors': suite_errors, 'failures': suite_failures})

        for case in suite.findall('testcase'):
            case_name = case.attrib['name']
            case_time = float(case.attrib['time'])
            failure = case.find('failure')
            case_status = 'failed' if failure is not None else 'passed'
            test_cases.append({'name': case_name, 'time': case_time, 'status': case_status})
        
        test_plans.append({'suites': test_suites, 'cases': test_cases})
    
    return test_plans
