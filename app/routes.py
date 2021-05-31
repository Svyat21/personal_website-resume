# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, NewPostForm, PersonalInformationForm, ContactsForm, \
    PositionForm, WorkExperienceForm, AdditionalInformationForm, AdditionalEducationForm, EducationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, ResumeBasicInformation, ResumeWorkExperience, ResumeAdditionalInformation, \
    ResumeEducation
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now() #strftime("%d.%m.%Y-%H:%M:%S")
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    form = NewPostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.post.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост опубликован!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    user = User.query.filter_by(username='Svyat').first_or_404()
    person_inform = ResumeBasicInformation.query.filter_by(user_id=user.id)
    works = ResumeWorkExperience.query.order_by(ResumeWorkExperience.timestamp.desc()).filter_by(user_id=user.id)
    add_inf = ResumeAdditionalInformation.query.filter_by(user_id=user.id)
    trainings = ResumeEducation.query.filter_by(user_id=user.id)
    return render_template(
        'index.html', title='Сайт-резюме', person_inform=person_inform,
        works=works, add_inf=add_inf, trainings=trainings, form=form, posts=posts.items,
        next_url=next_url, prev_url=prev_url
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный логин или пароль.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы зарегистрированы!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Пост опубликован.')
        return redirect(url_for('index'))
    return render_template('new_post.html', title='Написать пост', form=form)


@app.route('/personal_information', methods=['GET', 'POST'])
@login_required
def personal_information():
    form = PersonalInformationForm()
    if form.validate_on_submit():
        person_inform = ResumeBasicInformation(
            first_name=form.first_name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            city_of_residence=form.city_of_residence.data,
            user_id=current_user.id
        )
        db.session.add(person_inform)
        db.session.commit()
        flash('Персональная информация заполнена!')
        return redirect(url_for('resume', username=current_user.username))
    return render_template('personal_information.html', title='Персональная информация', form=form)


@app.route('/edit_personal_information', methods=['GET', 'POST'])
@login_required
def edit_personal_information():
    form = PersonalInformationForm()
    person_inform = ResumeBasicInformation.query.filter_by(user_id=current_user.id).first_or_404()
    if form.validate_on_submit():
        person_inform.first_name = form.first_name.data
        person_inform.surname = form.surname.data
        person_inform.patronymic = form.patronymic.data
        person_inform.date_of_birth = form.date_of_birth.data
        person_inform.gender = form.gender.data
        person_inform.city_of_residence = form.city_of_residence.data
        db.session.commit()
        flash('Персональная информация изменена.')
        return redirect(url_for('resume', username=current_user.username))
    elif request.method == 'GET':
        form.first_name.data = person_inform.first_name
        form.surname.data = person_inform.surname
        form.patronymic.data = person_inform.patronymic
        form.date_of_birth.data = person_inform.date_of_birth
        form.gender.data = person_inform.gender
        form.city_of_residence.data = person_inform.city_of_residence
    return render_template('edit_personal_information.html', title='Персональная информация', form=form)


@app.route('/edit_contacts', methods=['GET', 'POST'])
@login_required
def edit_contacts():
    form = ContactsForm()
    person_inform = ResumeBasicInformation.query.filter_by(user_id=current_user.id).first_or_404()
    if form.validate_on_submit():
        person_inform.phone_number = form.phone_number.data
        person_inform.email = form.email.data
        person_inform.link_social_network = form.link_social_network.data
        person_inform.comment_link_social_network = form.comment_link_social_network.data
        person_inform.additional_link_social_network = form.additional_link_social_network.data
        person_inform.additional_comment_link_social_network = form.additional_comment_link_social_network.data
        db.session.commit()
        flash('Контактная информация добавлена.')
        return redirect(url_for('resume', username=current_user.username))
    elif request.method == 'GET':
        form.phone_number.data = person_inform.phone_number
        form.email.data = person_inform.email
        form.link_social_network.data = person_inform.link_social_network
        form.comment_link_social_network.data = person_inform.comment_link_social_network
        form.additional_link_social_network.data = person_inform.additional_link_social_network
        form.additional_comment_link_social_network.data = person_inform.additional_comment_link_social_network
    return render_template('edit_contacts.html', title='Контактная информация', form=form)


@app.route('/edit_position', methods=['GET', 'POST'])
@login_required
def edit_position():
    form = PositionForm()
    person_inform = ResumeBasicInformation.query.filter_by(user_id=current_user.id).first_or_404()
    if form.validate_on_submit():
        person_inform.desired_position = form.desired_position.data
        person_inform.comment_desired_position = form.comment_desired_position.data
        person_inform.salary = form.salary.data
        person_inform.employment = form.employment.data
        person_inform.work_schedule = form.work_schedule.data
        db.session.commit()
        flash('Готово')
        return redirect(url_for('resume', username=current_user.username))
    elif request.method == 'GET':
        form.desired_position.data = person_inform.desired_position
        form.comment_desired_position.data = person_inform.comment_desired_position
        form.salary.data = person_inform.salary
        form.employment.data = person_inform.employment
        form.work_schedule.data = person_inform.work_schedule
    return render_template('edit_position.html', title='Желаемая должность', form=form)


@app.route('/work_experience', methods=['GET', 'POST'])
@login_required
def work_experience():
    form = WorkExperienceForm()
    if form.validate_on_submit():
        work_exp = ResumeWorkExperience(
            started_working=form.started_working.data,
            ending=form.ending.data,
            organization=form.organization.data,
            region=form.region.data,
            company_field_activity=form.company_field_activity.data,
            post=form.post.data,
            responsibilities_workplace=form.responsibilities_workplace.data,
            user_id=current_user.id
        )
        db.session.add(work_exp)
        db.session.commit()
        flash('Опыт работы сохранен.')
        return redirect(url_for('resume', username=current_user.username))
    return render_template('work_experience.html', title='Опыт работы', form=form)


@app.route('/edit_work_experience/<exp_id>', methods=['GET', 'POST'])
@login_required
def edit_work_experience(exp_id):
    form = WorkExperienceForm()
    work = ResumeWorkExperience.query.filter_by(id=exp_id).first_or_404()
    if form.validate_on_submit():
        work.started_working = form.started_working.data
        work.ending = form.ending.data
        work.organization = form.organization.data
        work.region = form.region.data
        work.company_field_activity = form.company_field_activity.data
        work.post = form.post.data
        work.responsibilities_workplace = form.responsibilities_workplace.data
        db.session.commit()
        flash('Опыт работы изменен.')
        return redirect(url_for('resume', username=current_user.username))
    elif request.method == 'GET':
        form.started_working.data = work.started_working
        form.ending.data = work.ending
        form.organization.data = work.organization
        form.region.data = work.region
        form.company_field_activity.data = work.company_field_activity
        form.post.data = work.post
        form.responsibilities_workplace.data = work.responsibilities_workplace
    return render_template('edit_work_experience.html', title='Опыт работы', form=form)


@app.route('/additional_information', methods=['GET', 'POST'])
@login_required
def additional_information():
    form = AdditionalInformationForm()
    if form.validate_on_submit():
        add_inf = ResumeAdditionalInformation(
            about_me=form.about_me.data,
            key_skills=form.key_skills.data,
            knowledge_languages=form.knowledge_languages.data,
            citizenship=form.citizenship.data,
            user_id=current_user.id
        )
        db.session.add(add_inf)
        db.session.commit()
        flash('Дополнительная информация сохранена.')
        return redirect(url_for('resume', username=current_user.username))
    return render_template('additional_information.html', title='Дополнительная информация', form=form)


@app.route('/edit_additional_information', methods=['GET', 'POST'])
@login_required
def edit_additional_information():
    form = AdditionalInformationForm()
    add_inf = ResumeAdditionalInformation.query.filter_by(user_id=current_user.id).first_or_404()
    if form.validate_on_submit():
        add_inf.about_me = form.about_me.data
        add_inf.key_skills = form.key_skills.data
        add_inf.knowledge_languages = form.knowledge_languages.data
        add_inf.citizenship = form.citizenship.data
        db.session.commit()
        flash('Дополнительная информация изменена.')
        return redirect(url_for('resume', username=current_user.username))
    elif request.method == 'GET':
        form.about_me.data = add_inf.about_me
        form.key_skills.data = add_inf.key_skills
        form.knowledge_languages.data = add_inf.knowledge_languages
        form.citizenship.data = add_inf.citizenship
    return render_template(
        'edit_additional_information.html', title='Дополнительная информация',
        form=form
    )


@app.route('/education', methods=['GET', 'POST'])
@login_required
def education():
    form = EducationForm()
    if form.validate_on_submit():
        training = ResumeEducation(
            level=form.level.data,
            educational_institution=form.educational_institution.data,
            faculty=form.faculty.data,
            specialization=form.specialization.data,
            year_completion=form.year_completion.data,
            user_id=current_user.id
        )
        db.session.add(training)
        db.session.commit()
        flash('Образвание сохранено.')
        return redirect(url_for('resume', username=current_user.username))
    return render_template('education.html', title='Образование', form=form)


@app.route('/edit_education/<education_id>', methods=['GET', 'POST'])
@login_required
def edit_education(education_id):
    form = EducationForm()
    training = ResumeEducation.query.filter_by(id=education_id).first_or_404()
    if form.validate_on_submit():
        training.level = form.level.data
        training.educational_institution = form.educational_institution.data
        training.faculty = form.faculty.data
        training.specialization = form.specialization.data
        training.year_completion = form.year_completion.data
        db.session.commit()
        flash('Образвание изменено.')
        return redirect(url_for('resume', username=current_user.username))
    elif request.method == 'GET':
        form.level.data = training.level
        form.educational_institution.data = training.educational_institution
        form.faculty.data = training.faculty
        form.specialization.data = training.specialization
        form.year_completion.data = training.year_completion
    return render_template('edit_education.html', title='Образование', form=form)


@app.route('/additional_education', methods=['GET', 'POST'])
@login_required
def additional_education():
    form = AdditionalEducationForm()
    if form.validate_on_submit():
        training = ResumeEducation(
            conducting_organization=form.conducting_organization.data,
            specialization=form.specialization.data,
            year_completion=form.year_completion.data,
            comment=form.comment.data,
            user_id=current_user.id
        )
        db.session.add(training)
        db.session.commit()
        flash('Дополнительное образование сохранено.')
        return redirect(url_for('resume', username=current_user.username))
    return render_template('additional_education.html', title='Дополнительное образование', form=form)


@app.route('/edit_additional_education/<education_id>', methods=['GET', 'POST'])
@login_required
def edit_additional_education(education_id):
    form = AdditionalEducationForm()
    training = ResumeEducation.query.filter_by(id=education_id).first_or_404()
    if form.validate_on_submit():
        training.conducting_organization = form.conducting_organization.data
        training.specialization = form.specialization.data
        training.year_completion = form.year_completion.data
        training.comment = form.comment.data
        db.session.commit()
        flash('Дополнительное образование изменено.')
        return redirect(url_for('resume', username=current_user.username))
    elif request.method == 'GET':
        form.conducting_organization.data = training.conducting_organization
        form.specialization.data = training.specialization
        form.year_completion.data = training.year_completion
        form.comment.data = training.comment
    return render_template(
        'edit_additional_education.html', title='Дополнительное образование', form=form
    )


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).filter_by(user_id=user.id).\
        paginate(page, app.config['POSTS_PER_PAGE'], False)
    follow_posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) if posts.has_prev else None
    follow_next_url = url_for('user', username=username, page=follow_posts.next_num) if follow_posts.has_next else None
    follow_prev_url = url_for('user', username=username, page=follow_posts.prev_num) if follow_posts.has_prev else None
    return render_template(
        'user.html', user=user, posts=posts.items, follow_posts=follow_posts.items,
        next_url=next_url, prev_url=prev_url, follow_next_url=follow_next_url,
        follow_prev_url=follow_prev_url, title=f'{username}'
    )


@app.route('/user/<username>/resume')
@login_required
def resume(username):
    user = User.query.filter_by(username=username).first_or_404()
    person_inform = ResumeBasicInformation.query.filter_by(user_id=user.id)
    works = ResumeWorkExperience.query.filter_by(user_id=user.id)
    add_inf = ResumeAdditionalInformation.query.filter_by(user_id=user.id)
    trainings = ResumeEducation.query.filter_by(user_id=user.id)
    return render_template(
        'resume.html', user=user, person_inform=person_inform, works=works, add_inf=add_inf,
        trainings=trainings, title='Резюме'
    )


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Изменения сохранены.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактировать профиль.', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Вы подписаны.')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Вы подписаны на {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Вы не можете отписаться.')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Вы не подписаны на {}.'.format(username))
    return redirect(url_for('user', username=username))
