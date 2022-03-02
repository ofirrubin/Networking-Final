Welcome!

Chat Application Project - Networking Course Finale


How To Run:


Download the requirements from:
```pip3 install -r requirements.txt```


Note that the Server and the client are modules so you have to run them with the module argument (-m):
For further information how to config the server/client you can learn using --help

To run the server:
```python3 -m Server```


To run the console client:
```python3 -m ConsoleClient```

To run the GUI client:


Since I can't do Wiki with private repo, I'll add the images and examples below.

Demo video (click to go to Youtube):
[![Watch on Youtube](https://github.com/ofirrubin/Networking-Final/blob/f3fccf26666d5cb88cd8f6defb21553c5ca3087b/Media/Login%20Screen.png)](https://www.youtube.com/watch?v=tiK175t1YfYE)


The Assignment had 2 parts:
* Chat-Messaging: TCP based Server&Client to allow passing text messages and details between users.
* File transferring (FT): UDP based Server&Client to allow downloading files from the server.

Since FT is based on UDP, we had to implement the control over the Application level.
The chat part allows the following functionality:
    Send & Receive Messages - Both in private (DM) and broadcast
    View list of online users.
    View list of available files to download.
The FT part allows the following functionality:
    Download files:
        - Full File Download (Continuous)
        - Resumable (0- End Offset)
        - Partial (Start Offset - End Offset)
        - Block verification

* FT implementation idea:
    Unlike TCP which is a stream, UDP = Datagram.
    So we have can't have "contentious conversation".
    In order to create TCP-like connection we might face some issues such as the requirement to save
    per-client information, messages-confirmations, know what data to retransmit in case of a loss, details
    to allow us to change the window size etc.
    All of these are liabilities that the server has to carry to create it.
        
    My idea is the following:
    The server is a dummy-server that responds blindly to the requests,
    The server will get a request including window-size, the required file and offset
    and send the required respond.
    On the other hand, the client will handle the data-verification, window-size etc.
    That means that the client is responsible for his own RTT & CC.
    
    The client will change these by the following parameters:
    Round-Trip-Time like = which also includes the data handling part.
    Dynamic Window Size = Using the RTT-like and the size left to be received we create a relative ratio compared to the last ratio and changing the window size accordingly.

    The client will also use the hash received by the server to validate each block of data it receives, so it can send the request again (allowing retransmitting per block)
    
    
    
GUI:
A while ago I found the ``eel`` package which usages javascript-html as frontend to the python program.
I found this opportunity to learn JavaScript, CSS and HTML and create this simple UI which would've been way harder design in Tkinter.
After learning JS, it was easy to link the UI to the backend since I already created the Console application.
There are two disadvantages for using the ``eel``:
1. You need to have supported 'engine': eel supports mainly chrome and electron but it can also convert it to the user default webbrowser. I figured since chrome is already the most used webbrowser, it should be fine.
2.```eel``` is using Network-Socket (TCP) as the PIPE between the backend and the frontend. As a result you can't run the same program twice without changing the parameters (port number), For now I chose to use the module ```teno``` which allows us to block multi-instances of the program using Singletone, I might change that later. 

Examples of the UI:


Quick Demo on Ubuntu too (the same as shown in MacOS):

Click the following image to watch
[![Watch on Youtube](https://github.com/ofirrubin/Networking-Final/blob/2c884c4c5deda61871297d9f00c6419aa156ab01/Media/Ubuntu%20TN.png)](https://youtu.be/Dc3d_evXV3M)


Screenshots:

<img src="https://github.com/ofirrubin/Networking-Final/blob/f3fccf26666d5cb88cd8f6defb21553c5ca3087b/Media/Login%20Screen.png" alt="Login page" width="400">

<img src="https://github.com/ofirrubin/Networking-Final/blob/d270eef949bfd18ace95fc7f5346279dfb07b64c/Media/Home%20:%20Messages.png" alt="Messages Page" width="400">

<img src="https://github.com/ofirrubin/Networking-Final/blob/d270eef949bfd18ace95fc7f5346279dfb07b64c/Media/Files%20Dropdown.png" alt="Files Dropdown" width="400">

<img src="https://github.com/ofirrubin/Networking-Final/blob/d270eef949bfd18ace95fc7f5346279dfb07b64c/Media/Users:Brodcast%20Dropdown.png" alt="Message Type Dropdown" width="400">

