import socket
import threading
import sys
import os
import traceback

BACKLOG = 100           # maximum number of pending connections, in queue
BUFFER_SIZE = 10000     # maximum number of bytes, received at once
HOST = None             # the ip address (local) in which the server will run (set up in code)
PORT = None             # the port in which the server will listen to (taken as an input)

def main():
    # setting up HOST & PORT
    HOST = ''
    # HOST = socket.gethostbyname(socket.gethostname())
    try:
        PORT = int(input("Enter PORT: "))
    except KeyboardInterrupt:
        print("[ERROR] entering port")
        sys.exit(0)
    
    #  server socket creation & server listening to certain port
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(BACKLOG)
        print(f"[LISTENING] server [{HOST}] listening on port [{PORT}]")

        # create directory for cache
        os.makedirs('cache/', exist_ok=True)

    except Exception as e:
        print(f"[ERROR] server socket creation {e}")
        sys.exit(2)

    # accepting client & opening new thread 
    while True:
        try:
            (client, address) = server.accept()
            thread = threading.Thread(target = client_thread, args = (client, address))
            thread.start()
        except KeyboardInterrupt:
            server.close()
            print("\n[ERROR] accepting client")
            sys.exit(1)

    # closing server socket
    server.close()

def client_thread(client: socket.socket, address):
    print(f"[NEW CONNECTION] {address} connected")
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

    # receiving message from client & parsing it
    message = client.recv(BUFFER_SIZE)
    (url, port) = parse(message)
 
    # finding cache information
    (is_cached, cache_file, cache) = find_cache(url)

    try:
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.connect((url, int(port)))

        # cached already
        if (is_cached):
            print("[CACHED] cached already")

            last_modified = find_last_modified(cache)
            headers = create_headers(url, is_cached, last_modified)

            # send request to remote server 
            # if-modified-since included
            proxy.send(headers)

            # receive response
            response = proxy.recv(BUFFER_SIZE)
            response_status_code = int(response.decode().split('/r/n')[0].split(" ")[1])

            # response status code 304 = Not Modified
            # cache hasn't been modified since
            if (response_status_code == 304):
                print("[NOT-MODIFIED-SINCE] sending cached content")
                client.sendall(cache.encode())

            # otherwise, cache has been modified
            else:
                print("[MODIFIED-SINCE] sending modified version")
                client.sendall(response)

                # receiving rest of the response
                content = response
                receiving = True
                while receiving:
                    response = proxy.recv(BUFFER_SIZE)
                    if (len(response) > 0):
                        print(response)
                        content += response
                        client.sendall(response)
                    else:
                        receiving = False

                update_cache(cache_file, content)
                print("[CACHE UPDATED]")

        # not cached yet
        else:
            print("[NOT CACHED] not cached yet")

            headers = create_headers(url, is_cached)
            proxy.send(headers)

            content = b''
            receiving = True
            while receiving:
                response = proxy.recv(BUFFER_SIZE)
                if (len(response) > 0):
                    content += response
                    client.sendall(response)
                else:
                    receiving = False
            
            update_cache(cache_file, content)
            print("[CACHE UPDATED]")

    except Exception as e:
        print(f"[ERROR] setting up proxy socket\n{e}")

    finally:
        if (client):
            client.close()
        if (proxy):
            proxy.close()

# parse client's (browser) request into url & port        
def parse(message):
    # getting url from the request
    url = message.decode().split("\n")[0].split(" ")[1]
    # default HTTP port
    port = 80

    # removing http://
    if (url.find("://") != -1):
        url = url.split("://")[1]

    # getting port from url (if specified)
    if (url.find(":") != -1):
        (url, port) = url.split(":")

    # removing '/' as last character
    if(url[-1] == "/"):
        url = url[:-1]

    return (url, port)

# find cache for a website
def find_cache(url):
    cache_file = url.replace(".", "_")
    cache_file = cache_file.replace("/", "-")
    cache_file += '.txt'   
    
    cache_path = os.path.join("cache/", cache_file)
    if (os.path.isfile(cache_path)):
        with open(cache_path, 'r') as file:
            return True, cache_file, file.read()

    return False, cache_file, None

# update/save cache for a website
def update_cache(cache_file, content=b''):
    cache_path = os.path.join("cache/", cache_file)
    with open(cache_path, 'w') as file:
        file.write(content.decode())

# finds last-modified field from cache file
def find_last_modified(cache):
    data = cache.split("\n")
    last_modified = None
    for line in data:
        if (line.find("Last-Modified:") != -1):
            last_modified = line[15:]
    return last_modified

# returns HTTP headers according to parameters
def create_headers(host, is_cached=False, last_modified=None):
    if (is_cached):
        return f"GET / HTTP/1.1\r\nAccept: */*\r\nCache-Control: no-cache\r\nAccept-Encoding: utf8\r\nHost: {host}\r\nIf-Modified-Since: {last_modified}\r\nContent-type: text/html\r\nConnection: keep-alive\r\n\r\n".encode()
    else:
        return f"GET / HTTP/1.1\r\nAccept: */*\r\nCache-Control: no-cache\r\nAccept-Encoding: utf8\r\nHost: {host}\r\nContent-type: text/html\r\nConnection: keep-alive\r\n\r\n".encode()

if __name__ == '__main__':
    main()
