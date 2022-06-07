import 'package:mtaa_frontend/app/today_events/today_events_endpoint.dart';
import 'package:mtaa_frontend/app/videoconference/calls_endpoint.dart';
import 'package:syncfusion_flutter_calendar/calendar.dart';
import 'package:synchronized/synchronized.dart';

import 'login/login_endpoint.dart';
import 'overview/calendar_screen.dart';
List<User> users = <User>[];
List<Call> calls = <Call>[];
User currentUser = User();
List <Appointment> appointments_list = getAppointments(eventsAll);
MeetingDataSource meetingDataSource = MeetingDataSource(appointments_list);

List<Event> eventsToday = <Event>[];
List<Event> eventsAll = <Event>[];
List<Event> eventsEdited = <Event>[];
List<Event> eventsAdded = <Event>[];
List<Event> eventsDeleted = <Event>[];
bool? connected = true;
bool backOnline = false;
bool inProgress = false;
final lock = new Lock();

deleteGlobals (){
  users = <User>[];
  calls = <Call>[];
  eventsToday = <Event>[];
  eventsAll = <Event>[];
  eventsEdited = <Event>[];
  eventsAdded = <Event>[];
  eventsDeleted = <Event>[];
  connected = true;
}


