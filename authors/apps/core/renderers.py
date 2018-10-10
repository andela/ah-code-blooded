import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList


class BaseJSONRenderer(JSONRenderer):
    """
    Use this class to render your response in the JSend API format.
    In your Views, add the following:
    renderer_names=('<singular>','<plural>')
    This will render your data based on the renderer_names.

    For example to render users,
    In the User view:

    renderer_names=('user','users')

    will render as follows:

    {
        'status': 'success',
        'data' : {
            'users':[

            ]
        }
    }

    and for the a single user
    {
        'status' : 'success',
        'data' :{
            'user' :{
            }
        }
    }
    """
    charset = 'utf-8'
    single = None
    many = None

    def render(self, data, accepted_media_type=None, renderer_context=None):

        view = renderer_context['view']
        if hasattr(view, 'renderer_names'):
            names = view.renderer_names
            if len(names) != 2:
                raise ValueError("renderer_names should have two items in the form: (<singular>, <plural>)")
            else:
                self.single, self.many = names[0], names[1]

        if hasattr(data, 'get'):
            status = 'success'
            errors = data.get('errors', data.get('detail', None))
            if errors is not None:
                status = 'error'
            else:
                errors = data.get('message', None)

            # if there exist errors, set the status as error
            if errors is not None:
                message = errors
                # if there is only one error, use 'message' field to display the response
                if isinstance(message, str):
                    return json.dumps({
                        'status': status,
                        'message': message
                    })
                else:
                    # for dictionary or list, use data to display the response
                    return json.dumps({
                        'status': status,
                        'data': message
                    })

        if isinstance(data, ReturnList):
            return json.dumps({
                'status': 'success',
                'data': {self.many: data} if self.many else data
            })

        return json.dumps({
            'status': 'success',
            'data': {self.single: data} if self.single else data
        })
