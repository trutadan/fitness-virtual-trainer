class Advice {
  final String category;
  final String text;
  final int correctionLevel;

  Advice({required this.category, required this.text, required this.correctionLevel});

  factory Advice.fromJson(Map<String, dynamic> json) {
    return Advice(
      category: json['category'],
      text: json['text'],
      correctionLevel: json['correction_level'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category': category,
      'text': text,
      'correction_level': correctionLevel,
    };
  }
}