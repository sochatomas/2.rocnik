
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:mtaa_frontend/app/overview/edit_event.dart';
import 'package:syncfusion_flutter_calendar/calendar.dart';

import '../globals.dart';
import '../home_screen.dart';
import '../login/login_endpoint.dart';
import '../today_events/create_event_screen.dart';
import '../today_events/today_events_endpoint.dart';
import 'package:xen_popup_card/xen_card.dart';
import 'edit_event.dart';


class Calendar extends StatefulWidget {
  final User user;
  const Calendar({Key? key,required this.user}) : super(key: key);

  @override
  State<Calendar> createState() => _CalendarState(user:this.user);
}

class _CalendarState extends State<Calendar> {
  User user;
  bool done = false;
  late List<Event> listofevents = [];
  bool? _isConnectionSuccessful;

  _CalendarState({required this.user});

  @override
  void initState() {
    super.initState();
    done = false;
    print(eventsAll);
    print(listofevents);
    print(connected);
    if(connected == false)
      {
        print(listofevents);
        listofevents = eventsAll;
        done = true;
      }
    else{
      getEvents(user).then((value)
      { listofevents.clear();
        eventsAll.clear();
        for( Event event in value){
          listofevents.add(event);
          eventsAll.add(event);
        }
        setState(() {
          done = true;
        });
      });
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(

      body: SfCalendar(
        view: CalendarView.week,
        firstDayOfWeek: 1,
        onTap:calendarTapped,
        dataSource: MeetingDataSource(getAppointments(eventsAll)),
      ),
      floatingActionButton: FloatingActionButton.extended(
        heroTag: const Text("btn1"),
        label: Text('Create event'),
        icon: Icon(Icons.add),
        backgroundColor:Colors.cyan[800],
        onPressed: (){Navigator.push(
            context,
            MaterialPageRoute(
                builder: (context) => CreateEvent(user: user,)
            )).then((value){
              setState(() {
                // listofevents.clear();
                // done = false;
                // getEvents(user).then((value)
                // {
                //   for( Event event in value){
                //     listofevents.add(event);
                //   }
                //   setState(() {
                //     done = true;
                //   });
                // });
                listofevents = eventsAll;
              });
        });},
      ),
      appBar: AppBar(
        backgroundColor: Colors.cyan[800],
      ),
    );
  }

  void calendarTapped(CalendarTapDetails details) {
    double _op = 0;
    if (details.targetElement == CalendarElement.appointment ||
        details.targetElement == CalendarElement.agenda) {
      final Appointment appointmentDetails = details.appointments![0];

      print("som t");
      for(Event event in eventsAll)
        {
          if((event.id == appointmentDetails.id) || (appointmentDetails.id == 0 && appointmentDetails.subject == event.title && appointmentDetails.startTime == event.time) )
            {
              print(appointmentDetails.location);
              print("---");
              print(event.createdAt);
                if(event.id == 0 && (event.createdAt != appointmentDetails.location))
                  {
                    continue;
                  }
              if(event.file != ""){
                _op=1;
              }
              showDialog(
                  context: context,
                  builder: (BuildContext context) {
                    return XenPopupCard(
                      appBar: XenCardAppBar(
                        shadow: BoxShadow(color: Colors.transparent),
                        child: Row(

                          children:[
                            FloatingActionButton.extended(
                              backgroundColor: Colors.cyan[800],
                              label: Text('Remove'),
                              icon: Icon(Icons.remove),
                              onPressed: () async {
                                print(tryConnection());
                                if (connected == true)
                                  {
                                    deleteEvent(user, event).then((value)
                                    {
                                      if(value.message == "Success")
                                        {
                                          final snackBar = SnackBar(
                                              content: Text("Event was removed"));
                                          ScaffoldMessenger.of(context).showSnackBar(snackBar);
                                          setState(() {
                                            print("tuuu");
                                            listofevents.remove(event);
                                            eventsAll.remove(event);
                                            Navigator.pop(context);
                                          });
                                        }else
                                          {
                                            final snackBar = SnackBar(
                                                content: Text("Error in removing event"));
                                            ScaffoldMessenger.of(context).showSnackBar(snackBar);
                                            setState(() {
                                              Navigator.pop(context);
                                            });
                                          }

                                    });
                                  }
                                else
                                  {
                                    final snackBar = SnackBar(
                                        content: Text("Event was removed"));
                                    ScaffoldMessenger.of(context).showSnackBar(snackBar);
                                    setState(() {
                                      listofevents.remove(event);
                                      eventsAll.remove(event);

                                      if(eventsAdded.contains(event))
                                      {
                                        eventsAdded.remove(event);
                                      }
                                      else
                                      {
                                        eventsDeleted.add(event);
                                      }
                                      if(eventsEdited.contains(event))
                                      {
                                        eventsEdited.remove(event);
                                      }
                                      Navigator.pop(context);
                                      // if (eventsToday.remove(event) == false)
                                      // {
                                      //   for(Event event1 in eventsToday)
                                      //   {
                                      //     if(event1.id == event.id)
                                      //     {
                                      //       eventsToday.remove(event1);
                                      //       break;
                                      //     }
                                      //   }
                                      // }

                                    });
                                  }
                                if (eventsToday.remove(event) == false)
                                {
                                  for(Event event1 in eventsToday)
                                  {
                                    if(event1.id == event.id)
                                    {
                                      eventsToday.remove(event1);
                                      break;
                                    }
                                  }
                                }


                              },
                            ),

                            SizedBox(width: 40,),
                            FloatingActionButton.extended(
                              backgroundColor: Colors.cyan[800],
                              label: Text('Edit'),
                              icon: Icon(Icons.edit),
                              onPressed: (){
                                Navigator.pushReplacement(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>EditEvent(event:event,user: user,),
                                  ),
                                ).then((value){
                                  setState(() {
                                  });
                                });
                              },
                            ),
                          ],
                        ),
                      ),
                      body: Center(

                        child: Container(
                          alignment: Alignment.bottomCenter,
                          child: Column(
                            children: [
                              SizedBox(height: 50,),
                              Text(event.title,
                              style: TextStyle(
                                fontSize: 25,
                                fontWeight: FontWeight.w600,
                              ),),
                              SizedBox(height: 20,),
                              Text(event.time.day.toString() + "." + event.time.month.toString() + "." + event.time.year.toString() + event.time.toString().substring(10,19)),
                              SizedBox(height: 20,),
                              Text(event.description),
                              SizedBox(height: 20,),
                              Opacity(
                                  opacity: _op,
                                  child: Image.memory(base64Decode(event.file),)
                              )
                            ],
                          ),
                        ),
                      ),
                     gutter:  XenCardGutter(
                       shadow: BoxShadow(color: Colors.transparent),
                       child: Padding(
                           padding: EdgeInsets.all(20.0),
                         child: FloatingActionButton.extended(
                           backgroundColor: Colors.green[600],
                            label: Text('Call'),
                            icon: const Icon(Icons.call),
                            onPressed: (){},
                          ),
                       ),
                     ),
                    );
                  });
            }
        }
    }
  }

}

class MeetingDataSource extends CalendarDataSource{
  MeetingDataSource(List<Appointment> source){
    appointments = source;
  }
}
List <MaterialColor>listOfColors = [Colors.red,Colors.blue,Colors.green,Colors.purple,Colors.orange,Colors.yellow];

List<Appointment> getAppointments(List<Event> listofevents) {
  List<Appointment> meetings = <Appointment>[];
  for(Event event in listofevents)
  {
    meetings.add(Appointment(
    startTime: event.time,
    endTime:  event.time.add(const Duration(hours: 1)),
    subject: event.title,
    notes: event.description,
    id: event.id,
    location: event.createdAt,
    color: event.color ));
  }

  return meetings;
}
