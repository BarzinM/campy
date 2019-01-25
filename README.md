# Campy

## Known Issues
If ROS is messing up the path for OpenCV, specially when trying to use python3 then do:

```bash
source fix_ros # to fix it in current terminal
```

or

```bash
bash fix_ros # to permanently add python3 dist-packages path to PYTHONPATH at boot
```


## Classes

### `Camera` Class

Operates USB cameras using OpenCV library.

#### `__init__` Method

Object constructor.

##### Args

- `device_number`: The numerical value associated with the hardware by the OS.

#### `display` Method

Displays the frames received from the hardware. This is a blocking function.

#### `capture` Method

Starts capturing the frames without displaying them. This is a non-blocking function. It uses multi-threading library for starting a thread that stores the most recent frame.

##### Args

- `device_number`: The numerical value associated with the hardware by the OS.

#### `monitor` Method

Opens a windows and starts displaying the frames. This is a blocking function. One can think of this method as a combination of `capture` and `display` methods.

##### Args

- `device_number`: The numerical value associated with the hardware by the OS.

#### `close` Method

Destructs the object. Ends all the threads and removes the access to camera hardware.

#### `get` Method

Returns the frame as a ndarray.

##### Args

- `blocking`: A boolean that indicates if the method should wait for a new frame or return whatever it contains in its buffer.

#### `setSize` Method

Sets the width and height of the frame.

##### Args

- `width`: An integer value corresponding the number of horizontal pixels.
- `height`: An integer value corresponding the number of vertical pixels.

### `Stream` Class

This is a subclass of `Camera` class with added functionality of streaming frames over a connection.

#### `server` Method

This method should be called on the server machine to setup the connection. It takes the IP address and port number of the server to establish the connection. It is also possible to not use this method, setup the connection separately, and pass the connection handle to `send` and `receive` methods below. It should be noted that the server can either be the sender of camera frames or the receiver.

##### Args

- `ip`: IP address of the server.
- `port`: Port number of server.
- `backlog`: Connection backlog.

#### `client` Method

This method should be called on the client machine to setup the connection. It takes the IP address and port number of the server to establish the connection. It is also possible to not use this method, setup the connection separately, and pass the connection handle to `send` and `receive` methods below. It should be noted that the client can either be the sender of camera frames or the receiver.

##### Args

- `ip`: IP address of the server.
- `port`: Port number of server.


#### `send` Method

A non-blocking method that starts streaming the frames over the connection. If the connection has been configured using `server` or `client` methods, then the `connection` argument can be left unassigned.

##### Args

- `connection`: TCP connection handle.

#### `receive` Method

A non-blocking method that starts receiving the frames over the connection. If the connection has been configured using `server` or `client` methods, then the `connection` argument can be left unassigned.

##### Args

- `connection`: TCP connection handle.
