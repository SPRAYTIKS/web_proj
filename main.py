import csv
from flask import Flask, render_template, redirect, request, session
from flask_mail import Mail, Message
from all_data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from all_data.user import User
from all_data.tournament import Tournament
from all_data.league import League
from all_data.group_league import GroupLeague
from forms.users.login import LoginForm
from forms.users.register_first import RegisterFormFirst
from forms.users.register_second import RegisterFormSecond
from forms.users.register_final import RegisterFormFinal
from forms.tournaments.create_tournament import CreateTournamentForm
from forms.tournaments.create_league import CreateLeagueForm
from forms.users.edit import EditForm
from forms.tournaments.edit import EditTournamentForm
from all_consts import MY_EMAIL, MY_PASSWORD, BOT_TOKEN, CHAT_ID
from random import randint
import datetime as dt
from os import listdir, mkdir
from os.path import isfile, join
import requests
from functions import shop_func, photo_func, news, tournamets
import os
import shutil
import datetime

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
listik = []
mail = Mail(app)

months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
          'Jul': '07', 'Aug': '08', 'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}


@app.route('/')
def index():
    if current_user.is_authenticated:
        news_lest = news()
        news_lest = news_lest[::-1]
        tournament = tournamets()
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
            return render_template('index.html', tournament=tournament, news_list=news_lest, notifications=f,
                                   len_notifications=len(f))
    return redirect('/login')


@app.route('/album')
def album():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
            images = photo_func()
            return render_template('album.html', status=current_user.status, images=images, notifications=f,
                                   len_notifications=len(f))
    return redirect('/login')


@app.route('/albumAdmin')
def albumAdmin():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        if current_user.status == 'admin':
            return render_template('admin_album.html', notifications=f, len_notifications=len(f))
    return redirect('/login')


@app.route('/save_album', methods=['POST'])
def save_album():
    album_name = request.form['album-name']
    main_photo = request.files['main-photo']
    photos = request.files.getlist('photos')

    path = './static/image/album'
    os.mkdir(path + '/' + album_name)
    filename = main_photo.filename
    upload_folder = './static/image/album/' + album_name
    main_photo.save(os.path.join(upload_folder, filename))

    os.mkdir(path + '/' + album_name + '/' + 'file')

    src_path = f'static/image/album/{album_name}/{filename}'
    dst_path = f'static/image/news/{filename}'
    shutil.copy(src_path, dst_path)

    name = album_name
    link = f'/album'
    path = filename
    dates = datetime.date.today()
    with open('static/files/news.txt', 'a', encoding='utf-8') as f:
        f.write(f'Создался новый альбом "{name}"*{link}*{path}*{dates}\n')

    for file in photos:
        path = 'static/image/cash'
        filename = file.filename
        upload_folder = path
        file.save(os.path.join(upload_folder, filename))

        src_path = f'static/image/cash/{file.filename}'
        dst_path = 'static/image/album/' + album_name + '/' + 'file' + '/' + file.filename
        shutil.copy(src_path, dst_path)
    return 'Альбом создан'


@app.route('/photo/<int:photo_id>')
def photo(photo_id):
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        images = photo_func()
        return render_template('photo.html', images_2=images[photo_id - 1]['file'], notifications=f,
                               len_notifications=len(f))
    return redirect('/login')


@app.route('/shop')
def shop():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
            shops = shop_func()
            return render_template('shop.html', status=current_user.status, shops=shops, notifications=f,
                                   len_notifications=len(f))
    return redirect('/login')


@app.route('/shopAdmin')
def shopAdmin():
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        if current_user.status == 'admin':
            return render_template('admin_shop.html', notifications=f, len_notifications=len(f))
    return redirect('/login')


@app.route('/add_product', methods=['POST'])
def add_product():
    photo = request.files['photo']
    name = request.form['name']
    price = request.form['price']
    upload_folder = './static/image/products'
    photo.save(os.path.join(upload_folder, photo.filename))
    raz = photo.filename.split('.')
    os.rename(upload_folder + '/' + photo.filename, upload_folder + '/' + name + '_' + price + '.' + raz[1])

    src_path = upload_folder + '/' + name + '_' + price + '.' + raz[1]
    dst_path = 'static/image/news/' + name + '_' + price + '.' + raz[1]
    shutil.copy(src_path, dst_path)

    name = name
    link = f'/shop'
    path = name + '_' + price + '.' + raz[1]
    dates = datetime.date.today()
    with open('static/files/news.txt', 'a', encoding='utf-8') as f:
        f.write(f'Появился новый товар "{name}"*{link}*{path}*{dates}\n')

    return 'Товар добавлен!'


@app.route('/buy/<int:shop_id>', methods=['GET', 'POST'])
def buy(shop_id):
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
            email = None
            shops = shop_func()
            if request.method == 'POST':
                email = request.form.get('email')
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                params = {
                    'chat_id': CHAT_ID,
                    'text': f"Новый заказ от {email}\n"
                            f"-{shops[shop_id - 1]['name']}\n"
                            f"Цена: {shops[shop_id - 1]['price']}\n"
                }
                requests.post(url=url, params=params)
            return render_template('buy.html', shop=shops[shop_id - 1], email=email, notifications=f,
                                   len_notifications=len(f))
    return redirect('/login')


@login_m.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


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
            if not tournament or tournament.is_finished or tournament.is_started:
                return redirect('/tournaments')

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

                if tournament.type == 'lm' and tournament.league_group_quantity > 3:
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
    if current_user.id == id_friend:
        db_sess = db_session.create_session()
        league = db_sess.query(League).filter(League.id == id_league).first()
        tournament = db_sess.query(Tournament).filter(Tournament.id == league.is_tournament).first()

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

        if not tournament.is_register:
            return redirect(request.referrer)
        if not league.team is None and len(league.team.split()) == league.team_quantity:
            return redirect(request.referrer)
        if (not league.team is None and
                (str(id_my) in league.players.split() or str(id_friend) in league.players.split())):
            return redirect(request.referrer)

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
        if league.team_quantity + 1 <= 32:
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
        if league.team_quantity - 1 >= 3:
            if league.team:
                if len(league.team.split()) != league.team_quantity:
                    league.team_quantity -= 1
            else:
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
            print(f)
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

                if tournament.is_visible:
                    name = tournament.name_tournament
                    link = f'/tournament_league/{tournament.id}'
                    path = f'img_{n}.png'
                    dates = datetime.date.today()

                    with open('static/files/news.txt', 'a', encoding='utf-8') as f:
                        f.write(f'Создался новый турнир "{name}"*{link}*{path}*{dates}\n')

                    with open('static/files/tournament.txt', 'a', encoding='utf-8') as file:
                        file.write(f'{name}*{dates}*{link}\n')

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
                                   len_notifications=len(f), tournament=tournament)
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
        if current_user.status == 'admin' and tournament and not tournament.is_started and not tournament.is_finished:

            form = CreateLeagueForm()
            if form.validate_on_submit():
                type_league = form.type.data
                quantity = form.team_quantity.data
                level = '' if tournament.type == 'lm' else form.level.data
                leagues = db_sess.query(League).filter(League.is_tournament == tournament.id).all()
                leagues = [league.type for league in leagues]
                if type_league in leagues:
                    print(12)
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


@app.route('/league/<int:id>/<int:id_group>', methods=['GET', 'POST'])
def league_id(id, id_group):
    if current_user.is_authenticated:
        with open(f'./static/users/{current_user.id}/notifications.txt', 'r') as f:
            f = [i.strip() for i in f.readlines()]
        db_sess = db_session.create_session()

        league = db_sess.query(League).filter(League.id == id).first()
        tournament = db_sess.query(Tournament).filter(Tournament.id == league.is_tournament).first()
        leagues = db_sess.query(League).filter(League.is_tournament == tournament.id).all()

        if league and (tournament.is_visible or current_user.status == 'admin'):
            if tournament.is_started or tournament.is_finished:
                groups = db_sess.query(GroupLeague).filter(GroupLeague.is_league == league.id).all()
                if groups:

                    group = groups[id_group]

                    with open(f'./groups/table_format/{group.players_quantity}_team.csv', 'r') as file:
                        games = []
                        for game in file:
                            game = game.strip().split(',')

                            player_1 = int(group.team.split()[int(game[2]) - 1].split('_')[0])
                            player_2 = int(group.team.split()[int(game[4]) - 1].split('_')[0])
                            referee = int(group.team.split()[int(game[5]) - 1].split('_')[0])

                            player_1 = db_sess.query(User).filter(User.id == player_1).first()
                            player_1 = f'{player_1.surname} {player_1.name[0]}.'
                            player_2 = db_sess.query(User).filter(User.id == player_2).first()
                            player_2 = f'{player_2.surname} {player_2.name[0]}.'
                            referee = db_sess.query(User).filter(User.id == referee).first()
                            referee = f'{referee.surname} {referee.name[0]}.'

                            games.append([player_1, player_2, referee])
                    admin = 'true' if current_user.status == 'admin' else 'false'

                    if request.method == 'POST':
                        if 'apply' in request.form:
                            f = request.form
                            with open(f'groups/{group.id}.csv', 'w', newline='', encoding="utf8") as csvfile:
                                writer = csv.writer(
                                    csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                for i in range(len(games)):
                                    ar = []
                                    for j in range(3):
                                        r = f[f'{i} {j}']
                                        ar.append(r)
                                    print(ar)
                                    writer.writerow(ar)
                                writer.writerow([f['format']])

                    result = []
                    with open(f'./groups/{group.id}.csv', 'r', encoding='utf-8') as file:
                        file = list(file)
                        for q in file[:-1]:
                            q = q.strip().split(',')
                            result.append(q)
                        format_game = file[-1]

                    return render_template('league_start.html', title=f'Лига {league.type} {league.level}',
                                           league=league, group=group, notifications=f, admin=admin, num=id_group,
                                           len_notifications=len(f), groups=groups, games=games, result=result,
                                           format=format_game, leagues=leagues, q_league=len(leagues))

                tournament.is_started = 0
                tournament.is_finished = 0
                db_sess.commit()
                return redirect(f'/tournament_league/{tournament.id}')

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

                register_my = True
                if league.type == 'ММ':
                    register_my = current_user.gender == 'man'
                    friends_my = [friend for friend in friends_my if friend.gender == 'man']

                elif league.type == 'ЖЖ':
                    register_my = current_user.gender == 'woman'
                    friends_my = [friend for friend in friends_my if friend.gender == 'woman']

                else:
                    my_gender = current_user.gender
                    friends_my = [friend for friend in friends_my if friend.gender != my_gender]

                players_id = []
                if league.players is None:
                    percent = 0
                else:
                    percent = round(len(league.team.split()) / (league.team_quantity / 100))
                    friends_my = [user for user in friends_my if user.id not in map(int, league.players.split())]
                    players_id = map(int, league.players.split())

                application = False
                with open(f'./static/users/{current_user.id}/application.txt', 'r') as file:
                    for i in file.readlines():
                        i = i.strip().split()
                        if int(i[1]) == league.id:
                            application = True
                            break

                max_team = False
                if len(new_teams) == league.team_quantity:
                    max_team = True

                return render_template('league_register.html', title=f'Регистрация {league.type} {league.level}',
                                       league=league, team=new_teams, q_team=len(new_teams), notifications=f,
                                       len_notifications=len(f), tournament=tournament,
                                       friends=friends_my, players_id=players_id, register_my=register_my,
                                       percent=percent, application=application, max_team=max_team)

            return redirect(f'/tournament_league/{tournament.id}')
        return redirect('/tournaments')

    return redirect('/login')


@app.route('/starting_tournament/<int:id>', methods=['GET', 'POST'])
def starting_tournament(id):
    if current_user.is_authenticated:
        if current_user.status == 'admin':
            db_sess = db_session.create_session()
            tournament = db_sess.query(Tournament).filter(Tournament.id == id).first()
            if tournament:
                leagues = db_sess.query(League).filter(League.is_tournament == id).all()
                errors = []
                if tournament.is_register:
                    errors.append('Регистрация на турнир продолжается!')
                if len(leagues) == 0:
                    errors.append('В турнире нет не одной лиги!')
                for league in leagues:
                    if league.team is None:
                        errors.append(f'В лиге {league.type} {league.level} нет команд!')
                    elif len(league.team.split()) != league.team_quantity:
                        errors.append(f'В лиге {league.type} {league.level} недостаточно команд!')

                return render_template('starting_tournament.html', tournament=tournament, title='Запуск турнира',
                                       errors=errors, len_errors=len(errors))

            return redirect('/tournaments')
        return redirect('/tournaments')
    return redirect('/login')


@app.route('/create_groups/<int:id>', methods=['GET', 'POST'])
def create_groups(id):
    if current_user.is_authenticated:
        if current_user.status == 'admin':
            db_sess = db_session.create_session()
            tournament = db_sess.query(Tournament).filter(Tournament.id == id).first()
            if tournament and not tournament.is_register:
                leagues = db_sess.query(League).filter(League.is_tournament == id).all()
                leagues_id = [league.id for league in leagues]

                groups = db_sess.query(GroupLeague).filter(GroupLeague.is_league.in_(leagues_id)).all()
                if not groups:
                    db_sess.commit()
                    q_teams = [len(league.team.split()) for league in leagues]
                    new_q = []
                    for q in q_teams:
                        arr = [6 for _ in range(q // 6)]
                        if q % 6 == 0:
                            pass
                        elif q % 6 >= 3:
                            arr.append(q % 6)
                        else:
                            arr[-1] -= (3 - q % 6)
                            arr.append(3)
                        zeros = [0 for _ in range(8 - len(arr))]
                        arr.extend(zeros)
                        new_q.append(arr)
                    sum_team = [sum(q) for q in new_q]

                    if request.method == 'POST':
                        arr = []
                        for i in range(len(new_q)):
                            ar = []
                            for j in range(8):
                                r = int(request.form[f'{i + 1} {j + 1}'])
                                ar.append(r)
                            arr.append(ar)
                        new_q = arr[:]
                        message = []
                        for q in range(len(new_q)):
                            if sum(new_q[q]) != sum_team[q]:
                                message.append(f'Распределено {sum(new_q[q])} вместо {sum_team[q]}!')
                            else:
                                message.append('1')
                        if all([i == '1' for i in message]):
                            session['create_group'] = [sorted(q)[::-1] for q in new_q]
                            session['ready'] = [0 for _ in new_q]
                            session['ready_league'] = [[] for _ in new_q]
                            session['message'] = [[] for _ in new_q]
                            return redirect(f'/distribution_team/{tournament.id}/0')

                        return render_template('create_groups.html', leagues=leagues, tournament=tournament,
                                               title='Создание групп', q_teams=new_q, messages=message)

                    return render_template('create_groups.html', leagues=leagues, tournament=tournament,
                                           title='Создание групп', q_teams=new_q, messages=['1'] * len(new_q))

        return redirect('/tournaments')
    return redirect('/login')


@app.route('/distribution_team/<int:id>/<int:num_league>', methods=['GET', 'POST'])
def distribution_team(id, num_league):
    if current_user.is_authenticated:
        if current_user.status == 'admin':
            db_sess = db_session.create_session()
            tournament = db_sess.query(Tournament).filter(Tournament.id == id).first()
            if tournament and not tournament.is_register:
                leagues = db_sess.query(League).filter(League.is_tournament == id).all()
                leagues_id = [league.id for league in leagues]

                groups = db_sess.query(GroupLeague).filter(GroupLeague.is_league.in_(leagues_id)).all()

                if not groups and 'create_group' in session and 'ready' in session and 'ready_league' in session:
                    teams = [i.team_quantity for i in leagues]
                    if (len(teams) == len(session['create_group']) and len(teams) == len(session['ready']) and len(
                            teams) == len(session['ready_league']) and
                            all([teams[i] == sum(session['create_group'][i]) for i in range(len(teams))])):

                        league = leagues[num_league]
                        teams = [' / '.join([db_sess.query(User).filter(User.id == int(j)).first().surname
                                             for j in i.split('_')])
                                 for i in league.team.split()]
                        all_teams = teams[:]
                        if session['ready_league'][num_league]:
                            all_teams = session['ready_league'][num_league][:]
                        if request.method == 'POST':
                            f = request.form
                            if 'name' in f and all(session['ready']):
                                for en, league in enumerate(session['ready_league']):
                                    for en_b, q in enumerate(session['create_group'][en]):
                                        if q == 0:
                                            continue
                                        teams = league[:q]
                                        qe = q
                                        teams_db = (
                                            db_sess.query(League).filter(League.id == leagues[en].id).first().team)
                                        d_teams = {}

                                        for team in teams_db.split():
                                            team = list(map(int, team.split('_')))

                                            user_1 = db_sess.query(User).filter(User.id == team[0]).first()
                                            user_2 = db_sess.query(User).filter(User.id == team[1]).first()

                                            d_teams[f'{user_1.surname} / {user_2.surname}'] = \
                                                f'{user_1.id}_{user_2.id}'
                                        teams_id = [d_teams[team] for team in teams]
                                        players_id = ' '.join([' '.join(team.split('_')) for team in teams_id])
                                        teams_id = ' '.join(teams_id)
                                        group = GroupLeague(name=f'Группа {"АБВГДЕЖЗ"[en_b]}', players=players_id,
                                                            team=teams_id, is_league=leagues[en].id,
                                                            players_quantity=len(teams_id.split()))
                                        db_sess.add(group)
                                        db_sess.commit()

                                        with open(f'{group.id}.csv', 'w', newline='', encoding="utf8") as csvfile:
                                            writer = csv.writer(
                                                csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                            if group.players_quantity == 3:
                                                q = 3
                                            elif group.players_quantity == 4:
                                                q = 6
                                            elif group.players_quantity == 5:
                                                q = 10
                                            else:
                                                q = 15
                                            for i in range(q):
                                                writer.writerow(['', '', ''])
                                            writer.writerow(['Формат: '])

                                        src_path = f'{group.id}.csv'
                                        dst_path = f'groups'
                                        shutil.move(src_path, dst_path)

                                        league = league[qe:]
                                tournament.is_started = True
                                db_sess.commit()
                                return redirect(f'/tournament_league/{tournament.id}')

                            elif 'apply' in f:
                                arr = []
                                for en, group in enumerate(session['create_group'][num_league]):
                                    ar = []
                                    for i in range(group):
                                        r = f[f'{en} {i}']
                                        arr.append(r)
                                copy_teams = teams[:]
                                repeat_teams = []
                                for team in arr:
                                    team = team.strip()
                                    if team in copy_teams:
                                        copy_teams.remove(team)
                                    else:
                                        repeat_teams.append(team)
                                all_teams = arr[:]
                                session.modified = True
                                session['ready_league'][num_league] = all_teams[:]
                                if repeat_teams:
                                    session['ready'][num_league] = 0
                                    session['message'][num_league] = repeat_teams
                                else:
                                    session['message'][num_league] = []
                                    session['ready'][num_league] = 1

                        ar_d = []
                        for en, group in enumerate(session['create_group'][num_league]):
                            if en == 0:
                                q = 0
                            else:
                                q = sum(session['create_group'][num_league][:en])
                            ar_d.append(q)
                        return render_template('distribution_team.html', tournament=tournament,
                                               ready=session['ready'], all_teams=all_teams, teams=teams,
                                               title=f'Распределение команд {league.type} {league.level}',
                                               leagues=leagues, num=num_league, league_my=league,
                                               distribution=session['create_group'][num_league], name_group='АБВГДЕЖЗ',
                                               message=session['message'][num_league], sum_d=ar_d)

        return redirect('/tournaments')
    return redirect('/login')


def main():
    db_session.global_init('db/main.db')
    app.run()


if __name__ == '__main__':
    main()
