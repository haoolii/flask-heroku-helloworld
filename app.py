from flask import Flask, request, escape, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import app_config
import datetime, os

app = Flask(__name__)
ma = Marshmallow(app)
app.config.from_object(app_config[os.getenv('FLASK_ENV')]())
db = SQLAlchemy(app)


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, default=datetime.datetime.now)

  def __repr__(self):
    return '<User %r>' % self.username

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("email", "date_created", "_links")

    # Smart hyperlinking
    _links = ma.Hyperlinks(
        {"self": ma.URLFor("user_detail", id="<id>"), "collection": ma.URLFor("users")}
    )

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route('/')
def hello():
    return 'Hello!Flask!'

@app.route('/api/users/', methods=['POST'])
def add_user():
    try:
        req_data = request.get_json()
        user = User(username= req_data['username'], email= req_data['email'])
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user)
    except Exception as error:
        abort(400,{'message': 'error'})

@app.route('/api/users/')
def users():
    all_users = User.query.all()
    return users_schema.dumps(all_users)

@app.route("/api/users/<id>")
def user_detail(id):
    user = User.query.filter_by(id=id).first()
    return user_schema.dump(user)