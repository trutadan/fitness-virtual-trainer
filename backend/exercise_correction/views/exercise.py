from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


IP_ADDRESS = 'http://localhost:8069'

EXERCISE_DATA = {
    'squat': {
        'name': 'Squat',
        'description': 'A squat is a strength exercise in which the trainee lowers their hips from a standing position and then stands back up.',
        'steps': [
            'Stand with feet a little wider than hip width, toes facing front.',
            'Drive your hips back-bending at the knees and ankles and pressing your knees slightly open-as you sit into a squat position.',
            'Sit into a squat position while still keeping your heels and toes on the ground, chest up and shoulders back.',
            'Strive to eventually reach parallel, meaning knees are bent to a 90-degree angle.',
            'Press into your heels and straighten legs to return to a standing upright position.'
        ],
        'video_url': f'{IP_ADDRESS}/media/video_exercises/squat.mp4',
        'image_url': f'{IP_ADDRESS}/media/image_exercises/squat.png'
    },
    'bicep_curl': {
        'name': 'Bicep Curl',
        'description': 'A bicep curl is an exercise that targets the biceps muscles at the front of the upper arm.',
        'steps': [
            'Stand up straight with a dumbbell in each hand at arm\'s length. Keep your elbows close to your torso and rotate the palms of your hands until they are facing forward.',
            'Now, keeping the upper arms stationary, exhale and curl the weights while contracting your biceps.',
            'Continue to raise the weights until your biceps are fully contracted and the dumbbells are at shoulder level.',
            'Hold the contracted position for a brief pause as you squeeze your biceps.',
            'Inhale and slowly begin to lower the dumbbells back to the starting position.'
        ],
        'video_url': f'{IP_ADDRESS}/media/video_exercises/bicep_curl.mp4',
        'image_url': f'{IP_ADDRESS}/media/image_exercises/bicep_curl.png'
    },
    'pushup': {
        'name': 'Pushup',
        'description': 'A push-up is a common calisthenics exercise beginning from the prone position.',
        'steps': [
            'Begin in a plank position, with your hands placed slightly wider than shoulder-width apart and feet together.',
            'Lower your body until your chest nearly touches the floor, ensuring that your body forms a straight line from your head to your heels.',
            'Pause, then push yourself back up to the starting position as quickly as possible.',
            'Keep your core tight and back flat throughout the movement.'
        ],
        'video_url': f'{IP_ADDRESS}/media/video_exercises/pushup.mp4',
        'image_url': f'{IP_ADDRESS}/media/image_exercises/pushup.png'
    },
}


class ExercisesListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        exercises = [
            {
                "name": data['name'],
                "type": exercise_type,
                "description": data['description'],
                "steps": data['steps'],
                "video_url": data['video_url'],
                "image_url": data['image_url'],
            }
            for exercise_type, data in EXERCISE_DATA.items()
        ]

        return Response(exercises)