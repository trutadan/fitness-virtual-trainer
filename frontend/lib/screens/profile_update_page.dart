import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';

import '../models/user_profile.dart';
import '../services/user_profile_service.dart';

class ProfileUpdatePage extends StatefulWidget {
  const ProfileUpdatePage({super.key});

  @override
  _ProfileUpdatePageState createState() => _ProfileUpdatePageState();
}

class _ProfileUpdatePageState extends State<ProfileUpdatePage> {
  final _formKey = GlobalKey<FormState>();
  late UserProfile _userProfile;

  late TextEditingController _birthdayController;
  late TextEditingController _heightController;
  late TextEditingController _weightController;
  String? _selectedGender;
  XFile? _avatarImage;

  final picker = ImagePicker();

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final UserProfile userProfile = ModalRoute.of(context)!.settings.arguments as UserProfile;
    _userProfile = userProfile;
    _birthdayController = TextEditingController(text: _userProfile.birthday != null ?
                            DateFormat('yyyy-MM-dd').format(_userProfile.birthday!) : '');
    _heightController = TextEditingController(text: _userProfile.heightCm?.toString() ?? '');
    _weightController = TextEditingController(text: _userProfile.weightKg?.toString() ?? '');
    _selectedGender = _userProfile.gender;
  }

  Future<void> _pickImage() async {
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _avatarImage = pickedFile;
      });
    }
  }

  Future<void> _selectBirthday(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _userProfile.birthday ?? DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() {
        _birthdayController.text = DateFormat('yyyy-MM-dd').format(picked);
      });
    }
  }

  void _updateProfile() async {
    if (_formKey.currentState!.validate()) {
      String formattedBirthday = _birthdayController.text.isNotEmpty
          ? DateFormat('yyyy-MM-dd').format(DateFormat('yyyy-MM-dd').parse(_birthdayController.text))
          : '';

      Map<String, dynamic> profileData = {
        "birthday": formattedBirthday,
        "height_cm": _heightController.text,
        "weight_kg": _weightController.text,
        "gender": _selectedGender ?? '',
      };

      try {
        await UserProfileService().updateUserProfile(profileData, avatar: _avatarImage);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Profile updated successfully')));
        Navigator.of(context).pushReplacementNamed('/profile');
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to update profile')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Column(
              children: <Widget>[
                GestureDetector(
                  onTap: _pickImage,
                  child: CircleAvatar(
                    radius: 55,
                    backgroundColor: Colors.grey.shade300,
                    backgroundImage: _avatarImage != null ?
                                      FileImage(File(_avatarImage!.path)) :
                                        _userProfile.avatarUrl != null ?
                                          NetworkImage(_userProfile.avatarUrl!) :
                                            const AssetImage('assets/images/avatar.png') as ImageProvider,
                  ),
                ),
                TextFormField(
                  controller: _birthdayController,
                  readOnly: true,
                  onTap: () => _selectBirthday(context),
                  decoration: const InputDecoration(labelText: 'Birthday'),
                ),
                TextFormField(
                  controller: _heightController,
                  decoration: const InputDecoration(labelText: 'Height in cm'),
                  keyboardType: TextInputType.number,
                ),
                TextFormField(
                  controller: _weightController,
                  decoration: const InputDecoration(labelText: 'Weight in kg'),
                  keyboardType: TextInputType.number,
                ),
                DropdownButtonFormField<String>(
                  value: _selectedGender,
                  onChanged: (newValue) {
                    setState(() {
                      _selectedGender = newValue;
                    });
                  },
                  items: <String>['Male', 'Female', 'Other']
                      .map<DropdownMenuItem<String>>((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                  decoration: const InputDecoration(labelText: 'Gender'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  child: ElevatedButton(
                    onPressed: _updateProfile,
                    child: const Text('Update'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}