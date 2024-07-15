import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';

import '../constants.dart';
import '../models/exercise.dart';
import 'authentication_service.dart';

class ExerciseService {
  final _storage = const FlutterSecureStorage();
  final _logger = Logger();
  final _authService = AuthenticationService();

  Future<List<Exercise>> fetchExercises() async {
    final accessToken = await _storage.read(key: 'accessToken');
    final response = await http.get(
      Uri.parse('$API_URL/exercises/'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );

    if (response.statusCode == 401) {
        await _authService.refreshToken();
        return await fetchExercises();
    } else if (response.statusCode != 200) {
      _logger.e('Failed to fetch exercises');
      throw Exception('Failed to fetch exercises');
    }

    _logger.d('Exercises fetched successfully');
    return (json.decode(response.body) as List)
        .map((e) => Exercise.fromJson(e))
        .toList();
  }
}
