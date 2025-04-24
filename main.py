import os

from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, session, flash, url_for
from werkzeug.utils import secure_filename
from pyexpat.errors import messages
from flask_mail import Mail, Message
from all_data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from all_data.user import User
from all_data.tournament import Tournament
from all_data.league import League
from forms.users.login import LoginForm
from forms.users.register_first import RegisterFormFirst
from forms.users.register_second import RegisterFormSecond
from forms.users.register_final import RegisterFormFinal
from forms.tournaments.create_tournament import CreateTournamentForm
from forms.tournaments.create_league import CreateLeagueForm
from forms.users.edit import EditForm
from forms.tournaments.edit import EditTournamentForm
from all_consts import MY_EMAIL, MY_PASSWORD
from random import randint
import datetime as dt
from os import listdir, mkdir
from os.path import isfile, join
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex'
login_m = LoginManager()
login_m.init_app(app)

app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = MY_EMAIL
app.config['MAIL_PASSWORD'] = MY_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
          'Jul': '07', 'Aug': '08', 'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}


@app.route('/')
def index():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
            return render_template('base.html', notifications=f, len_notifications=len(f))
    else:
        return render_template('base.html')


images = [
    {'filename': 'cat_1.jpg', 'description': 'Фотография 1'},
    {'filename': 'cat_2.jpg', 'description': 'Фотография 2'},
    {'filename': 'cat_3.jpg', 'description': 'Фотография 2'},
    {'filename': 'cat_6.jpg', 'description': 'Фотография 4'},
    {'filename': 'cat_5.jpg', 'description': 'Фотография 5'},
]

images_2 = [
    {'filename': 'cat_1.jpg', 'description': 'Фотография 1'},
    {'filename': 'cat_2.jpg', 'description': 'Фотография 2'},
    {'filename': 'cat_3.jpg', 'description': 'Фотография 2'},
    {'filename': 'cat_6.jpg', 'description': 'Фотография 4'},
    {'filename': 'cat_5.jpg', 'description': 'Фотография 5'},
]


@app.route('/album')
def album():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        return render_template('album.html', images=images, title='Альбомы', notifications=f, len_notifications=len(f))
    return redirect('/login')


@app.route('/album/photo')
def photo():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        return render_template('photo.html', images_2=images_2, title='Фотографии', notifications=f,
                               len_notifications=len(f))
    return redirect('/login')


@login_m.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/')
        elif not user:
            return render_template('login.html', form=form, message='Почты не существует!',
                                   title='Авторизация')
        else:
            return render_template('login.html', form=form, message='Неправильный пароль!',
                                   title='Авторизация')
    return render_template('login.html', form=form, title='Авторизация')


@app.route('/register_first', methods=['GET', 'POST'])
def register_first():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterFormFirst()
    if form.validate_on_submit():
        surname = form.surname.data
        name = form.name.data
        date_bir = form.date_of_birth.data
        gender = form.gender.data
        session['regist_1'] = [surname, name, date_bir, gender]
        return redirect('/register_second')
    return render_template('register_first.html', title='Регистрация', form=form)


@app.route('/register_second', methods=['GET', 'POST'])
def register_second():
    if current_user.is_authenticated:
        return redirect('/')
    if 'regist_1' not in session or len(session['regist_1']) != 4:
        return redirect('/register_first')
    form = RegisterFormSecond()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_second.html', title='Регистрация', form=form,
                                   message='Почта уже занята!')
        if form.password.data != form.password_again.data:
            return render_template('register_second.html', title='Регистрация', form=form,
                                   message='Пароли не совпадают!')
        session['regist_2'] = (session['regist_1'] + [form.email.data, form.password.data] +
                               [randint(100000, 999999)])
        return redirect('/push_message')
    return render_template('register_second.html', title='Регистрация', form=form)


@app.route('/push_message', methods=['GET', 'POST'])
def push_message():
    if current_user.is_authenticated:
        return redirect('/')
    if 'regist_2' in session and len(session['regist_2']) == 7:
        name = session['regist_2'][1]
        email = session['regist_2'][4]
        n = session['regist_2'][6]
        message = Message('Подтверждение почты от ВК "Новый Век".', sender=MY_EMAIL, recipients=[email])
        message.body = f'Привет, {name}!\nВот твой код подтверждения: {n}'
        mail.send(message)
        return redirect('/register_final')
    return redirect('/register_first')


@app.route('/register_final', methods=['GET', 'POST'])
def register_final():
    if current_user.is_authenticated:
        return redirect('/')
    if 'regist_2' not in session or len(session['regist_2']) != 7:
        return redirect('/register_first')

    surname = session['regist_2'][0]
    name = session['regist_2'][1]
    date = session['regist_2'][2]
    gender = session['regist_2'][3]
    email = session['regist_2'][4]
    password = session['regist_2'][5]
    n = session['regist_2'][6]

    date = f'{date.split()[1]}.{months[date.split()[2]]}.{date.split()[3]}'
    date = dt.datetime.strptime(date, '%d.%m.%Y')

    form = RegisterFormFinal()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        code = form.code.data
        if int(code) == n:
            user = User(surname=surname, name=name, date_of_birth=date, gender=gender, email=email)
            user.set_password(password)
            user.friends = '1'

            db_sess.add(user)
            db_sess.commit()

            user_new_vec = db_sess.query(User).filter(User.id == 1).first()
            user_new_vec.friends += f', {user.id}'
            db_sess.commit()

            login_user(user, remember=True)
            session['regist_1'].clear()
            session['regist_2'].clear()

            mkdir(f'./static/users/{user.id}')
            mkdir(f'./static/users/{user.id}/image_on_profile')

            file = open("notifications.txt", "w")
            file.close()
            os.replace('notifications.txt', f'./static/users/{user.id}/notifications.txt')

            file = open("application.txt", "w")
            file.close()
            os.replace('application.txt', f'./static/users/{user.id}/application.txt')

            src_path = f'./static/users/guest.png'
            dst_path = f'./static/users/{user.id}/avatar.png'
            shutil.copy(src_path, dst_path)

            src_path = f'./static/users/background.png'
            dst_path = f'./static/users/{user.id}/background.png'
            shutil.copy(src_path, dst_path)

            src_path = f'./static/users/standart_img.png'
            dst_path = f'./static/users/{user.id}/image_on_profile/img_1.png'
            shutil.copy(src_path, dst_path)

            return redirect('/')
        return render_template('register_final.html', title='Подтверждение', form=form, message='Неверный код!')
    return render_template('register_final.html', title='Подтверждение', form=form)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(User.id == id).first()
        friends = user.friends.split(', ')
        friends = friends if friends != [''] else []
        friends = list(map(int, friends))
        friends = db_sess.query(User).filter(User.id.in_(friends)).all()[::-1]

        mypath = f'./static/users/{user.id}/image_on_profile/'
        new_path = f'./../static/users/{user.id}/image_on_profile/'
        new_paths = [new_path + f for f in listdir(mypath) if isfile(join(mypath, f))]
        new_paths = sorted(new_paths, key=lambda x: int(x.split('/')[-1][4:-4]))[::-1]

        status = 'Администратор' if user.status == 'admin' else 'Игрок'

        if current_user.id == id:
            return render_template('profile_my.html', title='Мой профиль', friends=friends, user=user,
                                   img=new_paths, q_f=str(len(friends)), status=status)
        else:
            my_friends = db_sess.query(User).filter(User.id == current_user.id).first().friends
            is_my_friend = False if user.id in map(int, my_friends.split(', ')) else True
            with open(f'./static/users/{user.id}/notifications.txt', 'r') as file:
                file = [i.strip() for i in file.readlines()]
            with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as file_2:
                file_2 = [i.strip() for i in file_2.readlines()]
            is_send = f'add {current_user.id}' in file or f'add {user.id}' in file_2
            return render_template('profile.html', title=f'{user.name} {user.surname}', friends=friends,
                                   img=new_paths, user=user, q_f=str(len(friends)), is_my_friend=is_my_friend,
                                   is_send=is_send, status=status)
    return redirect('/login')


@app.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    if current_user.is_authenticated:
        if current_user.id == id:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == id).first()
            form = EditForm(name=user.name, surname=user.surname)

            if form.validate_on_submit():
                surname = form.surname.data
                name = form.name.data

                avatar = request.files['avatar']
                if avatar:
                    avatar.save(os.path.join(f'./static/users/{user.id}', 'avatar.png'))

                background = request.files['background']
                if background:
                    background.save(os.path.join(f'./static/users/{user.id}', 'background.png'))

                user.name = name
                user.surname = surname
                db_sess.commit()

                return redirect(f'/profile/{user.id}')

            return render_template('edit_profile.html', title='Редактировать профиль', user=user, form=form)

        return redirect(f'/edit_profile/{current_user.id}')
    return redirect('/login')


@app.route('/edit_tournament/<int:id>', methods=['GET', 'POST'])
def edit_tournament(id):
    if current_user.is_authenticated:
        if current_user.status == 'admin':
            db_sess = db_session.create_session()
            tournament = db_sess.query(Tournament).filter(Tournament.id == id).first()

            form = EditTournamentForm(name=tournament.name_tournament, quantity=tournament.league_group_quantity,
                                      start_registration=tournament.start_registration,
                                      end_registration=tournament.end_registration,
                                      start_tournament=tournament.start_tournament,
                                      end_tournament=tournament.end_tournament, is_visible=tournament.is_visible,
                                      is_register=tournament.is_register)
            if form.validate_on_submit():
                q = tournament.league_group_quantity

                tournament.name_tournament = form.name.data
                tournament.league_group_quantity = form.quantity.data
                tournament.start_registration = form.start_registration.data
                tournament.end_registration = form.end_registration.data
                tournament.start_tournament = form.start_tournament.data
                tournament.end_tournament = form.end_tournament.data
                tournament.is_visible = form.is_visible.data
                tournament.is_register = form.is_register.data

                if tournament.end_tournament < tournament.start_tournament:
                    return render_template('edit_tournament.html', title='Редактировать турнир', form=form,
                                           message='Введите другую дату турнира!')

                if tournament.end_registration < tournament.start_registration:
                    return render_template('edit_tournament.html', title='Редактировать турнир', form=form,
                                           message='Введите другую дату регистрации!')

                if tournament.type == 'lm' and tournament.quantity > 3:
                    return render_template('edit_tournament.html', title='Редактировать турнир', form=form,
                                           message='Слишком много лиг!')

                if tournament.league_group_quantity < q:
                    return render_template('edit_tournament.html', title='Редактировать турнир', form=form,
                                           message='Количество лиг не может быть меньше!')

                db_sess.commit()

                return redirect('/tournaments')

            return render_template('edit_tournament.html', title='Редактировать турнир', form=form)

        return redirect(f'/tournaments')
    return redirect('/login')


@app.route('/add_friends/<int:id_my>/<int:id_friend>', methods=['GET', 'POST'])
def add_friends(id_my, id_friend):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.id == id_my:
        with open(f'./static/users/{id_friend}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        with open(f'./static/users/{id_friend}/notifications.txt', 'w') as file:
            for i in f:
                file.write(i + '\n')
            file.write(f'add {id_my}' + '\n')
    return redirect(request.referrer)


@app.route('/perform_add_friend/<int:id_my>/<int:id_friend>/<int:loop_index>', methods=['GET', 'POST'])
def perform_add_friend(id_my, id_friend, loop_index):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.id == id_friend:
        db_sess = db_session.create_session()
        user_1 = db_sess.query(User).filter(User.id == id_my).first()
        user_2 = db_sess.query(User).filter(User.id == id_friend).first()
        user_1.friends += f', {id_friend}'
        user_2.friends += f', {id_my}'
        db_sess.commit()
        with open(f"./static/users/{id_friend}/notifications.txt", "r") as f:
            lines = [i.strip() for i in f.readlines()]
        with open(f"./static/users/{id_friend}/notifications.txt", "w") as file:
            for en, line in enumerate(lines):
                if en != loop_index - 1:
                    file.write(line + '\n')
    return redirect(request.referrer)


@app.route('/cancel_add_friend/<int:id_my>/<int:id_friend>/<int:loop_index>', methods=['GET', 'POST'])
def cancel_add_friend(id_my, id_friend, loop_index):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.id == id_friend:
        with open(f"./static/users/{id_friend}/notifications.txt", "r") as f:
            lines = [i.strip() for i in f.readlines()]
        with open(f"./static/users/{id_friend}/notifications.txt", "w") as file:
            for en, line in enumerate(lines):
                if en != loop_index - 1:
                    file.write(line + '\n')
    return redirect(request.referrer)


@app.route('/invite_friend/<int:id_my>/<int:id_friend>/<int:id_league>/', methods=['GET', 'POST'])
def invite_friend(id_my, id_friend, id_league):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.id == id_my:
        with open(f'./static/users/{id_friend}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        with open(f'./static/users/{id_friend}/notifications.txt', 'w') as file:
            for i in f:
                file.write(i + '\n')
            file.write(f'invite {id_my} {id_league}' + '\n')

        with open(f'./static/users/{id_my}/application.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        with open(f'./static/users/{id_my}/application.txt', 'w') as file:
            for i in f:
                file.write(i + '\n')
            file.write(f'{id_friend} {id_league}' + '\n')

    return redirect(request.referrer)


@app.route('/perform_invite_friend/<int:id_my>/<int:id_friend>/<int:id_league>/<int:loop_index>',
           methods=['GET', 'POST'])
def perform_invite_friend(id_my, id_friend, id_league, loop_index):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user == id_friend:
        db_sess = db_session.create_session()
        league = db_sess.query(League).filter(League.id == id_league).first()
        tournament = db_sess.query(Tournament).filter(Tournament.id == league.is_tournament).first()
        if league.team is None:
            league.team = f'{id_my}_{id_friend} '
        else:
            league.team += f'{id_my}_{id_friend} '

        if league.players is None:
            league.players = f'{id_my} {id_friend} '
        else:
            league.players += f' {id_my} {id_friend}'

        if tournament.team is None:
            tournament.team = f'{id_my}_{id_friend} '
        else:
            tournament.team += f'{id_my}_{id_friend} '

        if tournament.players is None:
            tournament.players = f'{id_my} {id_friend} '
        else:
            tournament.players += f' {id_my} {id_friend}'

        db_sess.commit()
        db_sess.commit()

        with open(f'./static/users/{id_friend}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        with open(f'./static/users/{id_friend}/notifications.txt', 'w') as file:
            for en, i in enumerate(f):
                if en != loop_index - 1:
                    file.write(i + '\n')

        with open(f'./static/users/{id_my}/application.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        with open(f'./static/users/{id_my}/application.txt', 'w') as file:
            for i in f:
                if i.split()[0] == str(id_friend) and i.split()[1] == str(id_league):
                    pass
                else:
                    file.write(i + '\n')
    return redirect(request.referrer)


@app.route('/cancel_invite_friend/<int:id_my>/<int:id_friend>/<int:id_league>/<int:loop_index>',
           methods=['GET', 'POST'])
def cancel_invite_friend(id_my, id_friend, id_league, loop_index):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.id == id_friend:
        with open(f'./static/users/{id_friend}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        with open(f'./static/users/{id_friend}/notifications.txt', 'w') as file:
            for en, i in enumerate(f):
                if en != loop_index - 1:
                    file.write(i + '\n')

        with open(f'./static/users/{id_my}/application.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        with open(f'./static/users/{id_my}/application.txt', 'w') as file:
            for i in f:
                if i.split()[0] == str(id_friend) and i.split()[1] == str(id_league):
                    pass
                else:
                    file.write(i + '\n')
    return redirect(request.referrer)


@app.route('/give_admin/<int:id>', methods=['GET', 'POST'])
def give_admin(id):
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user and current_user.status == 'admin':
        user.status = 'admin'
        db_sess.commit()
    return redirect(request.referrer)


@app.route('/increase_team/<int:id>', methods=['GET', 'POST'])
def increase_team(id):
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    league = db_sess.query(League).filter(League.id == id).first()
    if league and current_user.status == 'admin':
        if league.team_quantity != 30:
            league.team_quantity += 1
            db_sess.commit()
    return redirect(request.referrer)


@app.route('/reduce_team/<int:id>', methods=['GET', 'POST'])
def reduce_team(id):
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    league = db_sess.query(League).filter(League.id == id).first()
    if league and current_user.status == 'admin':
        if league.team_quantity != 3:
            if league.team:
                if len(league.team.split()) != league.team_quantity:
                    league.team_quantity -= 1
            league.team_quantity -= 1
            db_sess.commit()
    return redirect(request.referrer)


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        my_friends = db_sess.query(User).filter(User.id == current_user.id).first()
        my_friends = list(map(int, my_friends.friends.split(', ')))
        users = [user for user in users if user.id != current_user.id and user.id not in my_friends]
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        return render_template('friends.html', title='Все пользователи', users=users, notifications=f,
                               len_notifications=len(f))

    return redirect('/login')


@app.route('/tournaments', methods=['GET', 'POST'])
def tournaments():
    if current_user.is_authenticated:
        admin = True if current_user.status == 'admin' or current_user.status == '143' else False

        db_sess = db_session.create_session()
        all_tournaments = db_sess.query(Tournament).all()[::-1]

        if not admin:
            all_tournaments = db_sess.query(Tournament).filter(Tournament.is_visible == 1).all()[::-1]
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        print(all_tournaments)
        return render_template('tournaments.html', title='Турниры', admin=admin, all_tournaments=all_tournaments,
                               notifications=f, len_notifications=len(f))
    return redirect('/login')


@app.route('/create_tournament', methods=['GET', 'POST'])
def create_tournament():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        if current_user.status == 'admin':

            form = CreateTournamentForm()
            if form.validate_on_submit():

                title = form.name.data
                quantity = form.quantity.data
                start_registration = form.start_registration.data
                end_registration = form.end_registration.data
                start_tournament = form.start_tournament.data
                end_tournament = form.end_tournament.data
                type_tournament = form.type.data
                is_visible = form.is_visible.data
                is_register = form.is_register

                is_visible = 1 if is_visible else 0
                is_register = 1 if is_register else 0

                if end_tournament < start_tournament:
                    return render_template('create_tournament.html', title='Создать турнир', form=form,
                                           message='Введите другую дату турнира!', notifications=f,
                                           len_notifications=len(f))

                if end_registration < start_registration:
                    return render_template('create_tournament.html', title='Создать турнир', form=form,
                                           message='Введите другую дату регистрации!', notifications=f,
                                           len_notifications=len(f))

                if type_tournament == 'lm' and quantity > 3:
                    return render_template('create_tournament.html', title='Создать турнир', form=form,
                                           message='Слишком много лиг!', notifications=f,
                                           len_notifications=len(f))

                tournament = Tournament(name_tournament=title, type=type_tournament, league_group_quantity=quantity,
                                        start_registration=start_registration, end_registration=end_registration,
                                        start_tournament=start_tournament, end_tournament=end_tournament,
                                        is_visible=is_visible, is_register=is_register,
                                        creator_tournament=current_user.id)

                db_sess = db_session.create_session()
                db_sess.add(tournament)
                db_sess.commit()

                if type_tournament == 'lm':
                    league = League()

                n = randint(1, 9)

                mkdir(f'./static/tournaments/{tournament.id}')

                src_path = f'./static/image/background_tournament/img_{n}.png'
                dst_path = f'./static/tournaments/{tournament.id}/img.png'
                shutil.copy(src_path, dst_path)

                return redirect('/tournaments')

            return render_template('create_tournament.html', title='Создать турнир', form=form, notifications=f,
                                   len_notifications=len(f))

        return redirect('/tournaments')
    return redirect('/login')


@app.route('/tournament_league/<int:id>', methods=['GET', 'POST'])
def tournament_league(id):
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        db_sess = db_session.create_session()

        tournament = db_sess.query(Tournament).filter(Tournament.id == id).first()
        leagues = db_sess.query(League).filter(League.is_tournament == tournament.id).all()
        if tournament.is_visible or current_user.status == 'admin':
            return render_template('tournament_league.html', title=f'Турнир {tournament.name_tournament}',
                                   tour=tournament, leagues=leagues, q_league=len(leagues), notifications=f,
                                   len_notifications=len(f))
        else:
            return redirect('/tournaments')

    return redirect('/login')


@app.route('/create_league/<int:id>', methods=['GET', 'POST'])
def create_league(id):
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        db_sess = db_session.create_session()
        tournament = db_sess.query(Tournament).filter(Tournament.id == id).first()
        if current_user.status == 'admin' and tournament:

            form = CreateLeagueForm()
            if form.validate_on_submit():
                type_league = form.type.data
                quantity = form.team_quantity.data
                level = '' if tournament.type == 'lm' else form.level.data
                leagues = db_sess.query(League).filter(League.is_tournament == tournament.id).all()
                leagues = [league.type for league in leagues]
                if type_league in leagues:
                    return render_template('create_league.html', title='Создать лигу', form=form, notifications=f,
                                           len_notifications=len(f), tournament=tournament,
                                           messages=f'Категория уже используется в этом турнире!')

                league = League(type=type_league, level=level, is_tournament=id, team_quantity=quantity)
                db_sess.add(league)
                db_sess.commit()

                return redirect(f'/tournament_league/{id}')

            return render_template('create_league.html', title='Создать лигу', form=form, notifications=f,
                                   len_notifications=len(f), tournament=tournament)

        return redirect(f'/tournament_league/{id}')
    return redirect('/login')


@app.route('/league/<int:id>', methods=['GET', 'POST'])
def league_id(id):
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        db_sess = db_session.create_session()

        league = db_sess.query(League).filter(League.id == id).first()
        tournament = db_sess.query(Tournament).filter(Tournament.id == league.is_tournament).first()

        if league and (tournament.is_visible or current_user.status == 'admin'):
            if tournament.is_started or tournament.is_finished:

                return render_template('league_start.html', title=f'Лига {league.type} {league.level}', team=league,
                                       notifications=f, len_notifications=len(f))
            elif tournament.is_register:
                teams = league.team
                new_teams = []
                if teams:
                    teams = teams.split()
                    for team in teams:
                        one, two = map(int, team.split('_'))
                        player_one = db_sess.query(User).filter(User.id == one).first()
                        player_two = db_sess.query(User).filter(User.id == two).first()
                        new_teams.append([player_one, player_two])

                friends_my = db_sess.query(User).filter(User.id == current_user.id).first().friends.split(', ')
                friends_my = db_sess.query(User).filter(User.id.in_(friends_my)).all()[1:]
                players_id = []

                if league.players is None:
                    percent = 0
                else:
                    percent = round(len(league.team.split()) / (league.team_quantity / 100))
                    friends_my = [user for user in friends_my if user.id not in map(int, league.players.split())]
                    players_id = map(int, league.players.split())

                return render_template('league_register.html', title=f'Регистрация {league.type} {league.level}',
                                       league=league, team=new_teams, q_team=len(new_teams), notifications=f,
                                       len_notifications=len(f),
                                       friends=friends_my, players_id=players_id,
                                       percent=percent)
            return redirect(f'/tournament_league/{tournament.id}')
        return redirect('/tournaments')

    return redirect('/login')


def main():
    db_session.global_init('db/main.db')
    app.run()


if __name__ == '__main__':
    main()
