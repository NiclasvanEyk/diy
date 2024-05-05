# Project Structure

We will roughly use the following simple structure for our application:

```
weather/
├── cli.py
├── client/
│  ├── protocol.py
│  ├── client_1.py
│  └── client_2.py
├── container.py
└── http.py
```

We have a file for each of our interfaces to the outside world (`cli.py` for our commandline interface and `http.py` for our HTTP server).

Our business logic lives in the `client/` directory, where we define the central protocol for getting the data in `protocol.py` and one for each specific client.
There is nothing stopping you from putting all of the business logic on one file, but separating them better shows their shared structure.

Finally we glue everything together in `container.py`, where all our `diy` `Specification`s and `Container`s are configured.
These are then used in `cli.py` and `http.py` to retrieve pre-configured services that implement our business logic.