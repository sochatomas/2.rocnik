import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class todayEventsPage extends StatelessWidget {
  const todayEventsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
      title: Text(
        'úspešne si sa prihlásil',
        textAlign: TextAlign.center,
        style: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w500,
        ),
      ),
    ),
    );
  }
}
