import 'package:frontend/models/repetition.dart';

class Video {
  final int id;
  final String video;
  final String exerciseType;
  final DateTime createdAt;
  final List<Repetition> repetitions;

  Video({
    required this.id,
    required this.video,
    required this.exerciseType,
    required this.createdAt,
    required this.repetitions,
  });

  factory Video.fromJson(Map<String, dynamic> json) {
    var repetitionsList = json['repetitions'] as List;
    List<Repetition> repetitions = repetitionsList.map((i) => Repetition.fromJson(i)).toList();

    return Video(
      id: json['id'],
      video: json['video'],
      exerciseType: json['exercise_type'],
      createdAt: DateTime.parse(json['created_at']),
      repetitions: repetitions,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'video': video,
      'exercise_type': exerciseType,
      'created_at': createdAt.toIso8601String(),
      'repetitions': repetitions.map((r) => r.toJson()).toList(),
    };
  }
}
