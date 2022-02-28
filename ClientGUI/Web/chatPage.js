
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
function addToDrop(dropname, val){
    let downloadable = document.getElementById(dropname);
    let file = document.createElement("option");
    file.value = val;
    file.text = val;
    downloadable.appendChild(file);
}
eel.expose(removeFromDrop);
function removeFromDrop(dropname, val){
    let dropdown = document.getElementById(dropname);
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
    msg.value = "Message to " + to + ": " + message;
    msg.textContent = msg.value;
    allMsgs.appendChild(msg);
    allMsgs.appendChild(getLineBreak());
}
eel.expose(onBroadcastSent);
function onBroadcastSent(message){
    let msg = getDefaultTextBox();
    let allMsgs = document.getElementById("ChatsDialog");
    msg.style.float = "right";
    msg.value = "Broadcast: " + message;
    msg.textContent = msg.value;
    allMsgs.appendChild(msg);
    allMsgs.appendChild(getLineBreak());
}
eel.expose(onMsgRcv);
function onMsgRcv(from, message){
    let allMsgs = document.getElementById("ChatsDialog");
    let msg = getDefaultTextBox();
    msg.style.float = "left";
    msg.value = "Message from " + from + ": " + message;
    msg.textContent = msg.value;
    allMsgs.appendChild(msg);
    allMsgs.appendChild(getLineBreak());
}
eel.expose(onBroadcastRcv);
function onBroadcastRcv(from, message){
    let allMsgs = document.getElementById("ChatsDialog");
    let msg = getDefaultTextBox();
    msg.style.float = "left";
    msg.value = "Broadcast from " + from + ": " + message;
    msg.textContent = msg.value;
    allMsgs.appendChild(msg);
    allMsgs.appendChild(getLineBreak());
}
eel.expose(systemMessage);
function systemMessage(message_text){
    console.log("Adding system message: " + message_text);
    let msg = getDefaultTextBox();
    let allMsgs = document.getElementById("ChatsDialog");
    msg.value = message_text;
    msg.textContent = message_text;
    allMsgs.appendChild(msg);
    allMsgs.appendChild(getLineBreak());
}
function getDefaultTextBox(){
    let msg = document.createElement("p");
    msg.style.color = "black";
    msg.style.fontFamily = "Roboto Light";
    return msg;
}

function getLineBreak(){
    return document.createElement("br");
}

async function onDownloadClicked(){
    eel.request_download("file");
}