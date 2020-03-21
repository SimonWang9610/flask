from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from flask_pagedown.fields import PageDownField

from ..models import Role, User

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(0, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must be have only numbers, dots'
                                              'underscores and letters')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)

    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)

        # initialise the choices of SelectField
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    # check whether the new email exists before binding another email to current account
    def validate_email(self, field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    # check whether the new username exists before changing to a new username
    def validate_username(self, field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use!')

class PostForm(FlaskForm):
    body = PageDownField('What do you want to write?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = StringField('Enter your comment:', validators=[DataRequired()])
    submit = SubmitField('Submit')

