import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';

import '../constants.dart';
import 'authentication_service.dart';

class UserService {
  final _storage = const FlutterSecureStorage();
  final _logger = Logger();
  final _authService = AuthenticationService();

  Future<void> deleteUser() async {
    final accessToken = await _storage.read(key: 'accessToken');
    final response = await http.delete(
      Uri.parse('$API_URL/user/delete/'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );

    if (response.statusCode == 401) {
      await _authService.refreshToken();
      await deleteUser();
    } else if (response.statusCode != 204) {
      _logger.e('Failed to delete user');
      throw Exception('Failed to delete user');
    }

    _logger.d('User deleted successfully');
    await _storage.delete(key: 'accessToken');
    await _storage.delete(key: 'refreshToken');
  }
}