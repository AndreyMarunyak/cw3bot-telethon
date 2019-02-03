import re
import threading
import config

from my_hero import *

from my_hero import Hero

from get_admin_message import get_command
from telethon import TelegramClient, events

API_HASH = config.API_HASH

API_ID = config.API_ID

GAME_ID = 'ChatWarsBot'  # id of ChatWars3 bot

ADMIN_ID = config.ADMIN_ID

ORDER_ID = 614493767  # id of user/bot gives orders for battle

HELPER_ID = 615010125  # helper bot's id

client = TelegramClient('CW3bot', API_ID, API_HASH, connection_retries=0, timeout=180)

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

MyHero = Hero(bot_enable=False, quests=False, forest=True, valley=True, swamp=True, corovan=True, client=client)


@client.on(events.NewMessage(from_users=GAME_ID, pattern=r'Битва семи замков через|🌟Поздравляем! Новый уровень!🌟'))
def get_message_hero(event):
    logging.info('Received main message from bot')
    MyHero.endurance = int(re.search(r'Выносливость: (\d+)', event.raw_text).group(1))
    MyHero.endurance_max = int(re.search(r'Выносливость: (\d+)/(\d+)', event.raw_text).group(2))
    MyHero.state = re.search(r'Состояние:\n(.*)', event.raw_text).group(1)

    if re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!', event.raw_text):

        try:
            hours = int(re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!',
                                  event.raw_text).group(2))
        except TypeError:
            hours = 0

        try:
            minutes = int(re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!',
                                    event.raw_text).group(4))
        except TypeError:
            minutes = 0
        MyHero.time_to_battle = (hours if hours else 0) * 3600 + (minutes if minutes else 0) * 60  # convert to seconds

        logging.info('Time to battle: {0} : {1}. In seconds (approximately): {2}'.format(
            hours if hours else 0, minutes if minutes else 0, MyHero.time_to_battle))

    logging.info('endurance: {0} / {1}, State: {2}'.format(MyHero.endurance, MyHero.endurance_max, MyHero.state))

    MyHero.current_time = datetime.now()  # refresh current time

    if MyHero.endurance > 0 and MyHero.quests:
        if MyHero.state == '🛌Отдых':
            go_quest()
        else:
            logging.info('So busy for quests')

    # attack corovan between certain time
    if MyHero.endurance >= 2 and MyHero.corovan and 3 <= MyHero.current_time.hour <= 6:
        attack_corovan()

    if MyHero.time_to_battle > 3600 and MyHero.endurance == 0:
        logging.info('Time to battle > 1 hour and Endurance = 0. Delay = 30 min')
        MyHero.delay = 1800


# if bot ready to go to the quest. This func chooses one
def go_quest():
    MyHero.action(MyHero.quest_button)
    sleep(random.randint(1, 3))
    # choose random quest from quest list and 'press' quest button
    MyHero.action(MyHero.quests_button_list[random.choice(MyHero.quest_list)])


def attack_corovan():
    MyHero.action(MyHero.quest_button)
    sleep(random.randint(1, 3))
    MyHero.action(MyHero.quests_button_list['corovan'])


@client.on(events.NewMessage(from_users=GAME_ID, pattern=r'Ты заметил'))
def defend_corovan(event):
    MyHero.action('/go')
    logging.info('Your pledges are safe')


@client.on(events.NewMessage(from_users=ADMIN_ID))
def get_admin_message(event):
    command = event.raw_text.lower()
    get_command(command, MyHero, client)


@client.on(events.NewMessage(from_users=GAME_ID, pattern='After a successful act of'))
def pledge(event):
    logging.info('We got pledge!')
    MyHero.action('/pledge')


@client.on(events.NewMessage(from_users=ORDER_ID, pattern=r'⚔️(🐢|🍁|🌹|☘️|🦇|🖤|🍆)'))
def get_order(event):
    order = re.search(r'⚔️(🐢|🍁|🌹|☘️|🦇|🖤|🍆)', event.raw_text).group(1)
    MyHero.action(order)


@client.on(events.NewMessage(from_users=HELPER_ID, pattern=r'Изменения в стоке:'))
def get_report_from_battle(event):
    MyHero.action('/report')


@client.on(events.NewMessage(from_users=GAME_ID, pattern='.+\nТвои результаты в бою:'))
def send_report(event):
    client.forward_messages(HELPER_ID, event.message)


def worker():
    temp_time = 0

    while True:

        try:

            if MyHero.bot_enable:

                if time() - temp_time > MyHero.delay:

                    temp_time = time()

                    if MyHero.bot_enable:

                        MyHero.action('🏅Герой')

                        MyHero.current_time = datetime.now()
                        if MyHero.current_time.hour >= 23 or MyHero.current_time.hour <= 6:
                            if not MyHero.quests and MyHero.endurance < 2:
                                MyHero.delay = 1800
                            else:
                                MyHero.delay = random.randint(600, 800)  # increases delay at night
                        else:
                            if not MyHero.quests and not MyHero.corovan:
                                MyHero.delay = 1800
                            else:
                                MyHero.delay = random.randint(300, 500)
                        logging.info('Delay = {}'.format(MyHero.delay))
                        continue
                    else:
                        logging.info('Bot is going to sleep')


        except Exception as error:
            logging.info('Some trouble in worker: {}'.format(error))


if __name__ == '__main__':
    client.start()
    main_thread = threading.Thread(target=worker)
    main_thread.daemon = True  # allows to stop thread correctly
    main_thread.start()
    client.run_until_disconnected()
