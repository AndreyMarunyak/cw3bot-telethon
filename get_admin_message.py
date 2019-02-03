from config import ADMIN_ID


def bot_on(MyHero, client):
    MyHero.bot_enable = True
    client.send_message(ADMIN_ID, 'Bot enabled')


def bot_off(MyHero, client):
    MyHero.bot_enable = False
    client.send_message(ADMIN_ID, 'Bot disabled')


def quest_on(MyHero, client):
    MyHero.quests = True
    client.send_message(ADMIN_ID, 'Quests enabled')


def quest_off(MyHero, client):
    MyHero.quests = False
    client.send_message(ADMIN_ID, 'Quests disabled')


def corovan_on(MyHero, client):
    MyHero.corovan = True
    client.send_message(ADMIN_ID, 'Corovans enabled')


def corovan_off(MyHero, client):
    MyHero.corovan = False
    client.send_message(ADMIN_ID, 'Corovans disabled')


def forest_on(MyHero, client):
    MyHero.forest = True
    quest_switch_on('forest', MyHero, client)


def forest_off(MyHero, client):
    MyHero.forest = False
    quest_switch_off('forest', MyHero, client)


def valley_on(MyHero, client):
    MyHero.valley = True
    quest_switch_on('valley', MyHero, client)


def valley_off(MyHero, client):
    MyHero.valley = False
    quest_switch_off('valley', MyHero, client)


def swamp_on(MyHero, client):
    MyHero.swamp = True
    quest_switch_on('swamp', MyHero, client)


def swamp_off(MyHero, client):
    MyHero.swamp = False
    quest_switch_off('swamp', MyHero, client)


def help(_, client):
    client.send_message(ADMIN_ID, '\n'.join([
        'quest_on/off',
        'corovan_on/off',
        'bot_on/off',
        'forest_on/off',
        'swamp_on/off',
        'valley_on/off',
        'status'
    ]))

def status(MyHero, client):
    client.send_message(ADMIN_ID, '\n'.join([
        str(MyHero.quest_list),
        'quest = ' + str(MyHero.quests),
        'corovan = ' + str(MyHero.corovan),
        'bot = ' + str(MyHero.bot_enable)
    ]))

def quest_switch_on(quest_name, MyHero, client):
    if quest_name not in MyHero.quest_list:
        MyHero.quest_list.append(quest_name)
        client.send_message(ADMIN_ID, quest_name + ' added to quests list')
        if not MyHero.quests:
            client.send_message(ADMIN_ID, 'Quest switch is off. Turn in on')

    else:
        client.send_message(ADMIN_ID, quest_name + ' already in list')

    client.send_message(ADMIN_ID, 'Quest list: ' + str(MyHero.quest_list))


def quest_switch_off(quest_name, MyHero, client):
    if quest_name in MyHero.quest_list:
        MyHero.quest_list.remove(quest_name)
        client.send_message(ADMIN_ID, quest_name + ' deleted from quest list')
        if not MyHero.quest_list:
            client.send_message(ADMIN_ID, 'list is empty')
            MyHero.quests = False

    else:
        client.send_message(ADMIN_ID, quest_name + ' is not in list')

def get_command(command, MyHero, client):
    switcher = {
        'bot_on': bot_on,
        'bot_off': bot_off,
        'quest_on': quest_on,
        'quest_off': quest_off,
        'corovan_on': corovan_on,
        'corovan_off': corovan_off,
        'forest_on': forest_on,
        'forest_off': forest_off,
        'valley_on': valley_on,
        'valley_off': valley_off,
        'swamp_on': swamp_on,
        'swamp_off': swamp_off,
        'help': help,
        'status': status
    }


    if command in switcher.keys():
        func = switcher.get(command)
        func(MyHero, client)


