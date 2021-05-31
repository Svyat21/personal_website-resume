from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from app import login
from flask_login import UserMixin


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    resume_basic_information = db.relationship('ResumeBasicInformation', backref='author', lazy='dynamic')
    resume_work_experience = db.relationship('ResumeWorkExperience', backref='author', lazy='dynamic')
    resume_additional_information = db.relationship('ResumeAdditionalInformation', backref='author', lazy='dynamic')
    resume_education = db.relationship('ResumeEducation', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(5000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


class ResumeBasicInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    patronymic = db.Column(db.String(64))
    date_of_birth = db.Column(db.String(64))
    gender = db.Column(db.String(64))
    city_of_residence = db.Column(db.String(64))
    phone_number = db.Column(db.String(64))
    email = db.Column(db.String(128))
    link_social_network = db.Column(db.String(128))
    comment_link_social_network = db.Column(db.String(500))
    additional_link_social_network = db.Column(db.String(128))
    additional_comment_link_social_network = db.Column(db.String(500))
    desired_position = db.Column(db.String(128))
    comment_desired_position = db.Column(db.String(500))
    salary = db.Column(db.String(64))
    employment = db.Column(db.String(64))
    work_schedule = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ResumeWorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    started_working = db.Column(db.String(64))
    ending = db.Column(db.String(64))
    organization = db.Column(db.String(128))
    region = db.Column(db.String(64))
    company_field_activity = db.Column(db.String(128))
    post = db.Column(db.String(128))
    responsibilities_workplace = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ResumeAdditionalInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about_me = db.Column(db.String(1000))
    key_skills = db.Column(db.String(500))
    knowledge_languages = db.Column(db.String(500))
    citizenship = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ResumeEducation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(128))
    educational_institution = db.Column(db.String(500))
    conducting_organization = db.Column(db.String(500))
    faculty = db.Column(db.String(500))
    specialization = db.Column(db.String(128))
    year_completion = db.Column(db.String(64))
    comment = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
