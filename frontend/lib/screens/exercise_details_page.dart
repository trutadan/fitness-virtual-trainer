import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';

import '../constants.dart';
import '../exceptions.dart';
import '../models/exercise.dart';
import '../models/video.dart';
import '../services/video_service.dart';
import '../widgets/submission_overlay.dart';

class ExerciseDetailsPage extends StatefulWidget {
  const ExerciseDetailsPage({Key? key}) : super(key: key);

  @override
  _ExerciseDetailsPageState createState() => _ExerciseDetailsPageState();
}

class _ExerciseDetailsPageState extends State<ExerciseDetailsPage> {
  late VideoPlayerController _controller;
  late Exercise exercise;

  File? videoFile;
  bool isLoading = false;
  final VideoService _videoService = VideoService();
  Video? submittedVideo;
  final Map<int, VideoPlayerController> _videoControllers = {};
  final Map<int, bool> _videoPlaying = {};
  final Map<int, bool> _showRepetitions = {};
  final Map<int, Map<int, bool>> _showAdvice = {};

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    exercise = ModalRoute.of(context)!.settings.arguments as Exercise;

    _controller = VideoPlayerController.network(exercise.videoUrl)
      ..initialize().then((_) {
        setState(() {});
        _controller.setVolume(0.0);
      }).catchError((error) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error loading video: $error')));
      });
  }

  @override
  void dispose() {
    _controller.dispose();
    for (var controller in _videoControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _pickVideo() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.video);
    if (result != null) {
      setState(() {
        videoFile = File(result.files.single.path!);
      });
    }
  }

  Future<void> _submitVideo() async {
    if (videoFile != null) {
      setState(() {
        isLoading = true;
      });
      try {
        Video video = await _videoService.submitVideo(videoFile!, exercise.type);
        setState(() {
          submittedVideo = video;
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Video submitted successfully')));
        await Future.delayed(const Duration(seconds: 2));
        Navigator.of(context).pushReplacementNamed('/videos', arguments: {'exerciseType': exercise.type});
      } on AuthenticationException {
        Navigator.of(context).pushReplacementNamed('/login');
      } catch (e) {
        setState(() {
          isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(exercise.name),
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.pushNamed(
                context,
                '/videos',
                arguments: {'exerciseType': exercise.type},
              );
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(
                    exercise.description,
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ),
                GestureDetector(
                  onTap: () {
                    setState(() {
                      _controller.value.isPlaying ? _controller.pause() : _controller.play();
                    });
                  },
                  child: Card(
                    elevation: 5,
                    margin: const EdgeInsets.all(8),
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        if (_controller.value.isInitialized)
                          AspectRatio(
                            aspectRatio: _controller.value.aspectRatio,
                            child: VideoPlayer(_controller),
                          )
                        else
                          const SizedBox(
                            height: 200,
                            child: Center(child: CircularProgressIndicator()),
                          ),
                        if (!_controller.value.isPlaying)
                          Icon(
                            Icons.play_arrow,
                            size: 50,
                            color: Colors.white.withOpacity(0.7),
                          ),
                      ],
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Steps:',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 10),
                      ...exercise.steps.asMap().entries.map((entry) {
                        int index = entry.key + 1;
                        String step = entry.value;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4.0),
                          child: Text(
                            '$index. $step',
                            style: const TextStyle(fontSize: 14),
                          ),
                        );
                      }),
                    ],
                  ),
                ),
                Card(
                  elevation: 5,
                  margin: const EdgeInsets.all(8),
                  child: ListTile(
                    leading: const Icon(Icons.file_upload),
                    title: const Text("Select your video"),
                    onTap: _pickVideo,
                  ),
                ),
                if (videoFile != null)
                  Card(
                    elevation: 5,
                    margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
                    child: ListTile(
                      leading: const Icon(Icons.cloud_upload),
                      title: const Text("Submit your video"),
                      onTap: _submitVideo,
                    ),
                  ),
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text(
                    ATTENTION_TITLE,
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.red),
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 8.0),
                  child: Text(
                    ATTENTION_MESSAGE,
                    style: TextStyle(fontSize: 16, color: Colors.orange),
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 8.0),
                  child: Text(
                    STRAIGHT_BACK_MESSAGE,
                    style: TextStyle(fontSize: 16, color: Colors.yellow),
                  ),
                ),
              ],
            ),
          ),
          if (isLoading)
            SubmissionOverlay(
              isLoading: isLoading,
              submittedVideo: submittedVideo,
              videoControllers: _videoControllers,
              videoPlaying: _videoPlaying,
              showRepetitions: _showRepetitions,
              showAdvice: _showAdvice,
            ),
        ],
      ),
    );
  }
}
