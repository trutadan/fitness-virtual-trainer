import os
import re
import uuid

from django.db import transaction

from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status

from ..models.advice import Advice
from ..models.repetition import Repetition
from ..models.video import Video
from ..serializers.video import VideoSerializer
from ..services.exception.custom_exceptions import LandmarkExtractionError, AngleComputationError
from ..services.pose_correction.BicepCurlPoseCorrection import BicepCurlPoseCorrection
from ..services.pose_correction.PushupPoseCorrection import PushUpPoseCorrection
from ..services.pose_correction.SquatPoseCorrection import SquatPoseCorrection


class VideoSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        video_file = request.FILES.get('video')
        if not video_file:
            return Response({"error": "No video file provided"}, status=status.HTTP_400_BAD_REQUEST)

        exercise_type = request.data.get('type')
        if not exercise_type:
            return Response({"error": "No exercise type provided"}, status=status.HTTP_400_BAD_REQUEST)

        # generate a unique file name
        unique_filename = self.get_unique_filename(video_file.name)

        # submitted video path
        input_directory = "media/submitted_videos/"
        input_video_path = os.path.join(input_directory, unique_filename)

        try:
            with transaction.atomic():
                # save the original video within the atomic block
                original_video_instance = Video(user=request.user, video=unique_filename, exercise_type=exercise_type)
                original_video_instance.save()
                original_video_instance.video.save(unique_filename, video_file)

                processed_video_output_dictionary = self.process_video(input_video_path, exercise_type)

                if not processed_video_output_dictionary:
                    raise Exception("Processing failed")

                repetitions = []
                # iterate over each processed video and their respective advice
                for video_path, advices in processed_video_output_dictionary.items():
                    # ensure the video path is correct
                    video_path = re.sub(r'./media/', '', video_path)
                    repetition_instance = Repetition(video=original_video_instance, repetition=video_path)
                    repetition_instance.save()

                    # save each piece of advice
                    for category, details in advices.items():
                        text, correction_level = details
                        Advice.objects.create(
                            repetition=repetition_instance,
                            category=category,
                            text=text,
                            correction_level=correction_level
                        )

                    repetitions.append(repetition_instance)

                return Response(VideoSerializer(original_video_instance).data, status=status.HTTP_200_OK)
        except (LandmarkExtractionError, AngleComputationError) as e:
            self.cleanup_file(input_video_path)
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.cleanup_file(input_video_path)
            print(e)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_unique_filename(original_filename):
        """
        Generate a unique file name by appending a UUID to the original file name.
        """
        base, ext = os.path.splitext(original_filename)
        unique_filename = f"{base}_{uuid.uuid4().hex}{ext}"
        return unique_filename

    @staticmethod
    def process_video(video_file, exercise_type):
        """
        Process the video file and return a dictionary with processed video paths and their respective advice.
        """
        if exercise_type == 'squat':
            pose_correction = SquatPoseCorrection()
        elif exercise_type == 'bicep_curl':
            pose_correction = BicepCurlPoseCorrection()
        elif exercise_type == 'pushup':
            pose_correction = PushUpPoseCorrection()
        else:
            return None

        try:
            return pose_correction.process_video(video_file)
        except (LandmarkExtractionError, AngleComputationError) as e:
            raise e
        except Exception as e:
            raise Exception("An unexpected error occurred while processing the video")

    @staticmethod
    def cleanup_file(file_path):
        """
        Delete the file at the given file path.
        """
        if os.path.exists(file_path):
            os.remove(file_path)


class UserVideosListView(ListAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        exercise_type = self.request.query_params.get('type')
        if exercise_type:
            return Video.objects.filter(
                user=self.request.user,
                exercise_type=exercise_type
            ).prefetch_related('repetitions__advice').order_by('-created_at')
        return Video.objects.filter(
            user=self.request.user
        ).prefetch_related('repetitions__advice').order_by('-created_at')


class VideoDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # only allow deleting videos that belong to the requesting user
        return Video.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        video_id = kwargs.get('pk', None)
        if not video_id:
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        video = Video.objects.filter(pk=video_id, user=request.user).first()
        if video:
            self.perform_destroy(video)
            return Response({"message": "Video deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Video not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        instance.delete()
