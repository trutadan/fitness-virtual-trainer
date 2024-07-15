import 'package:flutter/material.dart';
import 'package:frontend/screens/register_page.dart';
import '../services/authentication_service.dart';
import 'exercises_page.dart';

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final AuthenticationService _authService = AuthenticationService();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Container(
            height: MediaQuery.of(context).size.height - MediaQuery.of(context).padding.top,
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                ClipOval(
                  child: Image.asset(
                    'assets/images/logo.png',
                    height: 200.0,
                    width: 200.0,
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(height: 20),
                const Text(
                  "Welcome to iTrainer!",
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: _usernameController,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    labelText: 'Username',
                    labelStyle: TextStyle(color: Colors.red),
                    enabledBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: Colors.red),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: Colors.red),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    labelText: 'Password',
                    labelStyle: TextStyle(color: Colors.red),
                    enabledBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: Colors.red),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: Colors.red),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(primary: Colors.red),
                  onPressed: () async {
                    try {
                      await _authService.login(_usernameController.text, _passwordController.text);
                      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (context) => ExercisesPage()));
                    } catch (e) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
                      );
                    }
                  },
                  child: const Text('Login', style: TextStyle(color: Colors.white)),
                ),
                TextButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => RegistrationPage()),
                    );
                  },
                  icon: const Icon(Icons.person_add, color: Colors.red),
                  label: const Text('Register', style: TextStyle(color: Colors.red)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
