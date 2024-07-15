import 'advice.dart';

class Repetition {
  final String repetition;
  final List<Advice> advice;

  Repetition({required this.repetition, required this.advice});

  factory Repetition.fromJson(Map<String, dynamic> json) {
    var adviceList = json['advice'] as List;
    List<Advice> advice = adviceList.map((i) => Advice.fromJson(i)).toList();

    return Repetition(
      repetition: json['repetition'],
      advice: advice,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'repetition': repetition,
      'advice': advice.map((a) => a.toJson()).toList(),
    };
  }
}
