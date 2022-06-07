
import 'package:flutter/material.dart';

class Button extends StatelessWidget {

  final Widget child;
  final Color? color;
  final double borderRadius;
  final VoidCallback onPressed;
  final double height;
  final double elevation;

  Button({
    required this.child,
    required this.color,
    this.borderRadius = 10,
    required this.onPressed,
    this.height = 50,
    this.elevation = 0,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      child: ElevatedButton(
        child: child,
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          elevation: elevation,
          primary: color,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(
              Radius.circular(borderRadius),
            ),
          ),
        ),
      ),
    );
  }
}
