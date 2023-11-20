from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///homebot.db'
db = SQLAlchemy(app)

class Api:
    @staticmethod
    def run():
        with app.app_context():
            db.create_all()
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8888)

    @app.route('/api/groups', methods=['GET'])
    def get_groups():
        return jsonify(get_groups())

    @app.route('/api/devices', methods=['GET'])
    def get_devices():
        return jsonify(get_devices())

    @app.route('/api/add_device_test', methods=['GET'])
    def test_add_device():
        device = LightDevice(id=99, name='Test Device', status='on')
        add_device(device)
        return f"Added device {device.name} with status {device.status} and id {device.id}"

    @app.route('/api/add_group_test', methods=['GET'])
    def test_add_group():
        group = Group(name='Test Group')
        add_group(group)
        return f"Added group {group.name} with id {group.id}"

# db methods

def try_add_group(group):
    if not Group.query.filter_by(id=group.id).first():
        db.session.add(group)
        db.session.commit()

def try_add_device(device):
    if not LightDevice.query.filter_by(id=device.id).first():
        db.session.add(device)
        db.session.commit()

def get_groups():
    return [group.to_dict() for group in Group.query.all()]

def get_devices():
    return [device.to_dict() for device in LightDevice.query.all()]

# db models

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class LightDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status
        }
