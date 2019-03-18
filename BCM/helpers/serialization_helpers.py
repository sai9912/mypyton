from django.core.serializers import serialize
import simplejson as json


def serialize_to_dict(instances, fields_only=False):
    """
    Serialize instance(s) to dictionary with force conversion of datetime,
    etc data types
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.create(email='root@root.ru', username='root')
    >>> instances = [user]
    >>> answer = serialize_to_dict(instances, fields_only=True)
    >>> answer[0]['username']
    'root'
    >>> answer = serialize_to_dict(instances, fields_only=False)
    >>> answer[0]['fields']['username']
    'root'
    >>> answer = serialize_to_dict(user, fields_only=False)
    >>> answer['fields']['email']
    'root@root.ru'
    >>> answer = serialize_to_dict(user, fields_only=True)
    >>> answer['email']
    'root@root.ru'
    """

    if isinstance(instances, (list, tuple, set)):
        serialized_data = serialize('json', instances)
        if fields_only:
            return [item['fields'] for item in json.loads(serialized_data)]
        else:
            return json.loads(serialized_data)
    else:
        serialized_data = serialize('json', [instances])
        if fields_only:
            return json.loads(serialized_data)[0]['fields']
        else:
            return json.loads(serialized_data)[0]
