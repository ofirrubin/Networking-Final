
function logOut() {
    eel.logout();
}
function sendMsg(){
    let dropdown = document.getElementById("usersList");
    let msg = document.getElementById("msg");
    eel.send_msg(dropdown.options[dropdown.selectedIndex].value, msg.value);
    msg.value = "";
}

/* Selection drop functions - search, add and remove options*/
eel.expose(getDropValues)
function getDropValues(dropName){
    let selectElement = document.querySelectorAll('[name=' + dropName + ']');
    return [...selectElement[0].options].map(o => o.value);
}
eel.expose(containsInDrop)
function containsInDrop(dropName, value){
    let dropdown = document.getElementById(dropName);
    for (let i=0; i<dropdown.length; i++) {
        if (dropdown.options[i].value === value) {
            return true;
        }
    }
    return false;
}
eel.expose(clearDrop);
function clearDrop(dropname){
    let dropdown = document.getElementById(dropname)
    for (let i=0; i<dropdown.length; i++) {
        if (dropdown.options[i].value !== "")
            dropdown.removeChild(dropdown.options[i]);
    }
}
eel.expose(addToDrop);
function addToDrop(name, val){
    let downloadable = document.getElementById(name);
    let file = document.createElement("option");
    file.value = val;
    file.text = val;
    downloadable.appendChild(file);
}
eel.expose(removeFromDrop);
function removeFromDrop(name, val){
    let dropdown = document.getElementById(name);
    for (let i=0; i<dropdown.length; i++) {
        if (dropdown.options[i].value === val)
            dropdown.removeChild(dropdown.options[i]);
    }
}

/* Change view */
eel.expose(setLoginView);
function setLoginView(){
    document.getElementById("chatApp").style.display = "none";
    document.getElementById("login_window").style.display = "block";
    eel.check_connection(); // Ask python to check if the user is still connected.
    // The page might have been reloaded.
}
eel.expose(setChatView);
function setChatView(){
    document.getElementById("chatApp").style.display = "block";
    document.getElementById("ChatsDialog").innerHTML = ""; // Remove all known messages
    document.getElementById("login_window").style.display = "none";
}


eel.expose(alertUser);
function alertUser(text){
    alert(text);
}

/* Update message box*/
eel.expose(onMsgSent);
function onMsgSent(to, message){
    let msg = getDefaultTextBox();
    let allMsgs = document.getElementById("ChatsDialog");
    msg.style.float = "right";
    msg.style.marginLeft = "30px";

    msg.value = "Message to " + to + ": " + message;
    msg.textContent = msg.value;

    allMsgs.appendChild(msg);
}
eel.expose(onBroadcastSent);
function onBroadcastSent(message){
    let msg = getDefaultTextBox();
    let allMsgs = document.getElementById("ChatsDialog");
    msg.style.float = "right";
    msg.style.marginLeft = "30px";
    msg.value = "Broadcast: " + message;
    msg.textContent = msg.value;
    allMsgs.appendChild(msg);
}
eel.expose(onMsgRcv);
function onMsgRcv(from, message){
    let allMsgs = document.getElementById("ChatsDialog");
    let msg = getDefaultTextBox();
    msg.style.float = "left";
    msg.style.marginRight = "30px";
    msg.value = "Message from " + from + ": " + message;
    msg.textContent = msg.value;
    allMsgs.appendChild(msg);
}
eel.expose(onBroadcastRcv);
function onBroadcastRcv(from, message){
    let allMsgs = document.getElementById("ChatsDialog");
    let msg = getDefaultTextBox();
    msg.style.float = "left";
    msg.style.marginRight = "30px";
    msg.value = "Broadcast from " + from + ": " + message;
    msg.textContent = msg.value;
    allMsgs.appendChild(msg);
}
eel.expose(systemMessage);
function systemMessage(message_text){
    console.log("Adding system message: " + message_text);
    let msg = getDefaultTextBox();
    let allMsgs = document.getElementById("ChatsDialog");
    msg.value = message_text;
    msg.textContent = message_text;
    allMsgs.appendChild(msg);
}
function getDefaultTextBox(){
    let msg = document.createElement("div");
    msg.style.display = "block";
    msg.style.position = "sticky";
    msg.style.lineBreak = "loose";
    msg.style.color = "black";
    msg.style.padding = "10px";
    msg.style.width = "90%";
    msg.style.fontFamily = "Roboto Light";
    return msg;
}

async function onDownloadClicked(){
    let downloads = document.getElementById("FilesList");
    let file = downloads.options[downloads.selectedIndex].value;
    if (file !== "")
        eel.request_download(file);
}