# object_recognition_service
##web-based object recognition with CNN

**Introduction:** in this project I am building a CNN-based object recognition service. The main architectural features are a HTTP API using Flask, and image classification using TensorFlow and a 3rd party class zoo.

**Requirements:** Python3, a number of packages such as Flask, TensorFlow, flask\_httpauth, Numpy, as well as some more common packages

**Installation:** obtain from GitHub at https://github.com/shaunster0/object_recognition_service (either clone or download \*.zip file and unzip). We will refer to thhe installation directory as the parent directory.

**Usage:** open a command prompt or shell in the parent directory (installation directory).

To run the main server enter-

\>python -m recognition\_server.recognition\_server

To run the unit tests enter-

\>python -m unittest test.test\_recognition\_server

If the server is already running, a client program can be run, such as the example in the \examples subdirectory

