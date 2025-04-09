from flask import Flask, render_template


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex'


@app.route('/')
def index():
    return render_template('base.html')


images = [
    {'filename': 'cat_1.jpg', 'description': 'Фотография 1'},
    {'filename': 'cat_2.jpg', 'description': 'Фотография 2'},
    {'filename': 'cat_3.jpg', 'description': 'Фотография 3'},
    {'filename': 'cat_6.jpg', 'description': 'Фотография 4'},
    {'filename': 'cat_5.jpg', 'description': 'Фотография 5'},
]

images_2 = [
    {'filename': 'cat_1.jpg', 'description': 'Фотография 1'},
    {'filename': 'cat_2.jpg', 'description': 'Фотография 2'},
    {'filename': 'cat_3.jpg', 'description': 'Фотография 3'},
    {'filename': 'cat_6.jpg', 'description': 'Фотография 4'},
    {'filename': 'cat_5.jpg', 'description': 'Фотография 5'},
]


@app.route('/album')
def album():
    return render_template('album.html', images=images)


@app.route('/album/photo')
def photo():
    return render_template('photo.html', images_2=images_2)



def main():
    app.run()


if __name__ == '__main__':
    main()