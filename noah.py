import matplotlib.pyplot as plt
import networkx as nx
from vk_api import *
from key import *
import time

# токен вбивать в файл key.py
access_token = token
mode = int(input("Enter mode (1 for friends, 2 for groups): "))
# сколько отображать ( 0 -> всех ; другое число -> столько и отобразит )
howManySea =int(input("Enter how many people add in graph (0->all or n-frends): "))

friends_list = []
while(access_token == ""):print("Enter valid access_token!");access_token = input(":>")
vk_session = vk_api.VkApi(token=access_token)
try:
    vk = vk_session.get_api()
    nickname = input("Enter nickname: ")
    main_id = vk.utils.resolveScreenName(screen_name=nickname)['object_id']
    friends = vk.friends.get(user_id=main_id)
except Exception:
    print("Error 404:\nNo enternet connection \nOr bad apiKey")
    exit()

def get_name_vk(id):
    user_get = vk.users.get(user_ids=id)[0]
    string = user_get['last_name'] + ' ' + user_get["first_name"]
    user_dict[id] = string
    print(string + '\nid: ' + str(id) + '\n' + '-'*30)
    return string + '\nid: ' + str(id)

def id_to_name(id):
    name = user_dict[id]
    string = name + '\nid: ' + str(id)
    return string

class Friend:
    def __init__(self, user_id, full_name, listGroupsId,listFrendsId):
        self.user_id = user_id
        self.full_name = full_name
        self.listGroupsId = listGroupsId
        self.listFrendsId = listFrendsId

class Graph:
    def __init__(self, user_dict, nodes, edges):
        self.user_dict = user_dict
        self.nodes = nodes
        self.edges = edges

def find_linked(edges, arr):
    if mode == 1:
        # проходимся по нашим пользователям
        for user in range (len(arr)):
            # id текущего пользователя
            user_id = arr[user].user_id
            # проходмся по след друзьям
            for k in range(user+1, len(arr)):
                if((user_id in arr[k].listFrendsId)):
                    edges.append((id_to_name(user_id),id_to_name(arr[k].user_id)))
                    break
        return edges
    if mode == 2:
        group_edges = []
        group_members = {}
        for user in range(len(arr)):
            for group_id in arr[user].listGroupsId:
                if group_id not in group_members:
                    group_members[group_id] = 1
                else:
                    group_members[group_id] += 1
        
        for group_id, count in group_members.items():
            if count >= 2:
                for user in range(len(arr)):
                    if group_id in arr[user].listGroupsId:
                        user_id = arr[user].user_id
                        group_edges.append((f"Group_{group_id}", id_to_name(user_id))) # Меняем порядок
        return group_edges
    else:
        return []


nodes, edges = [], []
user_dict = {}
nodes.append(get_name_vk(main_id))

if mode == 1:
    print("Start search frends of Frends\n")
    a=0
    for id in friends['items']:
        a+=1

        if howManySea >0:
            print(f"{a}/{howManySea}\n")
        else:
            print(f"{a}/{len(friends['items'])}\n")


        if howManySea >0 and a==howManySea:
            break
        
        

        time.sleep(0.33)  # Уменьшаем задержку для соблюдения лимитов VK API

        user_get = vk.users.get(user_ids=(id))
        user_get = user_get[0]
        try:
            user_friends = (vk.friends.get(user_id=id))['items']
            group_get = vk.groups.get(user_id=id)
            user_dict[id] = f"{user_get['last_name']} {user_get['first_name']}"	
            nodes.append(id_to_name(id))
            edges.append((id_to_name(main_id),id_to_name(id)))
            friends_list.append(Friend(user_id=id,full_name=f"{user_get['last_name']} {user_get['first_name']}",listGroupsId=group_get['items'],listFrendsId=user_friends)) 
        except ApiError:
            print(f"WARNING: {user_get['last_name']} {user_get['first_name']} id:{id} private account!")
    arr = friends_list
    G = nx.Graph()
    G.add_nodes_from(nodes)
    edges = find_linked(edges, arr)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    pos[main_id] = [0, 0]
    nx.draw(G, pos, with_labels=True, node_size=100, node_color='green', font_weight='bold', font_color='red')
    try:
        plt.show()
    except KeyboardInterrupt:
        print("\nExit")
        exit()

if mode == 2:
    print("Start search frends of Grops\n")
    a = 0
    for id in friends['items']:
        a+=1
        if howManySea >0:
            print(f"{a}/{howManySea}\n")
        else:
            print(f"{a}/{len(friends['items'])}\n")
        if howManySea >0 and a==howManySea:
            break

        time.sleep(0.33)
        user_get = vk.users.get(user_ids=(id))
        user_get = user_get[0]
        try:
            user_friends = (vk.friends.get(user_id=id))['items']
            group_get = vk.groups.get(user_id=id)
            user_dict[id] = f"{user_get['last_name']} {user_get['first_name']}" 
            nodes.append(id_to_name(id))
            # Добавляем ребро между главным пользователем и его другом
            edges.append((id_to_name(main_id), id_to_name(id)))
            friends_list.append(Friend(user_id=id,full_name=f"{user_get['last_name']} {user_get['first_name']}",listGroupsId=group_get['items'],listFrendsId=user_friends))
        except ApiError:
            print(f"WARNING: {user_get['last_name']} {user_get['first_name']} id:{id} private account!")
    # Получаем информацию о группах главного пользователя
    group_get_main = vk.groups.get(user_id=main_id)
    # Добавляем группы главного пользователя
    for group_id in group_get_main['items']:
        nodes.append(f"Group_{group_id}")
        edges.append((id_to_name(main_id), f"Group_{group_id}"))

    arr = friends_list
    G = nx.Graph()
    G.add_nodes_from(nodes)
    # Находим общих друзей и добавляем ребра в граф
    edges += find_linked(edges, arr) # Добавляем к уже существующим рёбрам
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    pos[main_id] = [0, 0]
    nx.draw(G, pos, with_labels=True, node_size=100, node_color='green', font_weight='bold', font_color='red', edge_color='blue')
    try:
        plt.show()
    except KeyboardInterrupt:
        print("\nExit")
        exit()