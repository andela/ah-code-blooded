import json

from rest_framework.renderers import JSONRenderer


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
        errors = data.get('errors', None)
        if errors is not None:
            return super().render(data)

        return json.dumps({
            'article': data
        })
