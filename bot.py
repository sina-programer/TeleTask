from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
from telethon import TelegramClient, events, sync
from telethon import functions, types

import datetime as dt
import logging
import time

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


@client.on(events.NewMessage(pattern=r'delete gap*'))
def delete_created_gaps(event):
    gap_fields = Gap.get_fields()
    counter = 0
    limit = event.message.message.split()[-1]

    try:
        limit = int(limit)
    except Exception:
        client.send_message(event.message.chat_id, 'Correct form: \ndelete gap <number>')
        return

    for gap in Gap.select():
        if counter == limit:
            break

        if gap.telegram_id:
            try:
                gap_info = '\n'.join([f'{f}: {str(getattr(gap, f))}' for f in gap_fields])
                gap_entity = client.get_entity(types.PeerChannel(int(gap.telegram_id)))
                client(
                    functions.channels.DeleteChannelRequest(
                        channel=gap_entity
                    )
                )

                client.send_message(event.message.chat_id, f'Gap deleted! \n\n{gap_info}')
                client.send_message('sina_programer', f'Gap deleted! \n\n{gap_info}')

            except Exception as error:
                client.send_message(event.message.chat_id, f"Can't delete Gap! \n\n{gap_info} \n\nError: {error}")
                client.send_message('sina_programer', f"Can't delete Gap! \n\n{gap_info} \n\nError: {error}")

            finally:
                counter += 1
                time.sleep(10)


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
        user = client.get_entity(types.PeerUser(member.user.username))
        gap = client.get_entity(types.PeerChannel(int(member.gap.telegram_id)))
        client(functions.channels.InviteToChannelRequest(channel=gap, users=[user]))
        Task.update(status='done', done_time=dt.datetime.now()).where(Task.id == member.task.id).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")


def verify_user(verify):
    pass  # verify user here



if __name__ == '__main__':
    while True:
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

            for user in User.select().where(User.telegram_id == None):  # set User.telegram_id for new users
                user_entity = client.get_entity(types.PeerUser(user.username))
                User.update(telegram_id=user_entity.id).where(User.username == user.username).execute()

        except Exception as error:
            print(error)

        finally:
            time.sleep(3)
