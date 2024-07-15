import 'package:flutter/material.dart';
import 'package:frontend/exceptions.dart';
import 'package:frontend/services/exercise_service.dart';
import 'package:logger/logger.dart';

import '../models/exercise.dart';

class ExercisesPage extends StatefulWidget {
  const ExercisesPage({super.key});

  @override
  _ExercisesPageState createState() => _ExercisesPageState();
}

class _ExercisesPageState extends State<ExercisesPage> {
  final int _selectedIndex = 0;
  final Logger _logger = Logger();

  late List<Exercise> _exercises = [];
  bool _isLoading = true;
  String? _error;

  late final ExerciseService _exerciseService = ExerciseService();

  @override
  void initState() {
    super.initState();
    _fetchExercises();
  }

  void _fetchExercises() async {
    try {
      _logger.d('Fetching exercises...');
      List<Exercise> exercises = await _exerciseService.fetchExercises();
      setState(() {
        _exercises = exercises;
        _isLoading = false;
      });
    } on AuthenticationException {
      Navigator.of(context).pushReplacementNamed('/login');
    } catch (e) {
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  void _onItemTapped(int index) {
    if (index == 1) {
      Navigator.of(context).pushReplacementNamed('/profile');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Exercises",
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
        automaticallyImplyLeading: false,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(child: Text('Error: $_error'))
          : ListView.builder(
        itemCount: _exercises.length,
        itemBuilder: (context, index) {
          Exercise exercise = _exercises[index];
          return GestureDetector(
            onTap: () {
              Navigator.pushNamed(
                context,
                '/exercise/details',
                arguments: exercise,
              );
            },
            child: Card(
              margin: const EdgeInsets.all(8),
              color: Colors.red,
              child: Container(
                height: 100,
                padding: const EdgeInsets.all(8),
                child: Row(
                  children: <Widget>[
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        image: DecorationImage(
                          image: exercise.imageUrl.isNotEmpty
                              ? NetworkImage(exercise.imageUrl)
                              : const AssetImage('assets/images/exercise.jpg') as ImageProvider,
                          fit: BoxFit.cover,
                          onError: (exception, stackTrace) {
                            _logger.e('Failed to load image: $exception');
                          },
                        ),
                      ),
                      child: exercise.imageUrl.isEmpty
                          ? const Icon(Icons.error, color: Colors.red)
                          : null,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(
                        exercise.name,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 24),
                      ),
                    ),
                    const Icon(
                      Icons.keyboard_arrow_right,
                      size: 50,
                      color: Colors.white,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.fitness_center),
            label: 'Exercises',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_circle),
            label: 'Account',
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.red,
        unselectedItemColor: Theme.of(context).primaryColor,
        backgroundColor: Colors.white,
        onTap: _onItemTapped,
      ),
    );
  }
}
