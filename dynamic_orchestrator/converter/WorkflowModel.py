import json
import string


def generate(nodelist,application_type):
    dict_template = {}

    for x in nodelist:
        if 'ACCORDION.Cloud_Framework' in x.get_type():
            workflows = x.get_workflows()
            for scenario in workflows:
                actions = scenario.get('actions')
                for action in actions:
                    components = action.get('components')
                    if components:
                        for component in components:
                            target = component.get('component')
                            application_component = application_type + "-" + target.lower()
                            component.update(component=application_component)
                            component.update(type=component.get('type').lower())
                    send = action.get('send')
                    if send:
                        for s in send:
                            component = s.get('component')
                            source_application_component = application_type+"-"+component
                            to = s.get('to')
                            target_application_component = application_type+"-"+to
                            s.update(component=source_application_component, to=target_application_component)
            dict_template = {'worklow_set': workflows}

    return dict_template
