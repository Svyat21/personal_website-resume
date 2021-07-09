# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, NewPostForm, PersonalInformationForm, \
    SocialNetworkForm, PositionForm, WorkExperienceForm, AdditionalEducationForm, EducationForm, \
    KeySkillsForm, ResumeForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Resume, BasicInformation, SocialNetwork, KeySkills, WorkExperience, Education, \
    AdditionalEducation
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    главная страница
    """
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
    svyat_res = Resume.query.filter_by(user_id=user.id).first_or_404()
    return render_template(
        'index.html', title='Сайт-резюме', svyat_res=svyat_res, form=form, posts=posts.items,
        next_url=next_url, prev_url=prev_url
    )


@app.route('/user/<username>')
@login_required
def user(username):
    """
    Страница пользователя
    """
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
        follow_prev_url=follow_prev_url, title='Python developer'
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Вход
    """
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
    """
    Выход
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Регистрация
    """
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


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Редактирование профиля
    """
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
    """
    Подписка
    """
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
    """
    Отписка
    """
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


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    """
    Написание поста
    """
    form = NewPostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Пост опубликован.')
        return redirect(url_for('index'))
    return render_template('new_post.html', title='Написать пост', form=form)


@app.route('/user/<username>/resume')
@login_required
def resume(username):
    """
    Страница с личными резюме пользователя
    """
    user = User.query.filter_by(username=username).first_or_404()
    resume = Resume.query.filter_by(user_id=user.id).all()
    return render_template('resume.html', user=user, resume=resume, title='Резюме')


@app.route('/resume/<res_id>')
@login_required
def this_resume(res_id):
    """
    Страница редактирования конкретного резюме пользователя
    """
    resume_c = Resume.query.filter_by(id=res_id).first_or_404()
    return render_template('this_resume.html', resume_с=resume_c, title='Резюме')


@app.route('/resume_create', methods=['GET', 'POST'])
@login_required
def resume_create():
    """
    Создание резюме (основная информация)
    """
    form = ResumeForm()
    if form.validate_on_submit():
        c_resume = Resume(
            first_name=form.first_name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            user_id=current_user.id
        )
        db.session.add(c_resume)
        db.session.commit()
        flash('Новое резюме создано!')
        return redirect(url_for('this_resume', res_id=c_resume.id))
    return render_template('resume_create.html', title='Основная информация', form=form)


@app.route('/<resume_id>/edit_resume', methods=['GET', 'POST'])
@login_required
def edit_resume(resume_id):
    """
    Редактирование рзюме (основной информации)
    """
    form = ResumeForm()
    resume = Resume.query.filter_by(id=resume_id).first_or_404()
    if form.validate_on_submit():
        resume.first_name = form.first_name.data
        resume.surname = form.surname.data
        resume.patronymic = form.patronymic.data
        resume.date_of_birth = form.date_of_birth.data
        resume.gender = form.gender.data
        db.session.commit()
        flash('Основная информация отредактирована.')
        return redirect(url_for('this_resume', res_id=resume.id))
    elif request.method == 'GET':
        form.first_name.data = resume.first_name
        form.surname.data = resume.surname
        form.patronymic.data = resume.patronymic
        form.date_of_birth.data = resume.date_of_birth
        form.gender.data = resume.gender
    return render_template('resume_create.html', title='Основная информация', form=form)


@app.route('/<resume_id>/personal_information', methods=['GET', 'POST'])
@login_required
def personal_information(resume_id):
    """
    Добавление персоналной информации
    """
    form = PersonalInformationForm()
    if form.validate_on_submit():
        person_inform = BasicInformation(
            city_of_residence=form.city_of_residence.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            about_me=form.about_me.data,
            knowledge_languages=form.knowledge_languages.data,
            citizenship=form.citizenship.data,
            resume_id=resume_id
        )
        db.session.add(person_inform)
        db.session.commit()
        flash('Персональная информация заполнена!')
        return redirect(url_for('this_resume', res_id=resume_id))
    return render_template('personal_information.html', title='Персональная информация', form=form)


@app.route('/<resume_id>/edit_personal_information', methods=['GET', 'POST'])
@login_required
def edit_personal_information(resume_id):
    """
    Редактирование персональной информации
    """
    form = PersonalInformationForm()
    person_inform = BasicInformation.query.filter_by(resume_id=resume_id).first_or_404()
    if form.validate_on_submit():
        person_inform.city_of_residence = form.city_of_residence.data
        person_inform.phone_number = form.phone_number.data
        person_inform.email = form.email.data
        person_inform.about_me = form.about_me.data
        person_inform.knowledge_languages = form.knowledge_languages.data
        person_inform.citizenship = form.citizenship.data
        db.session.commit()
        flash('Персональная информация изменена.')
        return redirect(url_for('this_resume', res_id=resume_id))
    elif request.method == 'GET':
        form.city_of_residence.data = person_inform.city_of_residence
        form.phone_number.data = person_inform.phone_number
        form.email.data = person_inform.email
        form.about_me.data = person_inform.about_me
        form.knowledge_languages.data = person_inform.knowledge_languages
        form.citizenship.data = person_inform.citizenship
    return render_template('personal_information.html', title='Персональная информация', form=form)


@app.route('/<resume_id>/edit_position', methods=['GET', 'POST'])
@login_required
def edit_position(resume_id):
    """
    Редактирование желаемой позиции
    """
    form = PositionForm()
    person_inform = BasicInformation.query.filter_by(resume_id=resume_id).first_or_404()
    if form.validate_on_submit():
        person_inform.desired_position = form.desired_position.data
        person_inform.professional_area = form.professional_area.data
        person_inform.salary = form.salary.data
        person_inform.employment = form.employment.data
        person_inform.work_schedule = form.work_schedule.data
        db.session.commit()
        flash('Готово')
        return redirect(url_for('this_resume', res_id=resume_id))
    elif request.method == 'GET':
        form.desired_position.data = person_inform.desired_position
        form.professional_area.data = person_inform.professional_area
        form.salary.data = person_inform.salary
        form.employment.data = person_inform.employment
        form.work_schedule.data = person_inform.work_schedule
    return render_template('edit_position.html', title='Желаемая позиция', form=form)


@app.route('/<resume_id>/<basic_information_id>/social_network', methods=['GET', 'POST'])
@login_required
def social_network(basic_information_id, resume_id):
    """
    Добавление соц сети, ссылки на нее и описание
    """
    form = SocialNetworkForm()
    if form.validate_on_submit():
        soc_net = SocialNetwork(
            link_social_network=form.link_social_network.data,
            comment_link_social_network=form.comment_link_social_network.data,
            basic_information_id=basic_information_id
        )
        db.session.add(soc_net)
        db.session.commit()
        flash('Опыт работы сохранен.')
        return redirect(url_for('this_resume', res_id=resume_id))
    return render_template('social_network.html', title='Соц. сеть', form=form)


@app.route('/<resume_id>/<social_network_id>/edit_social_network', methods=['GET', 'POST'])
@login_required
def edit_social_network(social_network_id, resume_id):
    """
    Редактирование соц сети, ссылки на нее и описание
    """
    form = SocialNetworkForm()
    soc_net = SocialNetwork.query.filter_by(id=social_network_id).first_or_404()
    if form.validate_on_submit():
        soc_net.link_social_network = form.link_social_network.data
        soc_net.comment_link_social_network = form.comment_link_social_network.data
        db.session.commit()
        flash('Ссылка на соц. сеть изменена.')
        return redirect(url_for('this_resume', res_id=resume_id))
    elif request.method == 'GET':
        form.link_social_network.data = soc_net.link_social_network
        form.comment_link_social_network.data = soc_net.comment_link_social_network
    return render_template('social_network.html', title='Соц. сеть', form=form)


@app.route('/<resume_id>/<basic_information_id>/key_skill', methods=['GET', 'POST'])
@login_required
def key_skills(basic_information_id, resume_id):
    """
    Добавление ключевого навыка
    """
    form = KeySkillsForm()
    if form.validate_on_submit():
        key_skill = KeySkills(
            skill_tag=form.skill_tag.data,
            basic_information_id=basic_information_id
        )
        db.session.add(key_skill)
        db.session.commit()
        flash('Ключевой навык добавлен.')
        return redirect(url_for('this_resume', res_id=resume_id))
    return render_template('key_skill.html', title='Ключевой навык', form=form)


@app.route('/<resume_id>/<key_skill_id>/edit_key_skill', methods=['GET', 'POST'])
@login_required
def edit_key_skills(key_skill_id, resume_id):
    """
    Редактирование ключевого навыка
    """
    form = KeySkillsForm()
    key_skill = KeySkills.query.filter_by(id=key_skill_id).first_or_404()
    if form.validate_on_submit():
        key_skill.skill_tag = form.skill_tag.data
        db.session.commit()
        flash('Ключевой навык изменен.')
        return redirect(url_for('this_resume', res_id=resume_id))
    elif request.method == 'GET':
        form.skill_tag.data = key_skill.skill_tag
    return render_template('key_skill.html', title='Ключевой навык', form=form)


@app.route('/<resume_id>/work_experience', methods=['GET', 'POST'])
@login_required
def work_experience(resume_id):
    """
    Добавление опыта работы
    """
    form = WorkExperienceForm()
    if form.validate_on_submit():
        work_exp = WorkExperience(
            started_working=form.started_working.data,
            ending=form.ending.data,
            organization=form.organization.data,
            region=form.region.data,
            company_field_activity=form.company_field_activity.data,
            post=form.post.data,
            responsibilities_workplace=form.responsibilities_workplace.data,
            resume_id=resume_id
        )
        db.session.add(work_exp)
        db.session.commit()
        flash('Опыт работы заполнен.')
        return redirect(url_for('this_resume', res_id=resume_id))
    return render_template('work_experience.html', title='Опыт работы', form=form)


@app.route('/<resume_id>/<work_id>/edit_work_experience', methods=['GET', 'POST'])
@login_required
def edit_work_experience(resume_id, work_id):
    """
    Редактирование персональной информации
    """
    form = WorkExperienceForm()
    work_exp = WorkExperience.query.filter_by(id=work_id).first_or_404()
    if form.validate_on_submit():
        work_exp.started_working = form.started_working.data
        work_exp.ending = form.ending.data
        work_exp.organization = form.organization.data
        work_exp.region = form.region.data
        work_exp.company_field_activity = form.company_field_activity.data
        work_exp.post = form.post.data
        work_exp.responsibilities_workplace = form.responsibilities_workplace.data
        db.session.commit()
        flash('Опыт работы изменен.')
        return redirect(url_for('this_resume', res_id=resume_id))
    elif request.method == 'GET':
        form.started_working.data = work_exp.started_working
        form.ending.data = work_exp.ending
        form.organization.data = work_exp.organization
        form.region.data = work_exp.region
        form.company_field_activity.data = work_exp.company_field_activity
        form.post.data = work_exp.post
        form.responsibilities_workplace.data = work_exp.responsibilities_workplace
    return render_template('work_experience.html', title='Опыт работы', form=form)


@app.route('/<resume_id>/education', methods=['GET', 'POST'])
@login_required
def education(resume_id):
    """
    Добавление образования
    """
    form = EducationForm()
    if form.validate_on_submit():
        training = Education(
            level=form.level.data,
            educational_institution=form.educational_institution.data,
            faculty=form.faculty.data,
            specialization=form.specialization.data,
            year_completion=form.year_completion.data,
            resume_id=resume_id
        )
        db.session.add(training)
        db.session.commit()
        flash('Образование заполнено.')
        return redirect(url_for('this_resume', res_id=resume_id))
    return render_template('education.html', title='Образование', form=form)


@app.route('/<resume_id>/<education_id>/edit_education', methods=['GET', 'POST'])
@login_required
def edit_education(resume_id, education_id):
    """
    Редактирование образования
    """
    form = EducationForm()
    training = Education.query.filter_by(id=education_id).first_or_404()
    if form.validate_on_submit():
        training.level = form.level.data
        training.educational_institution = form.educational_institution.data
        training.faculty = form.faculty.data
        training.specialization = form.specialization.data
        training.year_completion = form.year_completion.data
        db.session.commit()
        flash('Образвание изменено.')
        return redirect(url_for('this_resume', res_id=resume_id))
    elif request.method == 'GET':
        form.level.data = training.level
        form.educational_institution.data = training.educational_institution
        form.faculty.data = training.faculty
        form.specialization.data = training.specialization
        form.year_completion.data = training.year_completion
    return render_template('education.html', title='Опыт работы', form=form)


@app.route('/<resume_id>/additional_education', methods=['GET', 'POST'])
@login_required
def additional_education(resume_id):
    """
    Добавление доп. образования
    """
    form = AdditionalEducationForm()
    if form.validate_on_submit():
        training = AdditionalEducation(
            conducting_organization=form.conducting_organization.data,
            specialization=form.specialization.data,
            year_completion=form.year_completion.data,
            comment=form.comment.data,
            resume_id=resume_id
        )
        db.session.add(training)
        db.session.commit()
        flash('Доп. образование заполнено.')
        return redirect(url_for('this_resume', res_id=resume_id))
    return render_template('additional_education.html', title='Доп. образование', form=form)


@app.route('/<resume_id>/<additional_education_id>/edit_additional_education', methods=['GET', 'POST'])
@login_required
def edit_additional_education(resume_id, additional_education_id):
    """
    Редактирование доп. образования
    """
    form = AdditionalEducationForm()
    training = AdditionalEducation.query.filter_by(id=additional_education_id).first_or_404()
    if form.validate_on_submit():
        training.conducting_organization = form.conducting_organization.data
        training.specialization = form.specialization.data
        training.year_completion = form.year_completion.data
        training.comment = form.comment.data
        db.session.commit()
        flash('Доп. образование изменено.')
        return redirect(url_for('this_resume', res_id=resume_id))
    elif request.method == 'GET':
        form.conducting_organization.data = training.conducting_organization
        form.specialization.data = training.specialization
        form.year_completion.data = training.year_completion
        form.comment.data = training.comment
    return render_template('additional_education.html', title='Доп. образование', form=form)
