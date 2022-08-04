from telethon.tl.functions.channels import CreateChannelRequest, CheckUsernameRequest, UpdateUsernameRequest, InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
from telethon.tl.functions.messages import AddChatUserRequest, ExportChatInviteRequest
from telethon import TelegramClient, events, sync
import datetime as dt
import logging
import time

from database import User, Task, Gap, Member

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


def create_channel(member):
    try:
        user = client.get_input_entity(member.user.username)

        channel = client(CreateChannelRequest(member.gap.title, member.gap.bio, megagroup=False))
        channel_id = channel.__dict__["chats"][0].__dict__["id"]
        channel_link = client(
            ExportChatInviteRequest(
                peer=client.get_entity(channel_id),
                legacy_revoke_permanent=True,
                expire_date=None,
                usage_limit=-1
            )
        ).link

        client(InviteToChannelRequest(channel=channel_id, users=[user]))
        client.edit_admin(channel_id, user, is_admin=True, add_admins=False, invite_users=False)

        Gap.update(telegram_id=channel_id, link=channel_link).where(Gap.id == member.gap.id).execute()
        Task.update(status='done', done_time=dt.datetime.now()).where(Task.id == member.task.id).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception(f"Unexpected Error")

    finally:
        if Task.select().where(Task.id == member.task.id, Task.status != 'done').exists():
            Task.update(status='failed', done_time=dt.datetime.now()).where(Task.id == member.task.id).execute()


def create_group(member):
    try:
        user = client.get_input_entity(member.user.username)

        group = client(CreateChannelRequest(member.gap.title, member.gap.bio, megagroup=True))
        group_id = group.__dict__["chats"][0].__dict__['id']
        group_link = client(
            ExportChatInviteRequest(
                peer=client.get_entity(group_id),
                legacy_revoke_permanent=True,
                expire_date=None,
                usage_limit=-1
            )
        ).link

        client(InviteToChannelRequest(channel=group_id, users=[user]))
        client.edit_admin(group_id, user, is_admin=True, add_admins=False)

        Gap.update(telegram_id=group_id, link=group_link).where(Gap.id == member.gap.id).execute()
        Task.update(status='done', done_time=dt.datetime.now()).where(Task.id == member.task.id).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")

    finally:
        if Task.select().where(Task.id == member.task.id, Task.status != 'done').exists():
            Task.update(status='failed', done_time=dt.datetime.now()).where(Task.id == member.task.id).execute()


def add_user(member):
    try:
        user = client.get_input_entity(member.user.username)
        client(InviteToChannelRequest(channel=int(member.gap.telegram_id), users=[user]))
        Task.update(status='done', done_time=dt.datetime.now()).where(Task.id == member.task.id).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")


if __name__ == '__main__':
    while True:
        if task := Task.select().where(Task.status == 'pending').first():
            member = Member.get(task=task)
            if task.type == 1:
                create_channel(member)

            elif task.type == 2:
                create_group(member)

            elif task.type == 4:
                add_user(member)


        if user := User.select().where(User.telegram_id == None).first():  # set User.telegram_id for new users
            user_entity = client.get_input_entity(user.username)
            User.update(telegram_id=user_entity.user_id).where(User.username == user.username).execute()


        time.sleep(3)
