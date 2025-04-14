from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, session
from pyexpat.errors import messages
from flask_mail import Mail, Message
from all_data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from all_data.user import User
from forms.users.login import LoginForm
from forms.users.register_first import RegisterFormFirst
from forms.users.register_second import RegisterFormSecond
from forms.users.register_final import RegisterFormFinal
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
        return render_template('album.html', images=images, title='Альбомы')
    return redirect('/login')


@app.route('/album/photo')
def photo():
    if current_user.is_authenticated:
        return render_template('photo.html', images_2=images_2, title='Фотографии')
    return redirect('/login')


@login_m.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
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
            user.friends = '2'

            db_sess.add(user)
            db_sess.commit()

            user_new_vec = db_sess.query(User).filter(User.id == 2).first()
            user_new_vec.friends += f', {user.id}'
            db_sess.commit()

            login_user(user, remember=True)
            session['regist_1'].clear()
            session['regist_2'].clear()

            mkdir(f'./static/users/{user.id}')
            mkdir(f'./static/users/{user.id}/image_on_profile')

            src_path = f'./static/users/guest.png'
            dst_path = f'./static/users/{user.id}/avatar.png'
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
        friends = db_sess.query(User).filter(User.id.in_(friends)).all()

        mypath = f'./static/users/{user.id}/image_on_profile/'
        new_path = f'./../static/users/{user.id}/image_on_profile/'
        new_paths = [new_path + f for f in listdir(mypath) if isfile(join(mypath, f))]
        new_paths = sorted(new_paths, key=lambda x: int(x.split('/')[-1][4:-4]))[::-1]

        if current_user.id == id:
            return render_template('profile_my.html', title='Мой профиль', friends=friends, user=user,
                                   img=new_paths, q_f=str(len(friends)))
        else:

            return render_template('profile_my.html', title=f'{user.name} {user.surname}', friends=friends,
                                   img=new_paths, user=user, q_f=str(len(friends)))
    return redirect('/login')


@app.route('/tournaments', methods=['GET', 'POST'])
def tournaments():
    if current_user.is_authenticated:
        admin = True if current_user.status == 'admin' or current_user.status == '143' else False
        return render_template('tournaments.html', title='Турниры', admin=admin, images_2=images_2)
    return redirect('/login')


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        my_friends =  db_sess.query(User).filter(User.id == current_user.id).first()
        my_friends = list(map(int, my_friends.friends.split(', ')))
        users = [user for user in users if user.id != current_user.id and user.id not in my_friends]
        return render_template('friends.html', title='Все пользователи', users=users)

    return redirect('/login')


def main():
    db_session.global_init('db/main.db')
    app.run()


if __name__ == '__main__':
    main()
