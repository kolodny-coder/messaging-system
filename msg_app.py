import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


# Message Class/Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(20), nullable=False)
    receiver = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_message_read = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, sender, receiver, subject, body):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body


# Message Schema
class MessageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'sender', 'receiver', 'subject', 'body', 'date_posted', 'is_message_read')


# Init Schema
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)


# Create a Message
@app.route('/message', methods=['POST'])
def add_message():
    sender = request.json['sender']
    receiver = request.json['receiver']
    subject = request.json['subject']
    body = request.json['body']

    new_message = Message(sender, receiver, subject, body)
    db.session.add(new_message)
    db.session.commit()

    return message_schema.jsonify(new_message)


# Get all Messages by user
@app.route('/message/<sender>/<status>', methods=['GET'])
def get_messages_by_sender(sender, status):
    if status == 'all':
        db.session.query(Message).filter_by(sender=sender).update({"is_message_read": True})
        all_messages = Message.query.filter_by(sender=sender).all()

        result = messages_schema.dump(all_messages)

        return jsonify(result)
    if status == 'unread':
        # db.session.query(Message).filter_by(sender=sender, is_message_read=False).update({"is_message_read": True})

        all_messages = Message.query.filter_by(sender=sender, is_message_read=False).all()

        result = messages_schema.dump(all_messages)

        return jsonify(result)


# Get Single Messages
@app.route('/message/<int:id>', methods=['GET'])
def get_message(id):
    message = Message.query.get(id)
    if message:
        message.is_message_read = True
        db.session.commit()

    return message_schema.jsonify(message)


# Delete Message
@app.route('/message/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    db.session.delete(message)
    db.session.commit()
    return message_schema.jsonify(message)


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
