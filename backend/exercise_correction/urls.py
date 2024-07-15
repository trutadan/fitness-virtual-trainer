from django.urls import path

from .views.authentication import RegisterView
from .views.user import DeleteUserView
from .views.user_profile import UserProfileView
from .views.exercise import ExercisesListView
from .views.video import VideoSubmitView, UserVideosListView, VideoDeleteView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/delete/', DeleteUserView.as_view(), name='delete_account'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('exercises/', ExercisesListView.as_view(), name='exercises_list'),
    path('videos/', UserVideosListView.as_view(), name='user_videos'),
    path('videos/submit/', VideoSubmitView.as_view(), name='video_submit'),
    path('videos/<int:pk>/', VideoDeleteView.as_view(), name='delete_video'),
]
