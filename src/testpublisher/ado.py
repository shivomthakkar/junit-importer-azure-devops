import requests
import json
import jsonpath
from testpublisher.env_reader import get_var
import logging

configId = 49

def get_test_plan_details():
    organization = get_var('organization', '')
    project = get_var('project', '')
    pat = get_var('pat', '')
    plan_name = get_var('plan_name', '')
    try:
        url = f"https://dev.azure.com/{organization}/{project}/_apis/test/plans?api-version=5.0"
        response = requests.get(url=url, auth=('', pat))
        response_json = json.loads(response.text)

        plan_id = jsonpath.jsonpath(response_json, f"$.value.[?(@.name == '{plan_name}')].id")[0]
        suite_id = jsonpath.jsonpath(response_json, f"$.value.[?(@.name == '{plan_name}')].rootSuite.id")[0]
        return str(plan_id), suite_id
    except:
        logging.info(f"Can't find plan_name: {plan_name}")
        return -1, -1

def get_test_suite_details(plan_id, suite_name):
    organization = get_var('organization', '')
    project = get_var('project', '')
    pat = get_var('pat', '')

    url = f"https://dev.azure.com/{organization}/{project}/_apis/test/plans/{plan_id}/suites?api-version=5.0"
    response = requests.get(url=url, auth=('', pat))
    response_json = json.loads(response.text)
    suite_id = jsonpath.jsonpath(response_json, f"$.value.[?(@.name == '{suite_name}')].id")[0]
    return str(suite_id)

def search_test_case(testcase_name):
    organization = get_var('organization', '')
    project = get_var('project', '')
    area_path = get_var('area_path', '')
    pat = get_var('pat', '')
    
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0"
    payload = {"query": f"Select [System.Id] From WorkItems Where [System.WorkItemType] = 'Test Case' AND [System.Title] = '{testcase_name}' AND [Area Path] = '{area_path}'"}
    response = requests.post(url=url, json=payload, auth=('', pat), headers={'Content-Type': 'application/json'})
    response_json = json.loads(response.text)
    work_items = jsonpath.jsonpath(response_json, "$.workItems[*].id")
    if work_items:
        return work_items[0]
    return None

def create_test_case_work_item(testcase_name):
    organization = get_var('organization', '')
    project = get_var('project', '')
    area_path = get_var('area_path', '')
    iteration_path = get_var('iteration_path', '')
    pat = get_var('pat', '')

    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/$Test Case?api-version=7.1-preview.2"
    payload = [
        { "op": "add", "path": "/fields/System.Title", "from": None, "value": testcase_name },
        { "op": "add", "path": "/fields/System.AreaPath", "from": None, "value": area_path },
        { "op": "add", "path": "/fields/System.IterationPath", "from": None, "value": iteration_path },
        { "op": "add", "path": "/fields/Custom.HRSTestAutomationStatus", "from": None, "value": "Automated" }
    ]
    response = requests.post(url=url, json=payload, auth=('', pat), headers={'Content-Type': 'application/json-patch+json'})
    response_json = json.loads(response.text)
    work_item_id = jsonpath.jsonpath(response_json, "$.id")[0]
    return work_item_id

def search_test_case_in_suite(plan_id, suite_id, work_item_id):
    organization = get_var('organization', '')
    project = get_var('project', '')
    pat = get_var('pat', '')

    url = f"https://dev.azure.com/{organization}/{project}/_apis/test/plans/{plan_id}/suites/{suite_id}/testcases?api-version=6.0"
    response = requests.get(url=url, auth=('', pat))
    response_json = json.loads(response.text)
    test_case_ids = [str(tc['testCase']['id']) for tc in response_json['value']]
    return str(work_item_id) in test_case_ids

def create_test_case(plan_id, suite_id, work_item_id):
    organization = get_var('organization', '')
    project = get_var('project', '')
    pat = get_var('pat', '')

    url = f"https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{plan_id}/Suites/{suite_id}/TestCase?api-version=7.2-preview.3"
    payload = [{
        "pointAssignments": [{
            "configurationId": configId
        }],
        "workItem": {
            "id": work_item_id
        }
    }]
    response = requests.post(url=url, json=payload, auth=('', pat), headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        logging.debug(f"Test case {work_item_id} created successfully.")
    else:
        logging.debug(f"Failed to create test case {work_item_id}. Response: {response.text}")

def create_bug(testcase_name):
    organization = get_var('organization', '')
    project = get_var('project', '')
    pat = get_var('pat', '')

    try:
        title = testcase_name + " - Failed"
        url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/$bug?api-version=5.0"
        payload = '[{"op": "add","path": "/fields/System.Title","from": null,"value": "'+ title +'"}]'
        payload_json = json.loads(payload)
        response = requests.post(url=url, json=payload_json, auth=('', pat), headers={'Content-Type': 'application/json-patch+json'})
        response_json = json.loads(response.text)
        bug_id = jsonpath.jsonpath(response_json, "$.id")[0]
        logging.debug(f"Bug {bug_id} created for test case {testcase_name}.")
        return str(bug_id)
    except Exception as e:
        logging.debug('Something went wrong in creating the bug: ' + str(e))

def close_bug(testcase_name):
    organization = get_var('organization', '')
    project = get_var('project', '')
    pat = get_var('pat', '')
    area_path = get_var('area_path', '')

    try:
        title = testcase_name + " - Failed"
        query_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0"
        payload = '{"query": "Select [System.Id] From WorkItems Where [System.WorkItemType] = \'Bug\' AND [State] = \'New\' AND [System.Title] = \''+ title + '\' AND [Area Path] = \'' + area_path + '\'"}'
        payload_json = json.loads(payload)
        response = requests.post(url=query_url, json=payload_json, auth=('', pat), headers={'Content-Type': 'application/json'})
        response_json = json.loads(response.text)
        if(str(jsonpath.jsonpath(response_json, "$.workItems")[0]) != '[]'):
            bug_id = str(jsonpath.jsonpath(response_json, "$.workItems[0].id")[0])
            logging.debug('Bug ID to be closed: ' + bug_id)
            update_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/" + bug_id + "?api-version=6.0"
            update_payload = '[{"op":"test","path":"/rev","value":2},{"op":"add","path":"/fields/System.State","value":"Done"}]'
            update_payload_json = json.loads(update_payload)
            requests.patch(url=update_url, json=update_payload_json, auth=('', pat), headers={'Content-Type': 'application/json-patch+json'})
    except Exception as e:
        logging.debug('Something went wrong in closing the bug: ' + str(e))

def set_test_case_outcome(plan_id, suite_id, test_case_id, outcome):
    organization = get_var('organization', '')
    project = get_var('project', '')
    pat = get_var('pat', '')
    
    url = f"https://dev.azure.com/{organization}/{project}/_apis/test/Plans/{plan_id}/Suites/{suite_id}/points?testCaseId={test_case_id}"
    response = requests.get(url=url, auth=('', pat))
    response_json = response.json()
    if 'value' in response_json and response_json['value']:
        point_id = response_json['value'][0]['id']
        url = f"https://dev.azure.com/{organization}/{project}/_apis/test/Plans/{plan_id}/Suites/{suite_id}/points/{point_id}?api-version=7.1-preview.2"
        payload = {
            "outcome": outcome
        }
        response = requests.patch(url=url, json=payload, auth=('', pat), headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            logging.debug(f"Test case {test_case_id} outcome set to {outcome}.")
        else:
            logging.debug(f"Failed to set test case outcome. Response: {response.text}")
    else:
        logging.debug(f"Test case {test_case_id} not found in suite {suite_id}.")
