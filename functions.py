import os


def photo_func():
    kol = 1
    photo_list = []
    images = []
    main_flies = ''
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
    print(images)
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