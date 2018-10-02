import os

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .renderers import UserJSONRenderer

from rest_framework.reverse import reverse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)
from .models import User


class RegistrationAPIView(CreateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = User.objects.filter(email=user['email']).first()

        RegistrationAPIView.send_account_activation_email(user, request)

        msg = 'We have sent you an activation link'
        return Response({"message": msg}, status=status.HTTP_201_CREATED)

    @staticmethod
    def send_account_activation_email(user, request=None, send_email=True):
        """

        :param user:
        :param request:
        :param send_email: Testing will pass this as false in order to prevent actually sending an email to mock users
        :return:
        """
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.username)).decode("utf-8")

        if send_email:
            email = user.email
            username = user.username
            domain = get_current_site(request).domain
            from_email = os.getenv("EMAIL_HOST_SENDER ")

            email_subject = 'Activate your Author\'s Haven account.'
            activation_link = "http://" + domain + reverse("authentication:activate-account",
                                                           kwargs={"token": token, "uid": uid})
            email_message = render_to_string('email_verification.html',
                                             {
                                                 'activation_link': activation_link,
                                                 'title': email_subject,
                                                 'username': username
                                             })
            text_content = strip_tags(email_message)
            msg = EmailMultiAlternatives(
                email_subject, text_content, from_email, to=[email])
            msg.attach_alternative(email_message, "text/html")
            msg.send()

        return token, uid


class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountVerificationView(APIView):

    def get(self, request, token, uid):
        username = force_text(urlsafe_base64_decode(uid))

        user = User.objects.filter(username=username).first()
        validate_token = default_token_generator.check_token(user, token)

        data = {"message": "Congratulations! Your account has been activated. Please log in."}
        st = status.HTTP_200_OK

        if not validate_token:
            data['message'] = "Your activation link is Invalid or has expired. Kindly register."
            st = status.HTTP_400_BAD_REQUEST
        else:
            # Mark the user as verified
            user.is_verified = True
            user.save()

        return Response(data, status=st)
