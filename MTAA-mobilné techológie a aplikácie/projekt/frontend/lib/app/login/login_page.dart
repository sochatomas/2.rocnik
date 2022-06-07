import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:mtaa_frontend/app/globals.dart';
import 'package:mtaa_frontend/app/home_screen.dart';

import 'package:mtaa_frontend/app/login/login_button.dart';
import 'package:mtaa_frontend/app/register/register_page.dart';
import '../../widgets/login_text_field.dart';
import 'login_endpoint.dart';

class loginPage extends StatefulWidget {
  const loginPage({Key? key}) : super(key: key);

  @override
  State<loginPage> createState() => LoginPageState();
}

class LoginPageState extends State<loginPage> {
  late User usrData;
  var username_ctr = TextEditingController();
  var password_ctr = TextEditingController();
  double _op = 0;
  late Future<User> userFuture;


  @override
  void initState() {
    super.initState();
    userFuture = postLogin(username_ctr.text, password_ctr.text);
    usrData = User();
  }

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
      body: _buildContent(context),
      backgroundColor: Colors.white,
    );
  }

  Widget _buildContent(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(30.0),
      child: ListView(
        children: <Widget>[
          Image.asset("images/logo.jpg"),

          logInTextField("username", username_ctr, false),

          const SizedBox(height: 10),
          logInTextField("password", password_ctr, true),

          const SizedBox(height: 15),
          incorrectLoginMessage(),

          LogInButton(
            text: "Log In",
            textColor: Colors.white,
            color: Colors.cyan[800],
            elevation: 20,
            onPressed: (){
              postLogin(username_ctr.text, password_ctr.text).then((value)
              {
                if(value != null)
                  {
                    if(value.token.isNotEmpty)
                      {
                        // print(value.token);
                        usrData.userId = value.userId;
                        usrData.token = value.token;
                        usrData.username = username_ctr.text;
                        changeOpacityZero();
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (context) => HomeScreen(user: usrData)
                                  ));
                                  deleteGlobals();
                      }else {changeOpacityOne();}
                  }
              });
            }

          ),
          SizedBox(height: 30),
          const Text(
            'Don\'t have an account?',
            textAlign: TextAlign.center,
          ),

          const SizedBox(height: 10.0),
          Container(
            decoration: BoxDecoration(
                color: Colors.white,
                border: Border.all(
                  color: Colors.white,
                )),
            child: LogInButton(
              text: "Create account",
              textColor: Colors.cyan[800],
              color: Colors.white,
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => RegisterPage()),
                );
              },
            ),
          ),
          const SizedBox(height: 10.0),
        ],
      ),
    );
  }

  SizedBox incorrectLoginMessage() {
    return SizedBox(
      height: 30.0,
      child: Opacity(
        opacity: _op,
        child: const Text(
          "The username or password is incorrect",
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Colors.red,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
}
