import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../exceptions.dart';
import '../models/user_profile.dart';
import '../services/user_profile_service.dart';
import '../services/authentication_service.dart';
import '../services/user_service.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  _ProfilePageState createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final int _selectedIndex = 1;

  UserProfile? userProfile;
  final UserProfileService _userProfileService = UserProfileService();
  final AuthenticationService _authService = AuthenticationService();
  final UserService _userService = UserService();

  @override
  void initState() {
    super.initState();
    _fetchUserProfile();
  }

  void _fetchUserProfile() async {
    try {
      UserProfile profile = await _userProfileService.fetchUserProfile();
      setState(() {
        userProfile = profile;
      });
    } on AuthenticationException {
      Navigator.of(context).pushReplacementNamed('/login');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  void _logout() async {
    try {
      await _authService.logout();
      Navigator.of(context).pushReplacementNamed('/login');
    } on AuthenticationException {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  void _updateProfile() {
    Navigator.of(context).pushNamed('/profile/update', arguments: userProfile);
  }

  void _showDeleteAccountDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text("Delete your account"),
          content: const Text("Are you sure you want to delete your account? This action cannot be undone."),
          actions: <Widget>[
            TextButton(
              child: const Text("Cancel"),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: const Text("Delete", style: TextStyle(color: Colors.red)),
              onPressed: () {
                _deleteAccount();
              },
            ),
          ],
        );
      },
    );
  }

  void _deleteAccount() async {
    try {
      await _userService.deleteUser();
      Navigator.of(context).pushReplacementNamed('/login');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Account deleted successfully")),
      );
    } on AuthenticationException {
      Navigator.of(context).pushReplacementNamed('/login');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  void _onItemTapped(int index) {
    if (index == 0) {
      Navigator.of(context).pushReplacementNamed('/exercises');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Account"),
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: userProfile == null
          ? const Center(child: CircularProgressIndicator())
          : Center(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Padding(
                padding: const EdgeInsets.only(bottom: 10.0),
                child: userProfile?.avatarUrl != null
                    ? CircleAvatar(
                  backgroundImage: NetworkImage(userProfile!.avatarUrl!),
                  radius: 75,
                )
                    : const CircleAvatar(
                  backgroundImage: AssetImage('assets/images/avatar.png'),
                  radius: 75,
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 10.0),
                child: Text(
                  userProfile?.username ?? '-',
                  style: Theme.of(context).textTheme.headlineLarge,
                ),
              ),
              ListTile(
                leading: const Icon(Icons.cake),
                title: const Text("Birthday"),
                subtitle: Text(userProfile!.birthday != null
                    ? DateFormat('yyyy-MM-dd').format(userProfile!.birthday!)
                    : '-'),
              ),
              ListTile(
                leading: const Icon(Icons.height),
                title: const Text("Height in cm"),
                subtitle: Text(userProfile!.heightCm != null
                    ? userProfile!.heightCm.toString()
                    : '-'),
              ),
              ListTile(
                leading: const Icon(Icons.monitor_weight),
                title: const Text("Weight in kg"),
                subtitle: Text(userProfile!.weightKg != null
                    ? userProfile!.weightKg.toString()
                    : '-'),
              ),
              ListTile(
                leading: const Icon(Icons.transgender),
                title: const Text("Gender"),
                subtitle: Text(userProfile!.gender ?? '-'),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: 32.0, vertical: 16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    ElevatedButton(
                      onPressed: _updateProfile,
                      child: const Text('Update profile'),
                    ),
                    ElevatedButton(
                      onPressed: _showDeleteAccountDialog,
                      style: ElevatedButton.styleFrom(
                        primary: Colors.red,
                      ),
                      child: const Text('Delete account'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
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
