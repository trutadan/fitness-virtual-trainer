import 'package:flutter/material.dart';
import 'package:frontend/screens/exercise_details_page.dart';
import 'package:frontend/screens/exercises_page.dart';
import 'package:frontend/screens/profile_update_page.dart';
import 'package:frontend/screens/register_page.dart';
import 'package:frontend/screens/videos_history_page.dart';

import 'screens/login_page.dart';
import 'screens/profile_page.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'iTrainer',
      theme: ThemeData(
        // define the default brightness and colors
        brightness: Brightness.dark,
        primaryColor: Colors.black,
        hintColor: Colors.red,

        // define the default font family
        fontFamily: 'Montserrat',

        // define the default TextTheme
        textTheme: const TextTheme(
          headline1: TextStyle(fontSize: 72.0, fontWeight: FontWeight.bold),
          headline6: TextStyle(fontSize: 36.0, fontStyle: FontStyle.italic),
          bodyText2: TextStyle(fontSize: 14.0, fontFamily: 'Hind'),
        ),
      ),
      home: const ExercisesPage(),
      // define the routes
      routes: {
        '/exercises': (context) => const ExercisesPage(),
        '/exercise/details': (context) => const ExerciseDetailsPage(),
        '/login': (context) => LoginPage(),
        '/register': (context) => RegistrationPage(),
        '/profile': (context) => const ProfilePage(),
        '/profile/update': (context) => const ProfileUpdatePage(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/videos') {
          final args = settings.arguments as Map<String, String>;
          return MaterialPageRoute(
            builder: (context) {
              return VideosHistoryPage(exerciseType: args['exerciseType']!);
            },
          );
        }
        return null;
      },
    );
  }
}
