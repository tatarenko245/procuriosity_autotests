import json

import testrail

##########################
# GENERAL NOTES          #
######################################################################################################################
# Author: Roman Tatarenko
# Purpose: This script will create the UI functionality of 'Add Run'.
######################################################################################################################

##########################
# HOW TO USE THIS SCRIPT #
######################################################################################################################
# 1. Edit testrailAPIClient, suite_id, project_id, type_of_case values to match your criteria
# where:  testrailApiClient - get from TestRail web-site,
# suite_id - get from  TestRail web-site, which cases you want to use in TestRun,
# project_id -  get from  TestRail web-site, where you want to add TestRun,
# type_of_case =  get from  TestRail web-site, take from title of case in TestSuite (for example it will be regression
# or smoke).
# 2. Run the script
# 3. createdRunId is ID of created new run. You can use it everywhere

######################################################################################################################


# Details needed to make the API request
client = testrail.APIClient('https://ustudiocompany.testrail.io')  # do not include index.php?/api/v2
client.user = 'noreply@ustudio.company'  # TestRail email address
client.password = 'add2uStudio'  # TestRail password or API token
suite_id = 283
project_id = 13
# type_of_case = 'smoke'

sections_id = client.send_get(f'/get_sections/13&suite_id={suite_id}')
print("What section do you need? Set it, please in 'section_id'.")
print("Warning! The default value is 'sections_id[0]['id']'")
print(sections_id)
# What section do you need?
section_id = sections_id[0]["id"]

cases = client.send_get(f'/get_cases/13&suite_id={suite_id}&section_id={section_id}')
li = []
for case in cases:
    case_ids = case['id']
    li.append(case_ids)

post_body = {
    "suite_id": suite_id,
        "name": "BPE: update pn (open) (This is a new test run for automation)",
    "include_all": False,
    "case_ids": li

}
createRun = client.send_post(f'add_run/{project_id}', post_body)

createdRunId = createRun['id']
print("The new TestRun has been created. TestRun ==", createdRunId)
