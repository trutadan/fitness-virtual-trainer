import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';
import 'dart:convert';

import '../constants.dart';
import '../exceptions.dart';

class AuthenticationService {
  final _storage = const FlutterSecureStorage();
  final _logger = Logger();

  Future<void> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$API_URL/token/'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final responseJson = json.decode(response.body);
      await _storage.write(key: 'refreshToken', value: responseJson['refresh']);
      await _storage.write(key: 'accessToken', value: responseJson['access']);
      _logger.d('Login successful...');
    } else {
      String errorMessage = 'An unknown error occurred';
      if (response.statusCode == 400) {
        errorMessage = 'Invalid request';
      } else if (response.statusCode == 401) {
        errorMessage = 'Unauthorized. Check your credentials';
      } else if (response.statusCode >= 500) {
        errorMessage = 'Server error. Please try again later';
      }
      _logger.e(errorMessage);
      throw Exception(errorMessage);
    }
  }

  Future<void> register(String username, String email, String password, String passwordConfirmation) async {
    final response = await http.post(
      Uri.parse('$API_URL/register/'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'username': username,
        'email': email,
        'password': password,
        'password2': passwordConfirmation
      }),
    );

    if (response.statusCode == 201) {
      _logger.d('Registration successful');
    } else {
      String errorMessage = 'An unknown error occurred';
      if (response.statusCode == 400) {
        errorMessage = 'Invalid request. Please fill all fields correctly.';
      } else if (response.statusCode == 409) {
        errorMessage = 'User already exists.';
      } else if (response.statusCode >= 500) {
        errorMessage = 'Server error. Please try again later.';
      }
      _logger.e(errorMessage);
      throw Exception(errorMessage);
    }
  }

  Future<void> refreshToken() async {
    final refreshToken = await _storage.read(key: 'refreshToken');
    await _storage.delete(key: 'refreshToken');

    if (refreshToken == null) {
      _logger.e('No refresh token found');
      throw AuthenticationException('No refresh token found');
    }

    final response = await http.post(
      Uri.parse('$API_URL/token/refresh/'),
      headers: {'Content-Type': 'application/json; charset=UTF-8'},
      body: jsonEncode({'refresh': refreshToken}),
    );

    if (response.statusCode == 200) {
      final responseJson = json.decode(response.body);
      await _storage.write(key: 'accessToken', value: responseJson['access']);
      _logger.d('Token refreshed successfully');
    } else {
      _logger.e('Failed to refresh token');
      throw AuthenticationException('Failed to refresh token');
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'refreshToken');
    await _storage.delete(key: 'accessToken');
    _logger.d('Logout successful');

    throw AuthenticationException("Logout successful");
  }
}
