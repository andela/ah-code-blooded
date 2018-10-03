from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializer import ProfileSerializer
from .renderers import ProfileJSONRenderer


class ProfileListView(ListAPIView):
    # Remember to only permit authenticated users
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, *args, **kwargs):
        """
        Get a listing of user profiles. Excludes the requester.
        """
        # Remember to exclude the user that is making this request
        serializer = self.serializer_class(Profile.objects.all(), many=True)
        return Response({'profiles': serializer.data}, status=status.HTTP_200_OK)
