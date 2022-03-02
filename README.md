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


Demo video (click to go to Youtube):
[![IMAGE ALT TEXT HERE](https://github.com/ofirrubin/Networking-Final/blob/f3fccf26666d5cb88cd8f6defb21553c5ca3087b/Media/Login%20Screen.png)](https://www.youtube.com/watch?v=tiK175t1YfYE)



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
