import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from functions import get_photo, sort_likes, json_create, write_msg
from classes import engine, Session, register_user, add_user, add_user_photos, check_db_favorites, check_db_master, check_db_user, delete_db_favorites
from vk_tokens import group_token

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)

session = Session()
connection = engine.connect()

def loop_bot():
    for this_event in longpoll.listen():
        if this_event.type == VkEventType.MESSAGE_NEW and this_event.to_me:
            message_text = this_event.text
            return message_text, this_event.user_id


def menu_bot(id_num):
    write_msg(id_num,
              f"Вас приветствует бот - Vkinder\n"
              f"\nЕсли вы используете его первый раз - пройдите регистрацию.\n"
              f"Для регистрации введите - Да.\n"
              f"Если вы уже зарегистрированы - начинайте поиск.\n"
              f"\nДля поиска - мужчина 25-30 Санкт-Петербург\n")
    
def show_info():
    write_msg(user_id, 'Это была последняя анкета.Поиск - мужчина 25-30 Санкт-ПетербургМеню бота - Vkinder')


def reg_new_user(id_num):
    write_msg(id_num, 'Вы прошли регистрацию.')
    write_msg(id_num,
              f"Vkinder - для активации бота\n")
    register_user(id_num)
  
def go_to_favorites(ids):
    alls_users = check_db_favorites(ids)
    write_msg(ids, 'Избранные анкеты:')
    for nums, users in enumerate(alls_users):
        write_msg(ids, f'{users.first_name}, {users.second_name}, {users.link}')
        write_msg(ids, '1 - Удалить из избранного, 0 - Далее \nq - Выход')
        msg_texts, user_ids = loop_bot()
        if msg_texts == '0':
            if nums >= len(alls_users) - 1:
                write_msg(user_ids, f'Это была последняя анкета.\n'
                                    f'Vkinder - вернуться в меню\n')
        elif msg_texts == '1':
            delete_db_favorites(users.vk_id)
            write_msg(user_ids, 'Анкета успешно удалена.')
            if nums >= len(alls_users) - 1:
                write_msg(user_ids, f'Это была последняя анкета.\n'
                                    f'Vkinder - вернуться в меню\n')
        elif msg_texts.lower() == 'q':
            write_msg(ids, 'Vkinder - для активации бота.')
            break

if __name__ == '__main__':
    while True:
        msg_text, user_id = loop_bot()
        if msg_text == "vkinder":
            menu_bot(user_id)
            msg_text, user_id = loop_bot()
            if msg_text.lower() == 'да':
                reg_new_user(user_id)
            elif len(msg_text) > 1:
                sex = 0
                if msg_text[0:7].lower() == 'девушка':
                    sex = 1
                elif msg_text[0:7].lower() == 'мужчина':
                    sex = 2
                age_at = msg_text[8:10]
                if int(age_at) < 18:
                    write_msg(user_id, 'Выставлен минимальный возраст - 18 лет.')
                    age_at = 18
                age_to = msg_text[11:14]
                if int(age_to) >= 100:
                    write_msg(user_id, 'Выставлено максимальное значение 99 лет.')
                    age_to = 99
                city = msg_text[14:len(msg_text)].lower()
                result = search_users(sex, int(age_at), int(age_to), city)
                json_create(result)
                current_user_id = check_db_master(user_id)
                
                for i in range(len(result)):
                    dating_user, blocked_user = check_db_user(result[i][3])
                    user_photo = get_photo(result[i][3])
                    if user_photo == 'нет доступа к фото' or dating_user is not None or blocked_user is not None:
                        continue
                    sorted_user_photo = sort_likes(user_photo)
                    write_msg(user_id, f'\n{result[i][0]}  {result[i][1]}  {result[i][2]}', )
                    try:
                        write_msg(user_id, f'фото:',
                                  attachment=','.join
                                  ([sorted_user_photo[-1][1], sorted_user_photo[-2][1],
                                    sorted_user_photo[-3][1]]))
                    except IndexError:
                        for photo in range(len(sorted_user_photo)):
                            write_msg(user_id, f'фото:',
                                      attachment=sorted_user_photo[photo][1])
                    write_msg(user_id, '1 - Добавить, 0 - Далее, \nq - выход из поиска')
                    msg_text, user_id = loop_bot()
                    if msg_text == '0':
                        if i >= len(result) - 1:
                            show_info()
                                                              
                    elif msg_text == '1'
                        if i >= len(result) - 1:
                            show_info()
                            break
                        try:
                            add_user(user_id, result[i][3], result[i][1],
                                     result[i][0], city, result[i][2], current_user_id.id)
                            add_user_photos(user_id, sorted_user_photo[0][1],
                                            sorted_user_photo[0][0], current_user_id.id)
                        except AttributeError:
                            write_msg(user_id, 'Вы не зарегистрировались!\n Введите Vkinder для перезагрузки')
                            break
