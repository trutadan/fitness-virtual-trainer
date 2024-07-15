import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'dart:async';

import '../models/video.dart';

class SubmissionOverlay extends StatefulWidget {
  final bool isLoading;
  final Video? submittedVideo;
  final Map<int, VideoPlayerController> videoControllers;
  final Map<int, bool> videoPlaying;
  final Map<int, bool> showRepetitions;
  final Map<int, Map<int, bool>> showAdvice;

  const SubmissionOverlay({
    Key? key,
    required this.isLoading,
    required this.submittedVideo,
    required this.videoControllers,
    required this.videoPlaying,
    required this.showRepetitions,
    required this.showAdvice,
  }) : super(key: key);

  @override
  _SubmissionOverlayState createState() => _SubmissionOverlayState();
}

class _SubmissionOverlayState extends State<SubmissionOverlay> {
  @override
  void didUpdateWidget(covariant SubmissionOverlay oldWidget) {
    super.didUpdateWidget(oldWidget);
    // if the submission is done, show the message and redirect after a short delay
    if (!widget.isLoading && widget.submittedVideo != null) {
      Timer(const Duration(seconds: 2), () {
        Navigator.of(context).pushReplacementNamed('/videos', arguments: {'exerciseType': widget.submittedVideo!.exerciseType});
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return widget.isLoading
        ? const Center(child: CircularProgressIndicator())
        : Container(
      color: Colors.black54,
      child: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Processing is done',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            SizedBox(height: 10),
            Text(
              'Redirecting to history page...',
              style: TextStyle(fontSize: 16, color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }
}
