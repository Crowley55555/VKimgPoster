def vk_post_with_image(arguments):
    import requests

    access_token = arguments['access_token']
    image_url = arguments['image_url']
    message = arguments.get('message', '')
    group_id = arguments['group_id']

    headers = {'User-Agent': 'VK-Poster/1.0'}

    # 1. Получаем upload server
    upload_resp = requests.get(
        'https://api.vk.com/method/photos.getWallUploadServer',
        params={
            'access_token': access_token,
            'v': '5.199',
            'group_id': group_id
        },
        timeout=10
    ).json()

    if 'error' in upload_resp:
        err = upload_resp['error']
        code = err.get('error_code')
        if code == 15:
            raise Exception("Ошибка доступа: токен не имеет прав на запись в группу. Убедитесь, что вы — администратор и токен имеет права wall и photos.")
        elif code == 27:
            raise Exception("Ошибка авторизации: метод недоступен с токеном группы. Используйте пользовательский токен администратора.")
        else:
            raise Exception(f"Ошибка получения upload-сервера [{code}]: {err.get('error_msg', 'Неизвестная ошибка')}")

    upload_url = upload_resp['response']['upload_url']

    # 2. Загружаем изображение по URL с проверкой типа
    img_response = requests.get(image_url, headers=headers, timeout=10)
    if img_response.status_code != 200:
        raise Exception(f"Не удалось загрузить изображение: HTTP {img_response.status_code} по адресу {image_url}")

    content_type = img_response.headers.get('content-type', '').lower()
    if not content_type.startswith('image/'):
        raise Exception(f"URL не возвращает изображение. Получен Content-Type: {content_type}")

    # 3. Отправляем фото на сервер ВК
    upload_result = requests.post(
        upload_url,
        files={'photo': ('image.jpg', img_response.content, content_type or 'image/jpeg')},
        timeout=15
    ).json()

    if 'error' in upload_result:
        raise Exception(f"Ошибка загрузки фото на сервер ВК: {upload_result}")

    # 4. Сохраняем фото как wall photo
    save_resp = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        data={
            'access_token': access_token,
            'v': '5.199',
            'group_id': group_id,
            'photo': upload_result['photo'],
            'server': upload_result['server'],
            'hash': upload_result['hash']
        },
        timeout=10
    ).json()

    if 'error' in save_resp:
        err = save_resp['error']
        code = err.get('error_code')
        if code == 15:
            raise Exception("Ошибка сохранения фото: недостаточно прав. Убедитесь, что токен имеет право photos и вы — админ группы.")
        else:
            raise Exception(f"Ошибка сохранения фото [{code}]: {err.get('error_msg', 'Неизвестная ошибка')}")

    photo = save_resp['response'][0]
    attachment = f"photo{photo['owner_id']}_{photo['id']}"

    # 5. Публикуем пост от имени группы
    post_resp = requests.post(
        'https://api.vk.com/method/wall.post',
        data={
            'access_token': access_token,
            'v': '5.199',
            'owner_id': -group_id,
            'from_group': 1,
            'message': message,
            'attachments': attachment
        },
        timeout=10
    ).json()

    if 'error' in post_resp:
        err = post_resp['error']
        code = err.get('error_code')
        if code == 15:
            raise Exception("Ошибка публикации: нет прав на запись в группу. Проверьте права токена и роль администратора.")
        else:
            raise Exception(f"Ошибка публикации поста [{code}]: {err.get('error_msg', 'Неизвестная ошибка')}")

    return post_resp['response']