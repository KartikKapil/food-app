from main.serializers import UserSerializer
from main.models import Student


def jwt_response_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data,
        'name': Student.objects.get(user=user).name
    }
