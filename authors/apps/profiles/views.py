from django.http import Http404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer
from .renderers import ProfileJSONRenderer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from authors.apps.core.exceptions import ProfileDoesNotExist


class ProfileListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, *args, **kwargs):
        """
        Get a listing of user profiles. Excludes the requester.
        """
        try:
            queryset = Profile.objects.all().exclude(user=request.user)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist
        serializer = self.serializer_class(queryset, many=True)
        return Response({'profiles': serializer.data}, status=status.HTTP_200_OK)


class ProfileGetView(APIView):
    """Lists fetches a single profile and also updates a specific profile"""

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, username):
        """Fetches a specific profile filtered by the username"""

        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)
        return Response({'profile': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, username):
        """Allows authenticated users to update only their profiles."""
        data = request.data

        serializer = self.serializer_class(instance=request.user.profile, data=data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
