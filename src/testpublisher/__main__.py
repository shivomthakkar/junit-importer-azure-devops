import os
from testpublisher.helpers import parse_xml
from testpublisher.ado import create_bug, create_test_case, create_test_case_work_item, get_test_plan_details, get_test_suite_details, search_test_case, search_test_case_in_suite, set_test_case_outcome
from testpublisher.env_reader import load_config, get_var
import argparse
import logging

logging.getLogger("urllib3").setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-S', '--config-file', action='store')
args = parser.parse_args()
args = args.__dict__

load_config(args['config_file'])

logging.basicConfig(level=logging._nameToLevel[get_var("log_level", "INFO")])

folder_path = get_var("scan_folder") or "../coverage_files/"
logging.info(f"Scanning folder {folder_path}")
folder_path = os.path.join(os.getcwd(), folder_path)

for dirname, _, filenames in os.walk(folder_path):
    for filename in filenames:
        test_plans = parse_xml(os.path.join(dirname, filename))

        plan_id, suite_id = get_test_plan_details()
        for plan in test_plans:
            for suite in plan['suites']:
                suite_id = get_test_suite_details(plan_id, suite["name"])
                logging.info(f"Test Suite `{suite['name']}`, having {suite['tests']} tests")
                for case in plan['cases']:
                    work_item_id = search_test_case(case['name'])
                    if work_item_id is not None:
                        logging.debug(f"Found {work_item_id} - Skipping creating the work item on ADO")
                    else:
                        work_item_id = create_test_case_work_item(case['name'])

                    if not search_test_case_in_suite(plan_id, suite_id, work_item_id):
                        create_test_case(plan_id, suite_id, work_item_id)
                    else:
                        logging.debug(f"Found {work_item_id} - Skipping creating the test on ADO")

                    # Set the outcome of the test case
                    outcome = "Passed" if case['status'] == "passed" else "Failed"
                    set_test_case_outcome(plan_id, suite_id, work_item_id, outcome)
                    
                    if case['status'] == 'failed':
                        create_bug(case['name'])
