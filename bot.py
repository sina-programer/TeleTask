from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
from telethon import TelegramClient, events, sync
from telethon import functions, types

import datetime as dt
import schedule
import logging
import time
import pytz

from database import User, Task, Gap, Member, Verify

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(
    format='%(asctime)s - %(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)

client = TelegramClient(
    session=config['Bot']['session_name'],
    api_id=int(config['Bot']['api_id']),
    api_hash=config['Bot']['api_hash']
)
client.start()

logging.debug(f'is user authorized: {client.is_user_authorized()}')

tehran_tz = pytz.timezone('Asia/Tehran')

def now():
    return dt.datetime.now(tehran_tz)


def create_channel(member):
    try:
        user = client.get_entity(types.PeerUser(member.user.username))

        channel = client(functions.channels.CreateChannelRequest(member.gap.title, member.gap.bio, megagroup=False))
        channel_info = channel.__dict__["chats"][0].__dict__
        channel_id = channel_info["id"]
        channel_link = client(
            functions.messages.ExportChatInviteRequest(
                peer=client.get_entity(types.PeerChannel(channel_id)),
                legacy_revoke_permanent=True,
                expire_date=None,
                usage_limit=-1
            )
        ).link

        client(functions.channels.InviteToChannelRequest(channel=channel_id, users=[user]))
        client.edit_admin(channel_id, user, is_admin=True, add_admins=False, invite_users=False)

        Gap.update(telegram_id=channel_id, link=channel_link).where(Gap.id == member.gap.id).execute()
        Task.update(status='done', done_time=now()).where(Task.id == member.task.id).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception(f"Unexpected Error")

    finally:
        if Task.select().where(Task.id == member.task.id, Task.status != 'done').exists():
            Task.update(status='failed', done_time=now()).where(Task.id == member.task.id).execute()


def create_group(member):
    try:
        user = client.get_entity(types.PeerUser(member.user.username))

        group = client(functions.channels.CreateChannelRequest(member.gap.title, member.gap.bio, megagroup=True))
        group_info = group.__dict__["chats"][0].__dict__
        group_id = group_info['id']
        group_link = client(
            functions.messages.ExportChatInviteRequest(
                peer=client.get_entity(types.PeerChannel(group_id)),
                legacy_revoke_permanent=True,
                expire_date=None,
                usage_limit=-1
            )
        ).link

        client(functions.channels.InviteToChannelRequest(channel=group_id, users=[user]))
        client.edit_admin(group_id, user, is_admin=True, add_admins=False)

        Gap.update(telegram_id=group_id, link=group_link).where(Gap.id == member.gap.id).execute()
        Task.update(status='done', done_time=now()).where(Task.id == member.task.id).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")

    finally:
        if Task.select().where(Task.id == member.task.id, Task.status != 'done').exists():
            Task.update(status='failed', done_time=now()).where(Task.id == member.task.id).execute()


def add_user(member):
    try:
        user = client.get_entity(types.PeerUser(member.user.username))
        gap = client.get_entity(types.PeerChannel(int(member.gap.telegram_id)))
        client(functions.channels.InviteToChannelRequest(channel=gap, users=[user]))
        Task.update(status='done', done_time=now()).where(Task.id == member.task.id).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")


def verify_user(verify):
    pass  # verify user here



def handle_new_task():
    try:
        for task in Task.select().where(Task.status == 'pending'):
            member = Member.get(task=task)
            if task.type == 1:
                create_channel(member)

            elif task.type == 2:
                create_group(member)

            elif task.type == 4:
                add_user(member)

            elif task.type == 5:
                verify_user(Verify.get(task=task))

    except Exception as error:
        print(error)


def handle_new_user():
    try:
        for user in User.select().where(User.telegram_id == None):
            user_entity = client.get_entity(types.PeerUser(user.username))
            User.update(telegram_id=user_entity.id).where(User.username == user.username).execute()

    except Exception as error:
        print(error)


def handle_expired_users():
    try:
        for member in Member.select():
            if member.expire_date == dt.date.today():
                gap = client.get_entity(types.PeerChannel(int(member.gap.id)))
                user = client.get_entity(types.PeerUser(member.user.username))

                client.kick_participant(gap, user)

    except Exception as error:
        print(error)



if __name__ == '__main__':
    schedule.every(2).seconds.do(handle_new_task)
    schedule.every().minute.do(handle_new_user)
    schedule.every().day.at('06:00').do(handle_expired_users)

    while True:
        schedule.run_pending()
        time.sleep(1)
