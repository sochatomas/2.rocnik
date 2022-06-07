
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

import '../login/login_endpoint.dart';
import 'calls_endpoint.dart';

class VideoconferenceScreen extends StatefulWidget {
  final User user;
  const VideoconferenceScreen({Key? key,required this.user}) : super(key: key);

  @override
  State<VideoconferenceScreen> createState() => _VideoconferenceScreenState(user:this.user);


}

class _VideoconferenceScreenState extends State<VideoconferenceScreen> {
  User user;
  late Call call;
  late List<Call> listOfCalls = [];
  bool done = false;

  _VideoconferenceScreenState({required this.user});

  @override
  void initState() {
    super.initState();
    done = false;
    getCalls(user).then((value)
    {
      for( Call call in value){
        listOfCalls.add(call);
      }
      setState(() {
        done = true;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: _buildContent(context),
      appBar: AppBar(
        backgroundColor: Colors.cyan[800],
        elevation: 5,
        toolbarHeight: 80,
        title: const Text(
          "Recent Calls",
          textAlign: TextAlign.center,
          style: TextStyle(
          color: Colors.white,
          ),
        ),
      )
    );
  }

  Widget _buildContent(BuildContext){
    if(listOfCalls.length == 0 && done){
      return Center(child: Text("No recent calls"));
    }
    return ListView.separated(
      padding: EdgeInsets.all(0.0),
      itemCount: listOfCalls.length,
      separatorBuilder: (context,index) {
        return SizedBox(height: 0,);
      },
      itemBuilder: (context,index) {
        return buildCard(listOfCalls[index]);   // TODO riadok s menom a možnosťou rovno volať
      },
    );
  }

  Widget buildCard(Call call) {
    return Container(
      color: Colors.white,
      height: 100,
      child: Row(
        children: [
          SizedBox(width: 30,),
          Text(
          "Receiver ID: " + call.receriverId.toString() + "   Length: ${call.callLength}s\nTime: " + call.time.toString(),
          style: TextStyle(fontSize: 15),
        ),
        SizedBox(width: 25,),
        FloatingActionButton(
          backgroundColor: Colors.green[600],
         child: Icon(Icons.call,),
            onPressed: (){})],
      ),
    );
  }

}