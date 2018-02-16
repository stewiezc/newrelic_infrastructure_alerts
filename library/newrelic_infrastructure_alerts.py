#!/usr/bin/python

DOCUMENTATION = '''
---
module: newrelic_infrastructure_alerts
short_description: Manage Alert Conditions for New Relic Infrastructure
'''

EXAMPLES = '''
https://docs.newrelic.com/docs/infrastructure/new-relic-infrastructure/infrastructure-alert-conditions/rest-api-calls-new-relic-infrastructure-alerts

- name: create host not reporting alert condition
  newrelic_infrastructure_alerts:
    admin_api_key: 12345678901234567890
    name: slack_host_not_reporting_5mins
    type: infra_host_not_reporting
    alerts_policy_name: slack_alert_policy
    critical_threshold:
      duration_minutes: 5
    state: present
  register: result

- name: create disk usage alert condition 
  newrelic_infrastructure_alerts:
    admin_api_key: 12345678901234567890
    name: pagerduty_disk_used_above_90%
    type: infra_metric
    alerts_policy_name: pagerduty_alert_policy
    event_type: StorageSample
    select_value: diskUsedPercent
    comparison: above
    critical_threshold:
      value: 90
      duration_minutes: 5
      time_function: any
    state: present
  register: result

- name: process running condition
  newrelic_infrastructure_alerts:
    admin_api_key: 12345678901234567890
    name: slack_java_process_not_running
    type: infra_process_running
    alerts_policy_name: slack_alert_policy
    where_clause: (hostname LIKE '%websrv%')
    comparison: below
    critical_threshold:
      value: 1
      duration_minutes: 15
    process_where_clause: (commandName = 'java')
    state: present
  register: result
'''

from ansible.module_utils.basic import *
import requests

infra_api_url = "https://infra-api.newrelic.com"
alerts_api_url = "https://api.newrelic.com"

def get_policy_id(alerts_policy_name, admin_api_key):
    policy_id_url = "{}{}" . format(alerts_api_url, '/v2/alerts_policies.json')

    headers = {
            "X-Api-Key": admin_api_key,
            "Content-Type": "application/json"
        }

    result = requests.get(policy_id_url + "?filter[name]=" + alerts_policy_name, headers=headers)
    policy_id = result.json()['policies'][0]['id']
    return policy_id

def get_condition_id(condition_name, admin_api_key):
    url = "{}{}" . format(infra_api_url, '/v2/alerts/conditions')

    headers = {
        "X-Api-Key": "{}" . format(admin_api_key)
    }

    result = requests.get(url, headers=headers)
    if result.json()['data']:
        for condition in result.json()['data']:
            if condition['name'] == condition_name:
                condition_id = condition['id']
                return condition_id
            else:
                continue
        # condition id not found
        return "None"
    else:
        return "None"

def create_alert(data):
    admin_api_key = data['admin_api_key']
    del data['admin_api_key']

    url = "{}{}" . format(infra_api_url, '/v2/alerts/conditions')

    headers = {
        "X-Api-Key": admin_api_key,
        "Content-Type": "application/json"
    }

    post_data = {}
    post_data["data"] = data
    result = requests.post(url, json.dumps(post_data), headers=headers)
    if result.status_code == 201:
        return False, True, result.json()
    else:
        return True, False, result.json()

def update_alert(data):
    admin_api_key = data['admin_api_key']
    condition_name = data['name']

    condition_id = get_condition_id(condition_name, admin_api_key)

    del data['admin_api_key']

    url = "{}{}" . format(infra_api_url, '/v2/alerts/conditions')

    headers = {
        "X-Api-Key": admin_api_key,
        "Content-Type": "application/json"
    }

    post_data = {}
    post_data["data"] = data
    result = requests.post(url + '/' + str(condition_id), json.dumps(post_data), headers=headers)
    if result.status_code == 201:
        return False, True, result.json()
    else:
        return True, False, result.json()
    
def alerts_present(data):
    admin_api_key = data['admin_api_key']
    condition_name = data['name']
    del data['state']

    alerts_policy_name = data['alerts_policy_name']
    policy_id = get_policy_id(alerts_policy_name, admin_api_key)
    data.update({"policy_id": policy_id})
    del data['alerts_policy_name']

    url = "{}{}" . format(infra_api_url, '/v2/alerts/conditions')
    

    headers = {
        "X-Api-Key": "{}" . format(admin_api_key)
    }
    
    # check if alert condition exists
    result = requests.get(url, headers=headers)
    for alert in result.json()['data']:
        if data['name'] in alert['name']:
            # the alert condition exists. 
            for arg in data:
                if arg in alert:
                    if data[arg] == alert[arg]:
                        continue
                    else:
                        return update_alert(data)
                else:
                    continue
            return False, False, alert
        else:
            return create_alert(data)
    return create_alert(data)

    # default: something went wrong
    meta = {"status": result.status_code, 'response': result.json()}
    return True, False, meta

def alerts_absent(data):
    admin_api_key = data['admin_api_key']
    condition_name = data['name']

    condition_id = get_condition_id(condition_name, admin_api_key)
    if condition_id == "None":
        meta = {"response": "condition id not found"}
        return False, False, meta

    url = "{}{}" . format(infra_api_url, '/v2/alerts/conditions')

    headers = {
        "X-Api-Key": "{}" . format(admin_api_key)
    }

    result = requests.delete(url + '/' + str(condition_id), headers=headers)
    if result.status_code == 204:
        meta = {"status": result.status_code, "response": "Condition deleted"}
        return False, True, meta
    else:
        return True, False, result.json()

def main():
    fields = {
        "admin_api_key": {"required": True, "type": "str"},
        "name": {"required": True, "type": "str" },
        "type": {
            "required": False,
            "type": "str",
            "choices": ["infra_process_running", "infra_metric", "infra_host_not_reporting"]
        },
        "enabled": {
            "default": True,
            "choices": [True, False],
            "type": "bool"
        },
        "where_clause": {"required": False, "type": "str"},
        "process_where_clause": {"required": False, "type": "str"},
        "alerts_policy_name": {"required": False, "type": "str"},
        "critical_threshold": {"required": False, "type": "dict"},
        "warning_threshold": {"required": False, "type": "dict"},
        "comparison": {
            "required": False, 
            "type": "str",
            "choices": ["above", "below", "equal"]
        },
        "event_type": {"required": False, "type": "str"},
        "select_value": {"required": False, "type": "str"},
        "state": {
            "default": "present", 
            "choices": ['present', 'absent'],  
            "type": 'str' 
        },
    }
    
    choice_map = {
      "present": alerts_present,
      "absent": alerts_absent, 
    }
    
    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = choice_map.get(
        module.params['state'])(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
      module.fail_json(msg="Error", meta=result)

if __name__ == '__main__':  
    main()
