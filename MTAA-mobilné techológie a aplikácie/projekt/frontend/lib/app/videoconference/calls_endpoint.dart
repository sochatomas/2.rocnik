import 'dart:convert';

import 'package:http/http.dart' as http;

import '../login/login_endpoint.dart';

class Call{
  int id;
  int callerId;
  int receriverId;
  int callLength;
  String time;
  String message;

  Call({
    this.id = 0,
    this.callerId = 0,
    this.receriverId = 0,
    this.callLength = 0,
    this.time = '0',
    this.message = ''
  });

  Map<String,dynamic> toJson(){
    Map<String,dynamic> map = {
      'id': id,
      'caller_id': callerId,
      'receiver_id': receriverId,
      'call_length': callLength,
      'time': time
    };
    return map;
  }

  factory Call.fromJson(Map<String, dynamic> json) {
    return Call(
        callerId: json['caller_id'] ?? 0,
        receriverId: json['receiver_id'] ?? 0,
        callLength: json['call_length'] ?? 0,
        time: json['time'] ?? ""
    );
  }

  factory Call.fromJsonMessage(Map<String, dynamic> json){
    return Call(
        message: json['message']
    );
  }
}

Future<List> getCalls(User user) async {
  final response = await http.get(Uri.parse('http://147.175.162.226:5000/get/calls/${user.userId}'),
      headers: {
        "token": user.token
      });
  print(response.body);
  final jsonMap = json.decode(response.body)["calls"];
  List<Call> temp = (jsonMap as List)
      .map((itemWord) => Call.fromJson(itemWord))
      .toList();

  return temp;
}