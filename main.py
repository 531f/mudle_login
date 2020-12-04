import requests


def login_mudle(email, password):
    # Hacky splits because I'm lazy
    split0 = '<a class="btn-uamaltlogin btn-block" href="'
    split1 = '" title="Login via ID-UAM">'

    split2 = '<input type="hidden" name="AuthState" value="'
    split3 = '" />'

    split4 = '<input type="hidden" name="SAMLResponse" value="'
    split5 = '" />'

    split6 = '<input type="hidden" name="RelayState" value="'
    split7 = '" />'

    # Start the session to automatically save the cookies
    s = requests.Session()

    # Visit moodle
    r = s.get("https://moodle.uam.es/")
    link_login = r.text.split(split0)[1].split(split1)[0]

    # Enter login page
    r = s.get(link_login)

    # Extract auth_state
    auth_state = r.text.split(split2)[1].split(split3)[0]

    # Send user/pass
    payload = {
        "AuthState": auth_state,
        "username": email,
        "password": password
    }
    r = s.post("https://cas.uam.es/module.php/core/loginuserpass.php", data=payload)

    # Post middle
    saml_response = r.text.split(split4)[1].split(split5)[0]
    relay_state = r.text.split(split6)[1].split(split7)[0]
    payload = {
        "SAMLResponse": saml_response,
        "RelayState": relay_state
    }
    s.post("https://moodle.uam.es/auth/saml2/sp/saml2-acs.php/moodle.uam.es", data=payload)
    return s


if __name__ == "__main__":
    email = "USERNAME@estudiante.uam.es"
    password = "PASSWORD"

    # Create the loging session
    logged_session = login_mudle(email, password)
    # Now you can request anything that requires you to login to moodle

    # Open the main page of moodle
    r = logged_session.get("https://moodle.uam.es/message/index.php")

    # Extract the sesskey and enter the chat service
    sesskey = r.text.split('"sesskey":"')[1].split('",')[0]
    user_url = f"https://moodle.uam.es/lib/ajax/service.php?sesskey={sesskey}"

    # Make a request to the chat API to get as many moodle users as you want
    r = logged_session.post(user_url, json=[
        {
            "index": 0, # No idea :)
            "methodname":"core_message_data_for_messagearea_search_users", # API request (see https://docs.moodle.org/dev/Talk:Web_service_API_functions)
            "args":
            {
                "userid": 160595, # You should probably change this to your own userid (extract it using burp suite while sending a message in moodle)
                "search": "", # Here you can search letters or names
                "limitnum": 100 # Number of users you want, don't go too high
            }
        }
    ])

    # Print the results
    from pprint import pprint
    pprint(r.json())
