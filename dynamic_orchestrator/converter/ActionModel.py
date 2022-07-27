import json


def generate(nodelist, application):
    dict_template = {}

    for x in nodelist:
        if 'ACCORDION.Cloud_Framework' in x.get_type():
            actions = x.get_actions()
            for action in actions:
                components = action.get('components')
                for component in components:
                    target = component.get('component')
                    component.update(component=application + "-" + target.lower())
                    component.update(type=component.get('type').lower())

            dict_template['action_set'] = []
            dict_template['action_set'].append(actions)

    return dict_template
