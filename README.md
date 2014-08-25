Celery-SocketIO Example
==============

A super simple example to demonstrate how to monitor celery task progress
in realtime by using Flask-SocketIO

Example
-------
    from celery import Celery
    from flask import Flask, render_template
    from flask.ext.socketio import SocketIO, emit

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app)
    celery_thread = None

    @app.route('/')
    def index():
        global celery_thread
        if celery_thread is None:
            celery_thread = Thread(target=background_celery_thread)
            celery_thread.start()
        return render_template('index.html')

    def background_celery_thread():
        app = Celery(broker='amqp://guest:guest@127.0.0.1:49153//')
        my_monitor(app)

    @socketio.on('my event')
    def test_message(message):
        emit('my response', {'data': 'got it!'})

    def my_monitor(app):

        with app.connection() as connection:
          recv = app.events.Receiver(connection, handlers={
                  '*': do_something,
          })
          recv.capture(limit=None, timeout=None, wakeup=True)

    if __name__ == '__main__':
        socketio.run(app)

Resources
---------

- [Tutorial](http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent)
- [Documentation](http://pythonhosted.org/Flask-SocketIO)
- [PyPI](https://pypi.python.org/pypi/Flask-SocketIO)

