class Exercise {
  final String name;
  final String type;
  final String description;
  final List<String> steps;
  final String videoUrl;
  final String imageUrl;

  Exercise({
    required this.name,
    required this.type,
    required this.description,
    required this.steps,
    required this.videoUrl,
    required this.imageUrl,
  });

  factory Exercise.fromJson(Map<String, dynamic> json) {
    return Exercise(
      name: json['name'],
      type: json['type'],
      description: json['description'],
      steps: List<String>.from(json['steps']),
      videoUrl: json['video_url'],
      imageUrl: json['image_url'],
    );
  }
}
