# Gundb server

This starts a simple gundb server.

The sever data required:

- `addr`: address of the server
- `port`: port of the server

To use first get an instance:

```python
gunserver = j.servers.gundb.get('myinstance')
```

To start the server you need to have NodeJs installed and the gun node module available, to install them:

```python
gunserver.install_dep()
```

Then to start the server in tmux:

```python
gunserver.start()
```

To stop the server:

```python
gunserver.stop()
```
