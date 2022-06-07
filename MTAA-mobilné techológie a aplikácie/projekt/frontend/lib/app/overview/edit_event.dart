import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mtaa_frontend/app/globals.dart';
import 'package:mtaa_frontend/app/today_events/today_events_endpoint.dart';

import '../../widgets/login_text_field.dart';
import '../login/login_button.dart';
import '../login/login_endpoint.dart';
import 'package:flutter_datetime_picker/flutter_datetime_picker.dart';



class EditEvent extends StatefulWidget {
  final Event event;
  final User user;
  const EditEvent({Key? key,required this.event,required this.user}) : super(key: key);

  @override
  State<EditEvent> createState() => _EditEventState(event:this.event,user:this.user);
}

class _EditEventState extends State<EditEvent> {
  String _message = "One of required fields is empty(title,date,time)";
  double _op = 0;

  DateTime date_dateTime = DateTime(2022);
  DateTime time_dateTime = DateTime(2022);
  String _date = '';
  String _time = '';
  var title_ctr = TextEditingController();
  var description_ctr = TextEditingController();
  var contact_ctr = TextEditingController();
  Event event;
  User user;
  final scaffoldKey = GlobalKey<ScaffoldState>();

  _EditEventState({required this.event,required this.user});


  void changeOpacityOne() {
    setState(() {
      _op = 1;
    });
  }

  void changeOpacityZero() {
    setState(() {
      _op = 0;
    });
  }

  @override
  void initState() {
    super.initState();
  _date =   event.time.toString().substring(0,10);
  _time = event.time.toString().substring(11,19);
    date_dateTime = event.time;
    time_dateTime = event.time;
    title_ctr.text = event.title;
    description_ctr.text = event.description;
    contact_ctr.text = event.contactId.toString();
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      key: scaffoldKey,
      backgroundColor: Colors.white,
      body: _buildContent(context),
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios_new_outlined,
            color: Colors.black,
            size: 40,
          ),
          onPressed: () => Navigator.pop(context)
        ),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
    );
  }

  Widget _buildContent(BuildContext context){

    return Padding(
      padding: EdgeInsets.all(30.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[

          const Text(
            'Edit event',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 30,
              fontWeight: FontWeight.w500,
            ),
          ),

          const SizedBox(height: 50.0),
          logInTextField("Title",title_ctr,false),
          const SizedBox(height: 20.0),
          FloatingActionButton(
              backgroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20.0)),
              elevation: 4.0,
              onPressed: () {
                DatePicker.showDatePicker(context,
                    showTitleActions: true,
                    minTime: DateTime.now(),
                    maxTime: DateTime(2025, 12, 31),
                    onChanged: (date) {_date = date.toString().substring(0,10);;},
                    onConfirm: (date) {_date = date.toString().substring(0,10);date_dateTime = date;
                    setState(() {});},
                    currentTime: DateTime.now(), locale: LocaleType.en);},
              child: Text('$_date',
                style: TextStyle(
                  color: Colors.cyan[800],
                ),)
          ),

          const SizedBox(height: 20),
          FloatingActionButton(
            backgroundColor: Colors.white,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20.0)),
            elevation: 4.0,
            onPressed: () {
              DatePicker.showTimePicker(context,
                  showTitleActions: true,
                  onChanged: (time) {_time = time.toString().substring(11,19);},
                  onConfirm: (time) {_time = time.toString().substring(11,19);time_dateTime = time;
                  setState(() {_time = time.toString().substring(11,19);});},
                  currentTime: DateTime.now(), locale: LocaleType.en);},
            child: Text('$_time',
              style:TextStyle(
                color: Colors.cyan[800],
              ),
            ),
          ),
          const SizedBox(height: 20),
          logInTextField("Description",description_ctr,false),

          const SizedBox(height: 20),
          TextField(
            controller: contact_ctr,
            keyboardType: TextInputType.number,
            inputFormatters: <TextInputFormatter>[
              FilteringTextInputFormatter.digitsOnly
            ],
            decoration: const InputDecoration(
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.grey),
                borderRadius: BorderRadius.all(Radius.circular(20)),
              ),
              border: InputBorder.none,
              contentPadding: EdgeInsets.symmetric(horizontal: 20),
              hintText: "Contact ID",
            ),
          ),


          const SizedBox(height: 20),
          incorrectAddEventMessage(),

          AddEventButton(title_ctr, description_ctr, contact_ctr),
          const SizedBox(height: 10.0),
        ],
      ),
    );
  }
  SizedBox incorrectAddEventMessage() {
    return SizedBox(
      height: 30.0,
      child: Opacity(
        opacity: _op,
        child: Text(
          _message,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Colors.red,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
  Container AddEventButton(TextEditingController title_ctr, TextEditingController description_ctr, TextEditingController contact_ctr) {
    return Container(
      decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(
            color: Colors.white,
          )
      ),
      child: LogInButton(
        text: "Edit event",
        textColor: Colors.white,
        color: Colors.cyan[800],
        elevation: 20,
        onPressed: () {
          if (title_ctr.text == "" ){
            changeOpacityOne();
          }else{
            int contact_id;
            if (contact_ctr.text == '') contact_id = 0;
            else contact_id = int.parse(contact_ctr.text);

            Event eventChanged = Event(
              time: DateTime(date_dateTime.year,date_dateTime.month,date_dateTime.day,time_dateTime.hour,time_dateTime.minute,time_dateTime.second),
              title: title_ctr.text,
              description: description_ctr.text,
              contactId:contact_id,
              id: event.id,
              file: event.file,
            );
            if(connected == true)
              {
                putEvent(user, eventChanged).then((value)
                {
                  if(value.message == "Success")
                    {
                      changeOpacityZero();
                      event.time = eventChanged.time;
                      event.title = eventChanged.title;
                      event.description = eventChanged.description;
                      event.contactId = eventChanged.contactId;

                      final snackBar = SnackBar(
                          content: Text("Event successfully edited"));
                      ScaffoldMessenger.of(context).showSnackBar(snackBar);
                      Navigator.pop(context);

                    }else {
                    if (value.message == "Fail") {
                      changeOpacityOne();
                    }
                  }
                    });
              }else
                {
                  if(title_ctr.text.isNotEmpty)
                  {
                    changeOpacityZero();
                    event.title = title_ctr.text;
                    event.time = eventChanged.time;
                    event.description = description_ctr.text;
                    event.contactId = contact_id;
                    if(eventsEdited.contains(event) == false && eventsAdded.contains(event) == false)
                      eventsEdited.add(event);
                    print(eventChanged.time);

                    if(event.time.day == DateTime.now().day && event.time.month == DateTime.now().month && event.time.year == DateTime.now().year)
                    {
                      if(eventsToday.contains(event) == false)
                      {
                        for(Event eventToday in eventsToday)
                        {
                          if(eventToday.id == event.id)
                          {
                            eventsToday.remove(eventToday);
                            eventsToday.add(event);
                            eventsToday.sort((a, b) => a.time.compareTo(b.time));
                          }
                        }
                      }
                    }
                    final snackBar = SnackBar(
                        content: Text("Event successfully edited"));
                    ScaffoldMessenger.of(context).showSnackBar(snackBar);
                    Navigator.pop(context);
                  }else
                  {
                    changeOpacityOne();
                  }
                }


          }
        },
      ),
    );
  }

}
