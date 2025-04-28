import os


def photo_func():
    kol = 1
    photo_list = []
    images = []
    main_flies = ''
    listik = []
    path = './static/image/album'
    files_and_folders = os.listdir(path)
    for item in files_and_folders:
        files = os.listdir('./static/image/album/' + item)
        for itme_2 in files:
            if itme_2 == 'file':
                files_2 = os.listdir('./static/image/album/' + item + '/' + itme_2)
                for item_3 in files_2:
                    photo_slovar = {'filename': item_3}
                    photo_list.append(photo_slovar)
            else:
                main_flies = itme_2
        slovarik = {'filename': main_flies, 'description': item, 'id': kol, 'file': photo_list}
        photo_list = []
        kol += 1
        images.append(slovarik)
    return images



def shop_func():
    kol = 1
    shops = []
    path = './static/image/products'
    files_and_folders = os.listdir(path)
    for item in files_and_folders:
        item_1 = item
        item = item.split('_')
        price = item[1].split('.')
        slovar = {"id": kol, "name": item[0], "price": price[0], "image": item_1}
        kol += 1
        shops.append(slovar)

    return shops


def news():
    kol = 3
    news_list = [
        {"title": "МЯЧИ MiKASA", "image": "реклама.jpg", "date": '01.02.2020', 'id': 1,
         'link': '/shop'},
        {"title": "Золотая серия 2025",
         "image": "серия.jpg", "date": '01.02.2020', 'id': 2,
         'link': '/tournaments'},
    ]
    with open('static/files/news.txt', 'r', encoding='utf-8') as f:
        lines = [line for line in f]
    for x in lines:
        x = x.split('*')
        if len(x) != 0:
            slovar = {"title": x[0],
             "image": x[2].replace('\n', ''), "date": x[3], 'id': kol,
             'link': x[1]}
            news_list.append(slovar)
            kol += 1
    return news_list


def tournamets():
    tornument = []
    with open('static/files/tournament.txt', 'r', encoding='utf-8') as f:
        lines = [line for line in f]
    for x in lines:
        x = x.split('*')
        if len(x) != 0:
            slovar = {'time': x[1], 'name': x[0], 'link': x[2]}
            tornument.append(slovar)
    return tornument



