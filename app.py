from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
from celery import Celery
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
celery_thread = None
count = 0

def my_monitor(app):
    state = app.events.State()

    def announce_tasks(event):
        global count

        state.event(event)

        # task name is sent only with -received event, and state
        # will keep track of this for us.
        if 'uuid' in event:
          task = state.tasks.get(event['uuid'])

          count += 1

          socketio.emit('my response', {'data': 'EVENT %s: %s[%s] %s' % (
              event['type'], task.name, task.uuid, task.info(), ), 'count': count},
            namespace='/test')

          print('TASK %s: %s[%s] %s' % (event['type'],
              task.name, task.uuid, task.info(), ))

    with app.connection() as connection:
      recv = app.events.Receiver(connection, handlers={
              '*': announce_tasks,
      })
      recv.capture(limit=None, timeout=None, wakeup=True)

def background_celery_thread():
    app = Celery(broker='amqp://guest:guest@127.0.0.1:49153//')
    my_monitor(app)

@app.route('/')
def index():
    global celery_thread
    if celery_thread is None:
        celery_thread = Thread(target=background_celery_thread)
        celery_thread.start()
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    global count
    count += 1

    emit('my response', {'data': 'Connected', 'count': count})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
