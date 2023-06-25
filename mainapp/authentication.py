from rest_framework import authentication, exceptions
from firebase_admin import credentials, auth
import firebase_admin
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta

firebase_creds = credentials.Certificate(settings.FIREBASE_CONFIG)
default_app = firebase_admin.initialize_app(firebase_creds)

# https://www.oscaralsing.com/firebase-authentication-in-django/


class FirebaseAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            raise exceptions.AuthenticationFailed(
                "In Authentication: No auth token provided")
        id_token = auth_header.split(" ").pop()
        decoded_token = None

        try:
            id_token = auth_header.split(" ").pop()
            decoded_token = auth.verify_id_token(id_token, check_revoked=True)

            uid = decoded_token.get("uid")
            return (uid, id_token)
        except auth.RevokedIdTokenError:
            # Token revoked, inform the user to reauthenticate or signOut().
            print("Token Revoked")
            pass
        except auth.ExpiredIdTokenError:
            print("Expired ID Token")
            raise exceptions.PermissionDenied("Expired ID Token")

        except auth.UserDisabledError:
            # Token belongs to a disabled user record.
            pass
        except auth.InvalidIdTokenError:
            print("Invalid Token")
            pass
        except:
            raise exceptions.AuthenticationFailed(
                "In Authentication: Invalid authentication token")


class IsAuthenticatedWithFirebase(IsAuthenticated):
    def has_permission(self, request, view):
        # return FirebaseAuthentication().authenticate(request) is not None
        user, token = FirebaseAuthentication().authenticate(request)
        if not user:
            return False
        # Use the refreshed token instead of retrieving it from the request headers
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {token}"
        return True
