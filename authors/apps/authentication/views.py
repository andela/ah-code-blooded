from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView,CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
#from sendgrid.message import SendGridEmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template, render_to_string
from django.core.mail import send_mail

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, ResetPasswordSerializers, ForgotPasswordSerializer,
)


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

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request):

        email = request.data.get('email', {})
        serializer = self.serializer_class(data={"email":email})
        serializer.is_valid(raise_exception=True)
        email_subject = "Reset Your Password"
        content_message = get_template('reset_password.html')
        print (render_to_string(content_message))
        #send_mail('Subject here', 'Here is the message', 'from@example.com', [email] )
        # message = {"message": "Please check your email for your password reset activation code."}
        # send_mail(email_subject, content_message, 'brybzi@gmail.com',[email], fail_silently=False )
        #html_message=content_message)
        return Response(message, status=status.HTTP_200_OK)


class ComfirmPasswordResetAPIView(RetrieveUpdateAPIView):
    pass
#     permission_classes = (IsAuthenticated,)
#     renderer_classes = (UserJSONRenderer,)
#     serializer_class = ResetPasswordSerializers

#     def retrieve(self, request, *args, **kwargs):
#         token = get_authorization_header(request).decode("utf-8")
#         return Response({"token": token}, status=status.HTTP_200_OK)

#     def update(self, request, *args, **kwargs):
#         user = request.data.get('user', {})
#         serializer = self.serializer_class(request.user, data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"message": "Your password has been reset"}, status=status.HTTP_200_OK)

