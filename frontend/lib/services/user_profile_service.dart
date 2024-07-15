import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';
import 'package:logger/logger.dart';

import '../constants.dart';
import '../models/user_profile.dart';
import 'authentication_service.dart';

class UserProfileService {
  final _storage = const FlutterSecureStorage();
  final _logger = Logger();
  final _authService = AuthenticationService();

  Future<UserProfile> fetchUserProfile() async {
    final accessToken = await _storage.read(key: 'accessToken');
    final response = await http.get(
      Uri.parse('$API_URL/user/profile/'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );

    if (response.statusCode == 401) {
      await _authService.refreshToken();
      return await fetchUserProfile();
    } else if (response.statusCode != 200) {
      _logger.e('Failed to fetch user profile');
      throw Exception('Failed to fetch user profile');
    }

    _logger.d('User profile fetched successfully');
    return UserProfile.fromJson(json.decode(response.body));
  }

  Future<bool> updateUserProfile(Map<String, dynamic> profileData, {XFile? avatar}) async {
    final accessToken = await _storage.read(key: 'accessToken');
    var uri = Uri.parse('$API_URL/user/profile/');
    var request = http.MultipartRequest('PATCH', uri)
      ..headers['Authorization'] = 'Bearer $accessToken';

    profileData.forEach((key, value) {
      if(value != null) request.fields[key] = value.toString();
    });

    if (avatar != null) {
      request.files.add(await http.MultipartFile.fromPath(
        'avatar',
        avatar.path,
        contentType: MediaType('image', 'jpeg'),
      ));
    }

    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      print('Profile updated successfully.');
      return true;
    } else {
      print('Failed to update profile: ${response.reasonPhrase}');
      return false;
    }
  }
}
