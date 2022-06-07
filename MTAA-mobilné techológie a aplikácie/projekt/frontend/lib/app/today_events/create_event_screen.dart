import 'dart:convert';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mtaa_frontend/app/globals.dart';
import '../home_screen.dart';
import 'today_events_endpoint.dart';
import 'dart:io';
import '../../widgets/login_text_field.dart';
import '../login/login_button.dart';
import '../login/login_endpoint.dart';
import 'package:flutter_datetime_picker/flutter_datetime_picker.dart';
import 'package:path/path.dart' as Path;

class CreateEvent extends StatefulWidget {
  final User user;
  const CreateEvent({Key? key,required this.user}) : super(key: key);

  @override
  State<CreateEvent> createState() => _CreateEventState(user:this.user);
}

class _CreateEventState extends State<CreateEvent> {
  String _message = "One of required fields is empty(title,date,time)";
  double _op = 0;
  bool _dateBool = false;
  bool _timeBool = false;
  String _date = " Date Not set \t\t\t\t\t\t\t\t                  Change";
  String _time = "Time Not set \t\t\t\t\t\t\t\t                  Change";
  User user;
  DateTime date_dateTime = DateTime(2022);
  DateTime time_dateTime = DateTime(2022);
  File? attachedImage = null;
  String imageEncoded = "";
  var title_ctr = TextEditingController();
  var description_ctr = TextEditingController();
  var contact_ctr = TextEditingController();

  _CreateEventState({required this.user});
  final scaffoldKey = GlobalKey<ScaffoldState>();

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
          onPressed: () =>
              Navigator.pop(context),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
    );
  }

  Widget _buildContent(BuildContext context){
    final fileName = attachedImage != null ? Path.basename(attachedImage!.path) : 'No Image Selected';

    return Padding(
      padding: EdgeInsets.all(30.0),
      child: ListView(
        children: <Widget>[

          const Text(
            'Create event',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 30,
              fontWeight: FontWeight.w500,
            ),
          ),

          const SizedBox(height: 40.0),
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
              onConfirm: (date) {_date = date.toString().substring(0,10);_dateBool = true;date_dateTime = date;
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
                    onConfirm: (time) {_time = time.toString().substring(11,19); _timeBool=true;time_dateTime = time;
                  setState(() {});},
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
          const SizedBox(height: 10),

          incorrectAddEventMessage(),

          Padding(
              padding: EdgeInsets.fromLTRB(40, 0, 40, 0),
              child: ElevatedButton.icon(
                onPressed: selectImage,
                icon: Icon(
                    Icons.insert_photo,
                ),
                label: Text('Attach an Image'),
                style: ElevatedButton.styleFrom(
                  primary: Colors.cyan[800],
                  fixedSize: Size(150, 60),
                  shape: new RoundedRectangleBorder(
                    borderRadius: new BorderRadius.circular(50),
                  ),
                ),
              ),
          ),

          const SizedBox(height: 5),

         SizedBox(
          height: 30.0,

          child: Text(
            fileName,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.black,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),


          const SizedBox(height: 10),

          AddEventButton(title_ctr, description_ctr, contact_ctr),
          const SizedBox(height: 10.0),
        ],
      ),
    );
  }

  Future selectImage() async {
    // final result = await FilePicker.platform.pickFiles(allowMultiple: false);
    //
    // if (result == null){
    //   return;
    // }
    //
    // final path = result.files.single.path!;
    final result = await ImagePicker().pickImage(source: ImageSource.gallery);

    attachedImage = File(result!.path);

    Uint8List imgbytes = attachedImage!.readAsBytesSync();
    imageEncoded = base64.encode(imgbytes);

    // setState(() => attachedImage = File(path));
    // setState(() {});
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
        text: "Add event",
        textColor: Colors.white,
        color: Colors.cyan[800],
        elevation: 20,
        onPressed: () {
          if (title_ctr.text == "" || _timeBool == false || _dateBool == false){
            print("title chyba");
            changeOpacityOne();
          }else{
            int contact_id;
              if (contact_ctr.text == '') contact_id = 0;
              else contact_id = int.parse(contact_ctr.text);

            Event event = Event(
                time: DateTime(date_dateTime.year,date_dateTime.month,date_dateTime.day,time_dateTime.hour,time_dateTime.minute,time_dateTime.second),
                title: title_ctr.text,
                description: description_ctr.text,
                contactId:contact_id,
                file:imageEncoded,
            );
              if (connected == true)
                {
                  postEvent(user,event).then((value) async {
                    if(value.message == "Success")
                      {
                        changeOpacityZero();
                        if(event.time.day == DateTime.now().day && event.time.month == DateTime.now().month && event.time.year == DateTime.now().year)
                          eventsToday.add(event);
                        eventsAll.add(event);
                        print("bol som tu");
                        final snackBar = SnackBar(
                            content: Text("Event successfully created"));
                        ScaffoldMessenger.of(context).showSnackBar(snackBar);
                        setState(() {});
                        await getEvents(currentUser).then((value)
                        { eventsAll.clear();
                        for( Event event in value){
                          eventsAll.add(event);
                        }
                        Navigator.pop(context);
                        });

                      }
                    else{
                        if(value.message == "Fail")
                          {
                            changeOpacityOne();
                          }
                    }
                  });
                }else{
                if(event.time.day == DateTime.now().day && event.time.month == DateTime.now().month && event.time.year == DateTime.now().year)
                  eventsToday.add(event);
                eventsAll.add(event);
                eventsAdded.add(event);
                changeOpacityZero();
                final snackBar = SnackBar(
                    content: Text("Event successfully created"));
                ScaffoldMessenger.of(context).showSnackBar(snackBar);
                setState(() {});
                Navigator.pop(context);

              }




          }
        },
      ),
    );
  }

}

