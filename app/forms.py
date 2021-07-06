from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Используйте другой логин.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Используйте другой email.')


class EditProfileForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Сохранить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Используйте другой логин.')


class NewPostForm(FlaskForm):
    post = TextAreaField('Ваше сообщение:', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Оставить сообщение')


class ResumeForm(FlaskForm):
    first_name = StringField('Ваше имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    date_of_birth = StringField('Дата рождения')
    gender = SelectField('Пол', choices=[('мужчина', 'муж.'), ('женщина', 'жен.')])
    submit = SubmitField('Сохранить')


class PersonalInformationForm(FlaskForm):
    city_of_residence = StringField('Город проживания', validators=[DataRequired()])
    phone_number = StringField('Контактный номер', validators=[DataRequired()])
    email = StringField('Контактный email', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=1000)])
    knowledge_languages = TextAreaField('Знание языков', validators=[Length(min=0, max=500)])
    citizenship = StringField('Гражданство', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class PositionForm(FlaskForm):
    desired_position = StringField('Желаемая должность', validators=[DataRequired()])
    professional_area = StringField('профессиональная сфера')
    salary = StringField('Желаемая зарплата', validators=[DataRequired()])
    employment = StringField('Занятость', validators=[DataRequired()])
    work_schedule = StringField('График', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class SocialNetworkForm(FlaskForm):
    link_social_network = StringField('Ссылка на соц. сеть')
    comment_link_social_network = StringField('Комментарий')
    submit = SubmitField('Сохранить')


class WorkExperienceForm(FlaskForm):
    started_working = StringField('Начало работы', validators=[DataRequired()])
    ending = StringField('Окончание', validators=[DataRequired()])
    organization = StringField('Организация', validators=[DataRequired()])
    region = StringField('Регион', validators=[DataRequired()])
    company_field_activity = StringField('Сфера деятельности', validators=[DataRequired()])
    post = StringField('Должность', validators=[DataRequired()])
    responsibilities_workplace = TextAreaField('Обязанности', validators=[Length(min=0, max=1000)])
    submit = SubmitField('Сохранить')


class KeySkillsForm(FlaskForm):
    skill_tag = TextAreaField('Навык (тег)', validators=[Length(min=0, max=128)])
    submit = SubmitField('Сохранить')


class EducationForm(FlaskForm):
    level = StringField('Образование', validators=[DataRequired()])
    educational_institution = StringField('Учебное заведение', validators=[DataRequired()])
    faculty = StringField('Факультет', validators=[DataRequired()])
    specialization = StringField('Специализация', validators=[DataRequired()])
    year_completion = StringField('Год окончания', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class AdditionalEducationForm(FlaskForm):
    conducting_organization = StringField('Организация', validators=[DataRequired()])
    specialization = StringField('Специализация', validators=[DataRequired()])
    year_completion = StringField('Год окончания', validators=[DataRequired()])
    comment = TextAreaField('Комментарий', validators=[Length(min=0, max=1000)])
    submit = SubmitField('Сохранить')
