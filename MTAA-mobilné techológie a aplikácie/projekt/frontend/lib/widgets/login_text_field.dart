import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'TextField.dart';


Container logInTextField(String name,TextEditingController ctr,bool obscure) {
  return Container(
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(10),
    ),
    child: textField(
      name: name,
      controller: ctr,
      obscure: obscure,
    ),
  );
}