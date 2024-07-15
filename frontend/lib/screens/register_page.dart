import 'package:flutter/material.dart';

import '../services/authentication_service.dart';

import 'login_page.dart';

class RegistrationPage extends StatefulWidget {
  @override
  _RegistrationPageState createState() => _RegistrationPageState();
}

class _RegistrationPageState extends State<RegistrationPage> {
  final AuthenticationService _authService = AuthenticationService();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Container(
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
                const SizedBox(height: 30),
                TextField(
                  controller: _usernameController,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    labelText: 'Username',
                    labelStyle: TextStyle(color: Colors.red),
                    enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
                    focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _emailController,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    labelStyle: TextStyle(color: Colors.red),
                    enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
                    focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
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
                    enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
                    focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _confirmPasswordController,
                  obscureText: true,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    labelText: 'Confirm password',
                    labelStyle: TextStyle(color: Colors.red),
                    enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
                    focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.red)),
                  ),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(primary: Colors.red),
                  onPressed: () async {
                    if (_passwordController.text == _confirmPasswordController.text) {
                      try {
                        await _authService.register(
                          _usernameController.text,
                          _emailController.text,
                          _passwordController.text,
                          _confirmPasswordController.text,
                        );
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(builder: (context) => LoginPage()),
                        );
                      } catch (e) {
                        ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(e.toString().replaceFirst('Exception: ', '')))
                        );
                      }
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text("Passwords do not match"))
                      );
                    }
                  },
                  child: const Text('Register', style: TextStyle(color: Colors.white)),
                ),
                TextButton.icon(
                  onPressed: () {
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(builder: (context) => LoginPage()),
                    );
                  },
                  icon: const Icon(Icons.login, color: Colors.red),
                  label: const Text('Already have an account? Login', style: TextStyle(color: Colors.red)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
