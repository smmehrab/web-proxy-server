# web-proxy-server

A simple text-based HTTP client that keeps a local cache of the objects (base HTML) fetched.

Whenever the client is instructed to fetch an object (base HTML) from a remote HTTP server, it searches its local cache and displays it if the object was not modified at the server. However, if the object stored in the local cache is out-of-date (or not available) then the HTTP client must fetch the object from the server display it. 

<br>

## Submitted By

S.M.Mehrabul Islam

Roll: N/A (Readmission) 

Lab #2 A Simple Web Proxy Client 

CSE-3111 (Computer Networking Lab)

15 February 2022

<br>

## Requirements

The following requirements must be fulfilled before using it on your system: 

- Python 3 must be installed on your system

- You must manually set your system's HTTP proxy via network settings. Set the host as 'localhost' or '127.0.0.1' and set the port as your given input during the program execution. The process of setting these up may vary depending on your OS (Windows/Linux/Mac). 

- Make sure, the port you are entering as input, are currently free. 

<br>

## How to Use

**1. Download**

You can download the code from [here](https://drive.google.com/file/d/1QIfscRZcKrhWp-FNXhMP1FTu07UwnpIE/view?usp=sharing).

**2. Run**

(Make sure you are in the same directory as the soure code)

```
    python3 proxy.py
```

**3. Enter PORT**

It will ask you to enter a port, on which the server will be listening.
```
Enter Port: 
```
Enter a port, that's currently free. 

**4. Good to GO**

You should receive an output like this:
```
[LISTENING] server [] listening on port [8888]
```
And you are good to go. Now you can open your browser (preferrably, incognito) and try any HTTP website to test the functionality of the program.

<br>

## Assumptions

- This program only supports HTTP based website. 
- It can't fetch other objects in the base HTML file.
- It can only handle ```GET``` requests. Other HTTP requests aren't supported yet.
- As 'localhost' is used as the server's host address, it is accessable only from the system it's running on. 
- ```BACKLOG = 100```, which means it can support up to 100 pending connections in queue.
- ```BUFFER_SIZE = 10000```, which means it can receive up to 10000 bytes at once.
