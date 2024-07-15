import 'package:flutter/material.dart';
import 'package:frontend/exceptions.dart';
import 'package:intl/intl.dart';
import 'package:video_player/video_player.dart';

import '../models/video.dart';
import '../services/video_service.dart';

class VideosHistoryPage extends StatefulWidget {
  final String exerciseType;

  const VideosHistoryPage({Key? key, required this.exerciseType}) : super(key: key);

  @override
  _VideosHistoryPageState createState() => _VideosHistoryPageState();
}

class _VideosHistoryPageState extends State<VideosHistoryPage> {
  late VideoService videoService = VideoService();
  late Future<List<Video>> videosFuture;
  final Map<String, bool> _showRepetitions = {};
  final Map<String, Map<int, bool>> _showAdvice = {};
  final Map<String, VideoPlayerController> _videoControllers = {};
  final Map<String, bool> _videoPlaying = {};

  @override
  void initState() {
    super.initState();

    try {
      videosFuture = videoService.fetchUserVideos(exerciseType: widget.exerciseType);
    } on AuthenticationException {
      Navigator.of(context).pushReplacementNamed('/login');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  @override
  void dispose() {
    for (var controller in _videoControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _deleteVideo(int videoId) async {
    final bool confirm = await showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text("Delete the video"),
          content: const Text("Are you sure you want to delete this video?"),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text("Delete"),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text("Cancel"),
            ),
          ],
        );
      },
    ) ?? false;

    if (confirm) {
      try {
        await videoService.deleteVideo(videoId);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Video deleted successfully!')));
        setState(() {
          videosFuture = videoService.fetchUserVideos(exerciseType: widget.exerciseType);
        });
      } on AuthenticationException {
        Navigator.of(context).pushReplacementNamed('/login');
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
        );
      }
    }
  }

  void _initializeVideo(String key, String url) {
    final controller = VideoPlayerController.network(url);
    _videoControllers[key] = controller;
    _videoPlaying[key] = false;
    controller.addListener(() {
      if (mounted) {
        setState(() {});
      }
    });
    controller.initialize().then((_) {
      if (mounted) {
        setState(() {});
        controller.setVolume(0.0);
      }
    });
  }

  String formatCategory(String category) {
    return category.split('_').map((word) => word[0].toUpperCase() + word.substring(1)).join(' ');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Videos history'),
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
      ),
      body: FutureBuilder<List<Video>>(
        future: videosFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (snapshot.data == null || snapshot.data!.isEmpty) {
            return const Center(child: Text('No videos found'));
          } else {
            return ListView.builder(
              itemCount: snapshot.data!.length,
              itemBuilder: (context, index) {
                Video video = snapshot.data![index];
                String formattedDate = DateFormat('yyyy-MM-dd HH:mm:ss').format(video.createdAt);
                String videoUrl = video.video;
                String mainVideoKey = 'main_$index';

                if (!_videoControllers.containsKey(mainVideoKey)) {
                  _initializeVideo(mainVideoKey, videoUrl);
                }

                return Card(
                  margin: const EdgeInsets.all(8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Text(formattedDate, style: const TextStyle(fontSize: 18)),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: _videoControllers[mainVideoKey]!.value.isInitialized
                            ? AspectRatio(
                          aspectRatio: _videoControllers[mainVideoKey]!.value.aspectRatio,
                          child: Stack(
                            alignment: Alignment.bottomCenter,
                            children: [
                              VideoPlayer(_videoControllers[mainVideoKey]!),
                              VideoProgressIndicator(_videoControllers[mainVideoKey]!, allowScrubbing: true),
                              Center(
                                child: IconButton(
                                  icon: Icon(
                                    _videoPlaying[mainVideoKey]! ? Icons.pause : Icons.play_arrow,
                                    color: Colors.white,
                                    size: 50,
                                  ),
                                  onPressed: () {
                                    setState(() {
                                      if (_videoPlaying[mainVideoKey]!) {
                                        _videoControllers[mainVideoKey]!.pause();
                                      } else {
                                        _videoControllers[mainVideoKey]!.play();
                                      }
                                      _videoPlaying[mainVideoKey] = !_videoPlaying[mainVideoKey]!;
                                    });
                                  },
                                ),
                              ),
                            ],
                          ),
                        )
                            : const Center(child: CircularProgressIndicator()),
                      ),
                      Center(
                        child: TextButton(
                          onPressed: () {
                            setState(() {
                              _showRepetitions[mainVideoKey] = !(_showRepetitions[mainVideoKey] ?? false);
                            });
                          },
                          child: Column(
                            children: [
                              Text(
                                _showRepetitions[mainVideoKey] ?? false ? 'Hide repetitions' : 'Show repetitions',
                                style: const TextStyle(color: Colors.grey),
                              ),
                              Icon(
                                _showRepetitions[mainVideoKey] ?? false ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                                color: Colors.grey,
                              ),
                            ],
                          ),
                        ),
                      ),
                      if (_showRepetitions[mainVideoKey] ?? false)
                        ...video.repetitions.asMap().entries.map((entry) {
                          int repIndex = entry.key;
                          var repetition = entry.value;
                          String repetitionUrl = repetition.repetition;
                          String repetitionKey = 'repetition_${index}_$repIndex';

                          if (!_videoControllers.containsKey(repetitionKey)) {
                            _initializeVideo(repetitionKey, repetitionUrl);
                          }

                          return ClipRRect(
                            borderRadius: BorderRadius.circular(33.0),
                            child: Container(
                              color: Colors.black,
                              margin: const EdgeInsets.symmetric(vertical: 4.0),
                              child: Padding(
                                padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    _videoControllers[repetitionKey]!.value.isInitialized
                                        ? AspectRatio(
                                      aspectRatio: _videoControllers[repetitionKey]!.value.aspectRatio,
                                      child: Stack(
                                        alignment: Alignment.bottomCenter,
                                        children: [
                                          VideoPlayer(_videoControllers[repetitionKey]!),
                                          VideoProgressIndicator(_videoControllers[repetitionKey]!, allowScrubbing: true),
                                          Center(
                                            child: IconButton(
                                              icon: Icon(
                                                _videoPlaying[repetitionKey]! ? Icons.pause : Icons.play_arrow,
                                                color: Colors.white,
                                                size: 50,
                                              ),
                                              onPressed: () {
                                                setState(() {
                                                  if (_videoPlaying[repetitionKey]!) {
                                                    _videoControllers[repetitionKey]!.pause();
                                                  } else {
                                                    _videoControllers[repetitionKey]!.play();
                                                  }
                                                  _videoPlaying[repetitionKey] = !_videoPlaying[repetitionKey]!;
                                                });
                                              },
                                            ),
                                          ),
                                        ],
                                      ),
                                    )
                                        : const Center(child: CircularProgressIndicator()),
                                    Center(
                                      child: TextButton(
                                        onPressed: () {
                                          setState(() {
                                            _showAdvice[mainVideoKey] ??= {};
                                            _showAdvice[mainVideoKey]![repIndex] = !(_showAdvice[mainVideoKey]![repIndex] ?? false);
                                          });
                                        },
                                        child: Column(
                                          children: [
                                            Text(
                                              _showAdvice[mainVideoKey]?[repIndex] ?? false ? 'Hide advice' : 'Show advice',
                                              style: const TextStyle(color: Colors.grey),
                                            ),
                                            Icon(
                                              _showAdvice[mainVideoKey]?[repIndex] ?? false ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                                              color: Colors.grey,
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                    if (_showAdvice[mainVideoKey]?[repIndex] ?? false)
                                      ...repetition.advice.map((advice) => Padding(
                                        padding: const EdgeInsets.only(left: 16.0, bottom: 10.0),
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              formatCategory(advice.category),
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 16,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            Text(
                                              advice.text,
                                              style: TextStyle(
                                                color: advice.correctionLevel == 1
                                                    ? Colors.green
                                                    : advice.correctionLevel == 2
                                                    ? Colors.yellow
                                                    : Colors.red,
                                              ),
                                            ),
                                          ],
                                        ),
                                      )),
                                  ],
                                ),
                              ),
                            ),
                          );
                        }).toList(),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            onPressed: () => _deleteVideo(video.id),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            );
          }
        },
      ),
    );
  }
}
