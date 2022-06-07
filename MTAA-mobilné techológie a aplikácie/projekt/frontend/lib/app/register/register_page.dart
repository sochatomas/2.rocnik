import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

import '../../widgets/login_text_field.dart';
import '../login/login_button.dart';
import '../login/login_endpoint.dart';


class RegisterPage extends StatefulWidget {
  const RegisterPage({Key? key}) : super(key: key);

  @override
  State<RegisterPage> createState() => RegisterPageState();
}

class RegisterPageState extends State<RegisterPage> {
  String _message = "Passwords aren't same";
  double _op = 0;
  final scaffoldKey = GlobalKey<ScaffoldState>();

  void changeMessageMissing(){
    setState(() {
      _message = "One of required field is missing.";
    });
  }
void changeMessagePassword(){
  setState(() {
    _message = "Passwords aren't same.";
  });
}

void changeMessageUsername(){
  setState(() {
    _message = "Username already exists, try different.";
  });
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
          onPressed: () => Navigator.of(context).pop(),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
    );
  }


  Widget _buildContent(BuildContext context){
    var username_ctr = TextEditingController();
    var password_ctr = TextEditingController();
    var password_ctr2 = TextEditingController();

    return Padding(
      padding: EdgeInsets.all(30.0),
      child: ListView(

        children: <Widget>[
          SizedBox(height: 100,),
          const Text(
            'Create account',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 30,
              fontWeight: FontWeight.w500,
            ),
          ),

          const SizedBox(height: 50.0),
          logInTextField("username",username_ctr,false),

          const SizedBox(height: 10),
          logInTextField("password",password_ctr,true),

          const SizedBox(height: 15,),
          logInTextField("password again",password_ctr2,true),

          const SizedBox(height: 30),
          incorrectRegisterMessage(),

          RegisterButton(password_ctr2, password_ctr, username_ctr),
          const SizedBox(height: 10.0),
        ],
      ),
    );
  }


  SizedBox incorrectRegisterMessage() {
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

  Container RegisterButton(TextEditingController password_ctr2, TextEditingController password_ctr, TextEditingController username_ctr) {
    return Container(
          decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(
                color: Colors.white,
              )
          ),
          child: LogInButton(
            text: "Register",
            textColor: Colors.white,
            color: Colors.cyan[800],
            elevation: 20,
            onPressed: () {
              if(password_ctr2.text == "" || username_ctr.text == "")
                {
                  changeMessageMissing();
                  changeOpacityOne();
                }else {
                if (password_ctr2.text != password_ctr.text) {
                  changeMessagePassword();
                  changeOpacityOne();
                }
                else {
                  postRegister(username_ctr.text, password_ctr2.text).then((
                      value) {
                    if (value.message == "Success") {
                      changeOpacityZero();
                      final snackBar = SnackBar(
                          content: Text("Registration successful"));
                      ScaffoldMessenger.of(context).showSnackBar(snackBar);
                    } else {
                      if (value.message == "Fail") {
                        changeMessagePassword();
                        changeOpacityOne();
                        print("pouzivatel nevytvoreny");
                      } else {
                        changeMessageUsername();
                        changeOpacityOne();
                        print("The user already exists");
                      }
                    }
                  }
                  );
                }
              }
            },
          ),
        );
  }

}

