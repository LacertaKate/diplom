import vk_api
import json
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_tokens import group_token, user_token, V
from vk_api.exceptions import ApiError
from sqlalchemy.exc import IntegrityError, InvalidRequestError

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)

session = Session()
connection = engine.connect()

def get_user_info(user_id):
    user_info = {}
    try:
        response = vk_session.method('users.get', {'user_id': user_id,
                                                   'v': 5.131,
                                                   'fields': 'sex, status, age_at, age_to, has_photo, count, hometown'})
        if response:
            for key, value in response[0].items():
                if key == 'city':
                    user_info[key] = value['id']
                else:
                    user_info[key] = value
        else:
            write_msg(user_id, f'''Извините, что-то пошло не так.''')
            return False
        
    except vk_api.exceptions.ApiError as e:
        write_msg(user_id, f'''Извините, что-то пошло не так.''')
        print(f'Error! {e}')
    return user_info

    
def search_users(user_info):
    all_persons = []
    link_profile = 'https://vk.com/id'
    vk_ = vk_api.VkApi(token=user_token)
    response = vk_.method('users.search', {
                           'sex': 3 - user_info['sex'],
                           'age_at': user_info['age'] - 3,
                           'age_to': user_info['age'] + 3,
                           'has_photo': 1,
                           'count': 25,
                           'online': 1,
                           'status': 6; 
                           'hometown': user_info['hometown']
                           })
     if response:
            if response.get('items'):
                return response.get('items')
            write_msg(user_info['id'], 'Что-то пошло не так')
            return False
        write_msg(user_info['id'], 'Никого не нашли')
        return False
    except vk_api.exceptions.ApiError as e:
        write_msg(user_info['id'], f'''Извините, что-то пошло не так.''')
        print(f'Error! {e}')


def get_photo(user_id):
    vk_ = vk_api.VkApi(token=user_token)
    try:
        response = vk_.method('photos.get',
                              {
                                  'access_token': user_token,
                                  'v': V,
                                  'owner_id': user_id,
                                  'album_id': 'profile',
                                  'count': 10,
                                  'extended': 1,
                                  'photo_sizes': 1,
                              })
    except ApiError:
        return 'нет доступа к фото'
    users_photos = []
    for i in range(10):
        try:
            users_photos.append(
                [response['items'][i]['likes']['count'],
                 'photo' + str(response['items'][i]['owner_id']) + '_' + str(response['items'][i]['id'])])
        except IndexError:
            users_photos.append(['нет фото.'])
    return users_photos


def sort_likes(photos):
    result = []
    for element in photos:
        if element != ['нет фото.'] and photos != 'нет доступа к фото':
            result.append(element)
    return sorted(result)


def json_create(lst):
    today = datetime.date.today()
    today_str = f'{today.day}.{today.month}.{today.year}'
    res = {}
    res_list = []
    for num, info in enumerate(lst):
        res['data'] = today_str
        res['first_name'] = info[0]
        res['second_name'] = info[1]
        res['link'] = info[2]
        res['id'] = info[3]
        res_list.append(res.copy())

    with open("result.json", "a", encoding='UTF-8') as write_file:
        json.dump(res_list, write_file, ensure_ascii=False)

    print(f'Информация о загруженных файлах успешно записана в json файл.')
