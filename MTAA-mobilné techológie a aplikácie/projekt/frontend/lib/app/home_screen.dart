

import 'dart:io';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:date_format/date_format.dart';
import 'package:mtaa_frontend/app/globals.dart';

import 'package:mtaa_frontend/app/login/login_endpoint.dart';
import 'package:mtaa_frontend/app/today_events/create_event_screen.dart';
import 'package:mtaa_frontend/app/today_events/today_events_endpoint.dart';
import 'package:mtaa_frontend/app/videoconference/videoconference_screen.dart';
import 'overview/calendar_screen.dart';


class HomeScreen extends StatefulWidget {
  final User user;
  const HomeScreen( {Key? key,required this.user}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState(user:this.user);
}

class _HomeScreenState extends State<HomeScreen> {
  final now = DateTime.now();
   User user;
   late Event event;
   late List<Event> listofevents = [];
   bool done = false;

  // late StreamSubscription _connectionChangeStream;
  // bool isOffline = false;

     _HomeScreenState({required this.user});

  @override
  void initState() {
    super.initState();
    currentUser = user;
    done = false;
    getEventsToday(user).then((value)
    {
      for( Event event in value){
        listofevents.add(event);
        eventsToday.add(event);
      }
      setState(() {
        done = true;
      });

    });
    // ConnectionStatusSingleton connectionStatus = ConnectionStatusSingleton.getInstance();
    // _connectionChangeStream = connectionStatus.connectionChange.listen(connectionChanged);
  }

  // void connectionChanged(dynamic hasConnection) {
  //   setState(() {
  //     print(hasConnection);
  //     isOffline = !hasConnection;
  //   });
  // }

  void changeState(){
    // listofevents.clear();
    done = false;
    print("state changed");
    // getEventsToday(user).then((value)
    // {
    //   for( Event event in value){
    //     listofevents.add(event);
    //   }
    //   print(listofevents);
    //
    //   setState(() {
    //     done = true;
    //   });
    //
    // });

    setState(() {
      listofevents = eventsToday;
      done = true;
    });
    // print(eventsToday);
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: _someData(),
      builder: (context, snapshot) {
        return Scaffold(
          backgroundColor: Colors.white,
          body: _buildContent(context),
          drawer: Drawer(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                SizedBox(
                  height: 100,
                  child: DrawerHeader(
                    decoration: BoxDecoration(
                      color: Colors.cyan[800],
                    ),
                    child: Text(' '
                    ,style: TextStyle(
                        color: Colors.black87,
                        fontSize: 20,
                      ),),
                  ),
                ),
                ListTile(
                  title: const Text('Overview'),
                  onTap: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                        builder: (context) => Calendar(user: user,),)).then((value){
                          changeState();
                    });
                  },
                ),
                ListTile(
                  title: const Text('Videoconference'),
                  onTap: () {
                    print(listofevents);
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => VideoconferenceScreen(user: user,),)).then((value){
                      changeState();
                    });

                  },
                ),
                ListTile(
                  title: const Text('Log out'),
                  onTap: () {
                    Navigator.of(context).popUntil((route) => route.isFirst);
                  },
                ),
                ListTile(
                  textColor: Colors.red,
                  title: const Text('Remove account',
                    style: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  onTap: () {
                              deleteUser(user).then((value)
                              {
                                if(value.message == "Success")
                                {
                                  final snackBar = SnackBar(
                                      content: Text("Account was successfully removed"));
                                  ScaffoldMessenger.of(context).showSnackBar(snackBar);
                                  Navigator.of(context).popUntil((route) => route.isFirst);
                                }
                                else{
                                  if(value.message == "Fail")
                                  {
                                    final snackBar = SnackBar(
                                        content: Text("Error. User wasn't deleted"));
                                    ScaffoldMessenger.of(context).showSnackBar(snackBar);
                                  }
                                }
                              });
                  },
                ),
              ],
            ),
          ),
          floatingActionButton: FloatingActionButton.extended(
            heroTag: const Text("btn2"),
            label: Text('Create event'),
            icon: Icon(Icons.add),
            backgroundColor:Colors.cyan[800],
            onPressed: (){
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => CreateEvent(user: user,),maintainState: false,
                )).then((value){
                  changeState();
              }); },

          ),

          appBar: AppBar(
            backgroundColor: Colors.cyan[800],
            elevation: 5,
            toolbarHeight: 60,

            title: Text(
              formatDate(now,[DD,'  ',dd,'.',mm,'.',yyyy]),
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white,
              ),
            ),

            // leading: IconButton(
            //   icon: const Icon(
            //     Icons.arrow_back_ios_new_outlined,
            //     color: Colors.black,
            //     size: 40,
            //   ),
            //   onPressed: () => Navigator.of(context).pop(),
            // ),
          ),
        );
      }
    );


  }

  Widget _buildContent(BuildContext){
    if(listofevents.length == 0 && done){
      return Center(child: Text("No events today"));
    }
    return ListView.separated(
      padding: EdgeInsets.all(0.0),
      itemCount: listofevents.length,
      separatorBuilder: (context,index) {
        return SizedBox(height: 0,);
      },
      itemBuilder: (context,index) {
        return buildCard(listofevents[index]);
      },


    );
  }
  List <MaterialColor>listOfColors = [Colors.red,Colors.blue,Colors.green,Colors.purple,Colors.orange,Colors.yellow];

  Widget buildCard(Event event) {
    return Container(
      color: event.color,
      height: 100,
      child: Center(
        child: Text(
          event.title +"\n"+event.time.toString().substring(10,19),
        ),
      ),
    );
  }

}

 _someData()async* {
   // await Future.doWhile(() => _tryConnection());
   // print("vyplo ma");
   // var connectivityResult = await (Connectivity().checkConnectivity());
   // print(connectivityResult);
   // print("\n");

   // if (connectivityResult == ConnectivityResult.mobile) {
   //   // I am connected to a mobile network.
   //   print("pripojeny");
   // } else if (connectivityResult == ConnectivityResult.wifi) {
   //   // I am connected to a wifi network.
   //   print("pripojeny wifi");
   // }
// while(true) {
//   await Future.doWhile(() {
//     bool? oldConnection = connected;
//     _tryConnection().then((value) {
//       if (oldConnection == false && connected!) {
//         print("back online");
//         pushEverythingToDatabase().then((value) {
//           print(value);
//         });
//
//         // sleep(Duration(seconds: 2));
//         // getAllEvents();
//         // getTodayEvents();
//       } else {
//         sleep(Duration(seconds: 1));
//         print(connected);
//       }
//     });
//     return false;
//   });
//   sleep(Duration(seconds: 3));
// }

  yield* Stream.periodic(Duration(seconds: 1),(int a) async {
    bool? oldConnection = connected;
    bool end = false;
    await tryConnection().then((value) async {

      if((oldConnection == false) && (connected!) && (inProgress == false))
      {
        print("back online");
        backOnline = true;
        inProgress = true;
          await pushEverythingToDatabase().then((value){
            print(value);
            // if(eventsAdded.isEmpty && eventsEdited.isEmpty && eventsDeleted.isEmpty)
            //   {
            //     getAllEvents();
            //     getTodayEvents();
            //   }

          });

      }
      // print(connected);

    });
    if(eventsAdded.isEmpty && eventsEdited.isEmpty && eventsDeleted.isEmpty && backOnline)
    {
      backOnline = false;
      inProgress = false;
       getAllEvents();
       getTodayEvents();
       end = true;
    }
    if(end == true)
      { end == false;
        appointments_list = getAppointments(eventsAll);
      }

  });
  // if(eventsAdded.isEmpty && eventsEdited.isEmpty && eventsDeleted.isEmpty)
  // {
  //   getAllEvents();
  //   getTodayEvents();
  // }
}
Future getAllEvents()async{
  await getEvents(currentUser).then((value)
  { eventsAll.clear();
  for( Event event in value){
    eventsAll.add(event);
  }
  });
}

Future getTodayEvents()async{
 await getEventsToday(currentUser).then((value)
  { eventsToday.clear();
  for( Event event in value){
    eventsToday.add(event);
  }
  });
}


Future<bool> pushEverythingToDatabase() async {
  if(eventsAdded.isNotEmpty)
    {
     await pushEventsToDatabase().then((value){
      });

    }
  if(eventsEdited.isNotEmpty)
  {
   eventsEdited.forEach((element)
    async {
     await putEvent(currentUser, element).then((value)
      {
        if(value.message == "Success")
        {
          eventsEdited.remove(element);
        }else {
          if (value.message == "Fail") {
            print("error in editing event");
          }
        }
      });
    });
  }
  if(eventsDeleted.isNotEmpty){
   eventsDeleted.forEach((element)
    async {
      await deleteEvent(currentUser, element).then((value)
      {
        if(value.message == "Success")
        {
          eventsDeleted.remove(element);
        }else
        {
          print("error in removing event");
        }
      });
    });

  }

  return true;
}
Future<bool> pushEventsToDatabase() async {
  eventsAdded.forEach((element)
  async {
    await postEvent(currentUser,element).then((value){
      if(value.message == "Success")
      {
        eventsAdded.remove(element);
      }
      else{
        if(value.message == "Fail")
        {
          print("error in adding event");
          return false;
        }
      }
    });
  });
  return true;
}

Future<bool> tryConnection() async {
  try {
    final response = await InternetAddress.lookup('example.com');
    connected = response.isNotEmpty;
    return true;

  } on SocketException catch (e) {
    connected = false;
    return false;
  }
}

