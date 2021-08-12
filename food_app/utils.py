from main.models import Student, Vendor
from main.serializers import UserSerializer


def jwt_response_handler(token, user=None, request=None):
    isVendor = False
    try:
        stud = Student.objects.get(user=user)
        name = stud.name
    except:
        name = Vendor.objects.get(user=user).name
        isVendor = True

    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data,
        'name': name,
        'isVendor': isVendor
    }
