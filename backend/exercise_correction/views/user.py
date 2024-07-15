from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status


class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
