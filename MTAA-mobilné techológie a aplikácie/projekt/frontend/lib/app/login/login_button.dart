

import 'package:flutter/cupertino.dart';
import 'package:mtaa_frontend/widgets/Button.dart';

class LogInButton extends Button {
  LogInButton({
    required String text,
    Color? color,
    Color? textColor,
    required VoidCallback onPressed,
    double elevation = 0,

}) : super(
    color: color,
    onPressed: onPressed,
    borderRadius: 20,
    elevation: elevation,
    child: Text(
      text,
      style: TextStyle(color: textColor,fontSize: 17.0),
    ),
  );
}
