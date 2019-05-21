import requests
import json
import time

TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
params = {'access_token': TOKEN,
          'v': '5.95',
          }


class User:
    def __init__(self, uid):
        self.uid = uid

    def get_params(self):
        return dict(
            access_token=TOKEN,
            v='5.95'
        )

    def get_groups(self):
        params = self.get_params()
        params['user_id'] = self.uid
        params['extended'] = '1'
        params['fields'] = 'members_count'
        response = requests.get(
            'https://api.vk.com/method/groups.get',
            params
        )
        self.groups_count = response.json()['response']['count']
        group_list = []
        for group in response.json()['response']['items']:
            group_list.append({'name': group['name'], 'gid': group['id'], 'members_count': group.get('members_count', 0)})
        return group_list

    def get_friends(self):
        params = self.get_params()
        params['user_id'] = self.uid
        params['count'] = '400'
        response = requests.get(
            'https://api.vk.com/method/friends.get',
            params
        )
        if 'error' not in response.json().keys():
            friend_list = response.json()['response']['items']
            friend_ids = ','.join(str(id) for id in friend_list)
        else:
            print('Пользователь не найден')
            main()
        return friend_ids

    def search_for_distinct_groups(self):
        params = self.get_params()
        params['user_ids'] = self.get_friends()
        groups = []
        count = 0
        for group in self.get_groups():
            params['group_id'] = group['gid']
            response = requests.get(
                'https://api.vk.com/method/groups.isMember',
                params
            )
            members = []
            if 'error' not in response.json().keys():
                for member in response.json()['response']:
                    members.append(member['member'])
                if 1 not in set(members):
                    groups.append(group)
                count += 1
                if count != self.groups_count:
                    print('До конца поиска осталось приблизительно {} %'.format((100 - (count * 100 // self.groups_count))))
            time.sleep(0.5)
        return json.dumps(groups, ensure_ascii=False, indent=1)

    def search_for_mutual_groups(self):
        params = self.get_params()
        params['user_ids'] = self.get_friends()
        groups = []
        for group in self.get_groups():
            params['group_id'] = group['gid']
            response = requests.get(
                'https://api.vk.com/method/groups.isMember',
                params
            )
            members = []
            if 'error' not in response.json().keys():
                for member in response.json()['response']:
                    members.append(member['member'])
                    member_dict = {x: members.count(x) for x in members}
                if 0 != int(member_dict.get(1, 0)) <= 5:
                    group['friends_in_group'] = member_dict[1]
                    groups.append(group)
            print('---')
            time.sleep(0.5)
        return json.dumps(groups, ensure_ascii=False, indent=1)


def search_user(user):
    params['q'] = user
    response = requests.get(
        'https://api.vk.com/method/users.search',
        params
    )
    if response.json()['response']['count'] == 0:
        print('Пользователь не найден')
        main()
    return response.json()['response']['items'][0]


def main():
    while True:
        user_input = input('Введите имя или id пользователя vk или q для выхода: ')
        # имя пользователя (eshmargunov) и id (171691064) для проверки
        try:
            if user_input == 'q':
                break
            elif user_input.isnumeric() == False:
                user = search_user(user_input)
                user1 = User(user['id'])
            else:
                user1 = User(user_input)
            with open('groups.json', 'w') as f:
                f.write(user1.search_for_distinct_groups())
                print('Поиск закончен. Результат находится в файле "groups.json"')
            with open('mutual_groups.json', 'w') as f:
                f.write(user1.search_for_mutual_groups())
                print('Поиск закончен. Результат находится в файле "mutual_groups.json"')
        except requests.exceptions.Timeout:
            print('Timeout occured')

main()