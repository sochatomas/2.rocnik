import 'dart:convert';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../login/login_endpoint.dart';
import '../overview/calendar_screen.dart';

class Event{
  String title;
  String description;
  int id ;
  int userId;
  DateTime time;
  String file ;
  int contactId;
  String message;
 final String createdAt = DateTime.now().toString();
 MaterialColor color = listOfColors[Random().nextInt(5)];

  Event({
    this.userId = 0,
     this.contactId = 0,
    this.description = '',
    this.file = '',
    this.id = 0,
    DateTime? time ,
    this.title = '',
    this.message = "",
}): this.time = time ?? DateTime(2022);


  Map<String,dynamic> toJson(){
    Map<String,dynamic> map = {
      'title' : title.trim(),
      'description' : description.trim(),
      'time' : time,
      'file' : file.trim(),
      'id' : id,
      'contact_id' : contactId,
      'user_id' : userId,
    };
    return map;
  }

 factory Event.fromJson(Map<String, dynamic> json) {
    print(json['title'] + " subor: " + json['file']);

    DateTime date =DateTime(int.parse(json['time'].substring(12,16)),getMonth(json["time"].substring(8,11)) ,int.parse(json['time'].substring(5,7)),int.parse(json['time'].substring(17,19)),int.parse(json['time'].substring(20,22)),int.parse(json['time'].substring(23,25)));
    return Event(
      title: json['title'],
      description: json['description']?? "",
      time: date,
      file: json['file']?? "",
      id: json['event_id'],
      contactId: json['contact_id'] ?? "0",
    );
  }
  factory Event.fromJsonMessage(Map<String, dynamic> json){
    return Event(
      message: json['message'],
    );
  }
}


Future<List> getEventsToday(User user) async {

  final response = await http.get(Uri.parse('http://147.175.162.226:5000/get/user/events/today/${user.userId}'),
      headers: {
          "Connection": "Keep-Alive",
          "Keep-Alive": "timeout=5, max=1000",
          "token": user.token,
      });
  final jsonMap = json.decode(response.body)["events"];
  List<Event> temp = (jsonMap as List)
      .map((itemWord) => Event.fromJson(itemWord))
      .toList();
    // print(temp[0].title);

     // print(jsonDecode(response.body)["events"][0]);
    // return Event.fromJson(jsonDecode(response.body)["events"][0]);
  return temp;
  }

Future<List> getEvents(User user) async {

  final response = await http.get(Uri.parse('http://147.175.162.226:5000/get/user/events/${user.userId}'),
      headers: {
        "Connection": "Keep-Alive",
        "token": user.token,
      });
  final jsonMap = json.decode(response.body)["events"];
  List<Event> temp = (jsonMap as List)
      .map((itemWord) => Event.fromJson(itemWord))
      .toList();

  return temp;
}


Future<Event> postEvent(User user,Event event) async {
  final response = await http.post(Uri.parse('http://147.175.162.226:5000/add/event'),
      headers: {
        "token": user.token,
      },
      body: {
        "user_id":user.userId.toString() ,
        "title": event.title,
        "description": event.description,
        "time": event.time.toString(),
        "file": event.file,
        "contact_id": event.contactId.toString(),
      });
  return Event.fromJsonMessage(jsonDecode(response.body));
}


Future<Event> deleteEvent(User user,Event event) async {

  final response = await http.delete(Uri.parse('http://147.175.162.226:5000/delete/event/${event.id}'),
      headers: {
        "token": user.token,
      });
  return Event.fromJsonMessage(jsonDecode(response.body));
}

Future<Event> putEvent(User user,Event event) async {
  final response = await http.put(Uri.parse('http://147.175.162.226:5000/update/event/${event.id}'),
      headers: {
        "token": user.token,
      },
      body: {
        "title": event.title,
        "description": event.description,
        "time": event.time.toString(),
        // "file": event.file,
        "contact_id": event.contactId.toString(),
      });

  return Event.fromJsonMessage(jsonDecode(response.body));
}


int getMonth(String month) {
  if(month == "Jan") return 1;
  if(month == "Feb") return 2;
  if(month == "Mar") return 3;
  if(month == "Apr") return 4;
  if(month == "May") return 5;
  if(month == "Jun") return 6;
  if(month == "Jul") return 7;
  if(month == "Aug") return 8;
  if(month == "Sep") return 9;
  if(month == "Oct") return 10;
  if(month == "Nov") return 11;
  else return 12;
}