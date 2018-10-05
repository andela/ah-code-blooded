import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList


class ArticleJSONRenderer(JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        If the view throws an error, 'data' will contain errors key, the default JSONRenderer will handle this
        errors, so we need to check for this case
        :param data:
        :param accepted_media_type:
        :param renderer_context:
        :return:
        """
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
                'data': {
                    'articles': data
                }
            })

        return json.dumps({
            'status': 'success',
            'data': {
                'article': data
            }
        })


class RatingJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # If the view throws an error (such as the user can't be authenticated
        # or something similar), `data` will contain an `errors` key. We want
        # the default JSONRenderer to handle rendering errors, so we need to
        # check for this case.
        errors = data.get('errors', None)

        if errors is not None:
            # As mentioned about, we will let the default JSONRenderer handle
            # rendering errors.
            return super().render(data)

        # Finally, we can render our data under the "user" namespace.
        return json.dumps({
            'rating': data
        })
