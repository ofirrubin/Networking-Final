window.onresize = function (){ // Make sure the window is not too small.
            if (window.outerWidth < 800 || window.outerHeight < 500){
                window.resizeTo(800, 500);
            }
    }
function ip_validity_check(str) { // Doesn't check range
    if (str.length < 7 || str.length > 15 || (str.split(".") || []).length !== 4)
        return false; // len(x.x.x.x) = 7, len(xxx.xxx.xxx.xxx) = 11
    for (let i = 0; i < str.length; i++){
        if (str[i] !== '.' && ('0' > str[i] || str[i] > '9'))
            return false;
    }
    return true;
}
function login_clicked(){
    // Get login request details
    let username = document.getElementById("username");
    let ip = document.getElementById("ip");
    let port = document.getElementById("port");
    let failed = false;
    // If username is not valid, show message
    if (username.value == null || username.value.length < 2 || username.value.includes("\n")){
        username.placeholder = "Invalid username";
        username.value = "";
        failed = true;
    }
    else{
        username.placeholder = "Username";
    }
    // If IP address sanity check is not valid (not checking actual value but chars)
    if (ip.value == null || !ip_validity_check(ip.value)){
        ip.placeholder = "Invalid IP";
        ip.value = "";
        failed = true;
    }
    else{
        ip.placeholder = "IP";
    }
    // If port is not valid
    if (port.value == null || port.value.length < 2 || isNaN(port.value)){
        port.placeholder = "Invalid Port number";
        port.value = "";
        failed = true;
    }
    else{
        port.placeholder = "Port";
    }
    // If not failed, login.
    if (! failed){
        username.title = "Logging in...";
        eel.login(ip.value, port.value, username.value);
    }
}

eel.expose(setInvalidPort);
function setInvalidPort(){ // Set InputBox text to indicate invalid port
    let port = document.getElementById("port");
    port.value = "";
    port.placeholder = "Please check the port number and try again..";
}

eel.expose(setInvalidIP);
function setInvalidIP(){ // Set InputBox text to indicate invalid IP
    let ip = document.getElementById("ip");
    ip.value = "";
    ip.placeholder = "Please check your IP address and try again..";
}

eel.expose(setUserNameInUse);
function setUserNameInUse(){ // Set InputBox text to indicate in use username
    let username = document.getElementById("username");
    username.value = "";
    username.placeholder = "Username in use! Try another one";
}

eel.expose(closeWindow)
function closeWindow(){ // Close frontend (to use from backend)
    window.open('', '_self').close();
}