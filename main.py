import os
from dotenv import load_dotenv
from vk_post_with_image import vk_post_with_image

# Загружаем переменные из .env
load_dotenv()

args = {
    "access_token": os.getenv("VK_ACCESS_TOKEN"),
    "image_url": "https://i.pinimg.com/736x/1c/12/44/1c1244410bfa954f9a6232b182b04b80.jpg",
    "message": "Новый пост с изображением через API!",
    "group_id": int(os.getenv("VK_GROUP_ID"))
}

try:
    result = vk_post_with_image(args)
    print("Пост успешно опубликован:", result)
except Exception as e:
    print("Ошибка:", str(e))