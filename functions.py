import datetime
import json
from random import randrange
import vk_api
from vk_api.exceptions import ApiError
from vk_api.longpoll import VkLongPoll
from tokens import user_token, group_token, V

vk_session = vk_api.VkApi(token=user_token)
vk_session2 = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session2)


def get_user_info(user_id):
    user_info = {}
    try:
        if response := vk_session.method('users.get',
                                         {'user_id': user_id,
                                          'v': 5.131,
                                          'fields': 'sex, status, age_at, age_to, has_photo, count, hometown'}):
            for key, value in response[0].items():
                user_info[key] = value['id'] if key == 'city' else value
        else:
            write_msg(user_id, '''Извините, что-то пошло не так.''')
            return False

    except vk_api.exceptions.ApiError as e:
        write_msg(user_id, '''Извините, что-то пошло не так.''')
        print(f'Error! {e}')
    return user_info


def write_msg(user_id, message, attachment='0'):
    vk_session.method('messages.send', {'user_id': user_id,
                                        'message': message,
                                        'random_id': randrange(10 ** 7),
                                        'attachment': attachment})


def find_matches(user_info):
    try:
        response = vk_session2.method('users.search', {
            'age_from': user_info['age'] - 3,
            'age_to': user_info['age'] + 3,
            'sex': 3 - user_info['sex'],
            'city': user_info['city'],
            'city_id': user_info['city'],
            'status': 6,
            'has_photo': 1,
            'count': 1000,
            'v': 5.131})
        if response:
            if response.get('items'):
                return response.get('items')
            write_msg(user_info['id'], 'Что-то пошло не так')
            return False
        write_msg(user_info['id'], 'Мы никого не нашли')
        return False
    except vk_api.exceptions.ApiError as e:
        write_msg(user_info['id'], '''Извините, что-то пошло не так.''')
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
    result = [element for element in photos if element != ['нет фото.'] and photos != 'нет доступа к фото']
    return sorted(result)


def json_create(lst):
    today = datetime.date.today()
    today_str = f'{today.day}.{today.month}.{today.year}'
    res = {}
    res_list = []
    for info in lst:
        _extracted_from_json_create_(today_str, res, info, res_list)
    with open("result.json", "a", encoding='UTF-8') as write_file:
        json.dump(res_list, write_file, ensure_ascii=False)
    print('Информация о загруженных файлах успешно записана в json файл.')


def _extracted_from_json_create_(today_str, res, info, res_list):
    res['data'] = today_str
    res['first_name'] = info[0]
    res['second_name'] = info[1]
    res['link'] = info[2]
    res['id'] = info[3]
    res_list.append(res.copy())
