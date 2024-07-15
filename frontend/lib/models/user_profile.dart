class UserProfile {
  final String? id;
  final DateTime? birthday;
  final int? heightCm;
  final double? weightKg;
  final String? gender;
  final String? avatarUrl;
  final String? username;

  UserProfile({
    this.id,
    this.birthday,
    this.heightCm,
    this.weightKg,
    this.gender,
    this.avatarUrl,
    this.username,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String?,
      birthday: json['birthday'] != null ? DateTime.parse(json['birthday']) : null,
      heightCm: json['height_cm'] as int?,
      weightKg: json['weight_kg'] != null ? double.parse(json['weight_kg'].toString()) : null,
      gender: json['gender'] as String?,
      avatarUrl: json['avatar'] as String?,
      username: json['username'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'birthday': birthday?.toIso8601String(),
      'height_cm': heightCm,
      'weight_kg': weightKg,
      'gender': gender,
      'avatar': avatarUrl,
    };
  }

  UserProfile copyWith({DateTime? birthday, int? heightCm, double? weightKg, String? gender}) {
    return UserProfile(
      birthday: birthday ?? this.birthday,
      heightCm: heightCm ?? this.heightCm,
      weightKg: weightKg ?? this.weightKg,
      gender: gender ?? this.gender
    );
  }
}
