import 'dart:convert';
import 'dart:async';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http_parser/http_parser.dart';
import 'package:logger/logger.dart';
import 'package:mime/mime.dart';

import '../constants.dart';
import '../models/video.dart';
import 'authentication_service.dart';

class VideoService {
  final _storage = const FlutterSecureStorage();
  final _logger = Logger();
  final _authService = AuthenticationService();

  Future<Video> submitVideo(File videoFile, String exerciseType) async {
    final accessToken = await _storage.read(key: 'accessToken');
    var uri = Uri.parse('$API_URL/videos/submit/');
    var request = http.MultipartRequest('POST', uri)
      ..headers['Authorization'] = 'Bearer $accessToken'
      ..files.add(await http.MultipartFile.fromPath(
        'video',
        videoFile.path,
        contentType: MediaType.parse(lookupMimeType(videoFile.path) ?? 'video/mp4'),
      ))
      ..fields['type'] = exerciseType;

    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 401) {
      await _authService.refreshToken();
      return await submitVideo(videoFile, exerciseType);
    } else if (response.statusCode != 200) {
      _logger.e('Failed to submit video: ${response.body}');
      throw Exception(jsonDecode(response.body)['error']);
    }

    return Video.fromJson(jsonDecode(response.body));
  }

  Future<List<Video>> fetchUserVideos({String? exerciseType}) async {
    final accessToken = await _storage.read(key: 'accessToken');
    final queryParameters = exerciseType != null ? '?type=$exerciseType' : '';
    final response = await http.get(
      Uri.parse('$API_URL/videos/$queryParameters'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 401) {
      await _authService.refreshToken();
      return await fetchUserVideos();
    } else if (response.statusCode != 200) {
      _logger.e('Failed to fetch user videos');
      throw Exception('Failed to fetch user videos');
    }

    _logger.d('Fetched user videos successfully');
    return (json.decode(response.body) as List)
        .map((i) => Video.fromJson(i))
        .toList();
  }

  Future<void> deleteVideo(int videoId) async {
    final accessToken = await _storage.read(key: 'accessToken');
    final response = await http.delete(
      Uri.parse('$API_URL/videos/$videoId/'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 401) {
      await _authService.refreshToken();
      return await deleteVideo(videoId);
    } else if (response.statusCode != 204) {
      _logger.e('Failed to delete video');
      throw Exception('Failed to delete video');
    }

    _logger.d('Video deleted successfully');
  }
}
