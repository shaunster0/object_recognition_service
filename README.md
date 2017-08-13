# object\_recognition\_service
## web-based object recognition with CNN

**Introduction:** in this project I am building a CNN-based object recognition service. The main architectural features are a HTTP API using Flask (with data JSON encoded), and image classification using TensorFlow and a 3rd party class zoo.

**Requirements:** Python3, a number of packages such as Flask, TensorFlow, flask\_httpauth, Numpy, as well as some more common packages

**Installation:** obtain from GitHub at https://github.com/shaunster0/object_recognition_service (either clone or download \*.zip file and unzip). We will refer to the installation directory as the parent directory.

**Usage:** open a command prompt or shell in the **parent directory (installation directory)**.

To run the main server enter-

\>python -m recognition\_server.recognition\_server

To run the unit tests enter-

\>python -m unittest test.test\_recognition\_server

If the server is already running, a client program can be run, such as the example in the \examples subdirectory

\>python example\_client.py

**Internal Data Structure:** the server maintains a list of images (with URLs) in JSON format. These may or may not have had recognition inference run on them. This list can be regarded as a list of tasks to do, or that have been done.

**Example:** as an example, if the recognition\_server is running the Python command

`requests.put('http://127.0.0.1:5000/img/api/v1.0/infer/1', json = dict(id = 1))`

gives the output

```json
{
    "img": {
        "id": 1,
        "resize": false,
        "results": {
            "0": {
                "results_name": "running shoe",
                "results_score": "0.5944"
            },
            "1": {
                "results_name": "Loafer",
                "results_score": "0.0459"
            },
            "2": {
                "results_name": "jean, blue jean, denim",
                "results_score": "0.0165"
            },
            "3": {
                "results_name": "clog, geta, patten, sabot",
                "results_score": "0.0158"
            },
            "4": {
                "results_name": "cowboy boot",
                "results_score": "0.0115"
            }
        },
        "size": "",
        "title": "Nikes",
        "url": "http://imgdirect.s3-website-us-west-2.amazonaws.com/nike.jpg"
    }
}
```

