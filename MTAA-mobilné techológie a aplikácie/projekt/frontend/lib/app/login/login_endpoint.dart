import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:crypto/crypto.dart';

class User {
  int userId;
  String token;
  String username;
  String password;
  bool done = false;
  String message;

  User({
    this.password = "",
    this.username = "",
    this.userId = 0,
    this.token = "",
    this.message = "",
  });

  factory User.fromJson(Map<String, dynamic> json){
    return User(
      userId: json['user_id'],
      token: json['token'],
    );
  }

  Map<String,dynamic> toJson(){
    Map<String,dynamic> map = {
      'token' : token.trim() ,
      'userId' : userId ,
    };
    return map;
  }

  factory User.fromJsonMessage(Map<String, dynamic> json){
    return User(
      message: json['message'],
    );
  }


}

Future<User> postLogin(String username,String password) async {
  var bytes = utf8.encode(password); // data being hashed
  var passwd = sha256.convert(bytes);
  final response = await http.post(Uri.parse('http://147.175.162.226:5000/login'),
      body: {
        "name": username,
        "password": passwd.toString(),
      });

  if (response.statusCode == 200) {

    return User.fromJson(jsonDecode(response.body));
  } else {
    return User.fromJsonMessage(jsonDecode(response.body));
  }
}

Future<User> postRegister(String username,String password) async {
  var bytes = utf8.encode(password); // data being hashed
  var passwd = sha256.convert(bytes);
  final response = await http.post(Uri.parse('http://147.175.162.226:5000/register'), // 10.10.38.85:5000
      body: {
        "name": username,
        "password": passwd.toString(),
        "ip_address": "192.168.0.1"
      });

  return User.fromJsonMessage(jsonDecode(response.body));
}
Future<User> deleteUser(User user) async {

  final response = await http.delete(Uri.parse('http://147.175.162.226:5000/delete/user/${user.userId}'),
      headers: {
        "token": user.token,
      });

  return User.fromJsonMessage(jsonDecode(response.body));
}
