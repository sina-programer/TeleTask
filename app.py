from flask import Flask, jsonify, request, make_response
import datetime as dt
import requests
import time

from database import User, Task, Gap, Member, Verify 

import configparser

config = configparser.ConfigParser()
config.read('config.ini')


def check_attributes(data: dict, attrs):
    """
    This function check that all necessary attributes there are in data

    NOTE: if you want to check that there are at least one of some attrs, you can send they in a list.  for example:
    check_attributes(data, ['first_necessary', ['second_optional1', 'second_optional2'], 'third_necessary'])
    but, must there is at least one of ['second_optional1', 'second_optional2']
    """

    for attr in attrs:
        if isinstance(attr, list):  # if <attr> is a list, existing one of them is enough
            if all(not data.get(a, None) for a in attr):
                response = {'message': f"you have to enter at least one of {attr}"}
                requests.post(config["Site"]["host"] + '/create/callback', json=response)
                return jsonify(response)

        elif not data.get(attr, None):
            response = {'message': f"<{attr}> is invalid"}
            requests.post(config["Site"]["host"] + '/create/callback', json=response)
            return jsonify(response)


def clear_data(data: dict, exceptions=[]):
    funcs = {
        'phone_number': lambda x: x.replace('+', '').replace('"', '').strip(),
        'username': lambda x: x.replace('@', '').replace('"', '').strip(),
        'general_str': lambda x: x.replace('"', '').strip()
    }

    for key in data:
        if key not in exceptions:
            if key in funcs:
                data[key] = funcs[key](data[key])
            else:
                data[key] = funcs['general_str'](data[key])

    return data


def _create_channel():
    data = clear_data(dict(request.values))
    if result := check_attributes(data, ['username', 'phone_number', 'channel_title']):
        return result

    channel = Gap.create(
        package_id=data.get('package_id', None),
        title=data['channel_title'],
        bio=data.get('channel_bio', ''),  # maybe there is not at all
        create_date=dt.date.today(),
        is_group=False,
    )

    user = User.get_or_none(
        username=data['username'],
        phone_number=data['phone_number']
    )
    if not user:
        user = User.create(
            username=data['username'],
            phone_number=data['phone_number'],
            authenticated=False,
            signup_date=dt.date.today()
        )

    task = Task.create(
        type=1,
        status='pending',
        create_time=dt.datetime.now()
    )

    member = Member.create(
        user=user,
        gap=channel,
        is_admin=True,
        task=task,
        add_date=dt.date.today()
    )


    while True:
        time.sleep(3)
        member = Member.get_by_id(member.id)
        if member.task.status != 'pending':
            break


    if member.task.status == 'done':
        response = {
                'task_type': 1,
                'message': '201 Channel created',
                'severity': "info",
                'package_id': member.gap.package_id,
                'id': member.gap.telegram_id,
                'link': member.gap.link,
                'title': member.gap.title,
                'bio': member.gap.bio
        }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            201
        )

    else:
        response = {
                "message": '500 Channel not created',
                "severity": "danger"
            }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            500
        )


def _create_group():
    data = clear_data(dict(request.values))
    if result := check_attributes(data, ['username', 'phone_number', 'group_title']):
        return result

    group = Gap.create(
        package_id=data.get('package_id', None),
        title=data['group_title'],
        bio=data.get('group_bio', ''),  # might there is not at all
        create_date=dt.date.today(),
        is_group=True
    )

    user = User.get_or_none(
        username=data['username'],
        phone_number=data['phone_number']
    )
    if not user:
        user = User.create(
            username=data['username'],
            phone_number=data['phone_number'],
            authenticated=False,
            signup_date=dt.date.today()
        )

    task = Task.create(
        type=2,
        status='pending',
        create_time=dt.datetime.now()
    )

    member = Member.create(
        user=user,
        gap=group,
        is_admin=True,
        task=task,
        add_date=dt.date.today()
    )

    while True:
        time.sleep(3)
        member = Member.get_by_id(member.id)
        if member.task.status != 'pending':
            break

    if member.task.status == 'done':
        response = {
                'task_type': 2,
                'message': '201 Group created',
                'severity': "info",
                'package_id': member.gap.package_id,
                'id': member.gap.telegram_id,
                'link': member.gap.link,
                'title': member.gap.title,
                'bio': member.gap.bio
            }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            201
        )

    else:
        response = {
                "message": '500 Group Not Created',
                "severity": "danger"
            }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            500
        )


def _create_both():
    data = clear_data(dict(request.values))
    if result := check_attributes(data, ['username', 'phone_number', 'group_title', 'channel_title']):
        return result

    channel = Gap.create(
        package_id=data.get('package_id', None),
        title=data['channel_title'],
        bio=data.get('channel_bio', ''),  # might there is not at all
        create_date=dt.date.today(),
        is_group=False
    )
    group = Gap.create(
        package_id=data.get('package_id', None),
        title=data['group_title'],
        bio=data.get('group_bio', ''),
        create_date=dt.date.today(),
        is_group=True
    )

    user = User.get_or_none(
        username=data['username'],
        phone_number=data['phone_number']
    )
    if not user:
        user = User.create(
            username=data['username'],
            phone_number=data['phone_number'],
            authenticated=False,
            signup_date=dt.date.today()
        )

    group_task = Task.create(
        type=2,
        status='pending',
        create_time=dt.datetime.now()
    )
    group_member = Member.create(
        user=user,
        gap=group,
        is_admin=True,
        task=group_task,
        add_date=dt.date.today()
    )

    channel_task = Task.create(
        type=1,
        status='pending',
        create_time=dt.datetime.now()
    )
    channel_member = Member.create(
        user=user,
        gap=channel,
        is_admin=True,
        task=channel_task,
        add_date=dt.date.today()
    )


    for member in [group_member, channel_member]:
        while True:
            time.sleep(3)
            member = Member.get_by_id(member.id)
            if member.task.status != 'pending':
                break

    group_member = Member.get_by_id(group_member.id)
    channel_member = Member.get_by_id(channel_member.id)

    created_gaps = []
    if channel_member.task.status == 'done':
        created_gaps.append('Channel')
    if group_member.task.status == 'done':
        created_gaps.append('Group')
    created_gaps = ' and '.join(created_gaps)

    if created_gaps:
        response = {
                'task_type': 3,
                'message': f'201 {created_gaps} created',
                'package_id': channel_member.gap.package_id,
                'channel_title': channel_member.gap.title,
                'channel_id': channel_member.gap.telegram_id,
                'channel_bio': channel_member.gap.bio,
                'channel_link': channel_member.gap.link,
                'group_id': group_member.gap.telegram_id,
                'group_bio': group_member.gap.bio,
                'group_title': group_member.gap.title,
                'group_link': group_member.gap.link,
                'severity': "info"
            }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            201
        )

    else:
        response = {
                "message": '500 Not Created',
                "severity": "danger"
            }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            500
        )


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Home</h1>"


@app.route('/create', methods=['GET', 'POST'])
def create():
    data = clear_data(dict(request.values))
    task_type = data.get('task_type', None)
    if not task_type:
        response = {'message': 'Please enter task type!'}
        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return jsonify(response)


    if task_type == '1':
        return _create_channel()

    elif task_type == '2':
        return _create_group()

    elif task_type == '3':
        return _create_both()

    else:
        response = {"message": 'Please enter a valid task type!'}
        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return jsonify(response)


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    data = clear_data(dict(request.values))
    if result := check_attributes(data, ['username', 'phone_number', ['channel_id', 'group_id']]):
        return result

    if expire_date := data.get('expire_date', None):
        expire_date = dt.datetime.strptime(expire_date, '%d_%m_%Y').date()

    user = User.get_or_none(
        username=data['username'],
        phone_number=data['phone_number']  # save without space ' ' at first when sent '+'
    )
    if not user:
        user = User.create(
            username=data['username'],
            phone_number=data['phone_number'],
            authenticated=False,
            signup_date=dt.date.today()
        )

    tasks = []
    done_response = {
        "message": '200 user added',
        "severity": "info"
    }

    if channel_id := data.get('channel_id', None):
        channel_task = Task.create(
            type=4,
            status='pending',
            create_time=dt.datetime.now()
        )
        tasks.append(channel_task)

        channel_member = Member.create(
            user=user,
            gap=Gap.get(telegram_id=channel_id),
            is_admin=False,
            task=channel_task,
            add_date=dt.date.today(),
            expire_date=expire_date
        )


    if group_id := data.get('group_id', None):
        group_task = Task.create(
            type=4,
            status='pending',
            create_time=dt.datetime.now()
        )
        tasks.append(group_task)

        group_member = Member.create(
            user=user,
            gap=Gap.get_or_none(telegram_id=group_id),
            is_admin=False,
            task=group_task,
            add_date=dt.date.today(),
            expire_date=expire_date
        )

    while Member.select().where(Member.task.in_(tasks)).join(Task).where(Task.status == 'pending').exists():
        time.sleep(3)


    condition = False
    if data.get('channel_id', None):
        channel_member = Member.get_by_id(channel_member.id)
        done_response['added_channel_id'] = channel_member.gap.telegram_id
        condition = condition or channel_member.task.status == 'done'
    if data.get('group_id', None):
        group_member = Member.get_by_id(group_member.id)
        done_response['added_group_id'] = group_member.gap.telegram_id
        condition = condition or group_member.task.status == 'done'

    if condition:
        requests.post('http://parvaneh.app/create/callback', json=done_response)
        return make_response(
            jsonify(done_response),
            200
        )

    else:
        response = {
                "message": '500 User Could Not Be Added',
                "severity": "danger"
                }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            500
        )


@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    return 'Please use /fetch/user to get users. You can do the same with "gap"'


def _get_mask(prefix, Model):
    """
    this function filter parameters and give only parameters who starts with <prefix> and exists in <Model> fields
    """

    data = dict(request.values)
    fields = Model.get_fields()
    if params := {key.removeprefix(prefix): value for key, value in data.items() if (prefix in key) and key.removeprefix(prefix) in fields}:
        model = Model.get_or_none(**params)  # get obj instance by <params>
        if model:
            return Model.id == model.id

        return False  # if there isn't desired instance, return nothing


def _fetch():
    prefixes = ['gap', 'task', 'user']  # only tables who have at least one ForeignKeyField in Member table
    # masks = {prefix: _get_mask(f'{prefix}_', eval(prefix.title())) for prefix in prefixes}  # not very readable
    masks = {
        # table_name: table_mask
        'gap': _get_mask('gap_', Gap),
        'task': _get_mask('task_', Task),
        'user': _get_mask('user_', User)
    }

    mask = Member.select()
    # filter by Member fields, without prefix
    mask = mask & Member.select().where(_get_mask('', Member))

    for key, value in masks.items():
        mask = mask & Member.select().join(eval(key.title())).where(value)

    return mask


@app.route('/fetch/user', methods=['GET', 'POST'])
def fetch_user():
    mask = _fetch()
    user_fields = User.get_fields()
    response = {member.user.id: {f: getattr(member.user, f) for f in user_fields} for member in mask}
    # response = {}
    # for member in mask:
    #     response[member.user.id] = {
    #         'username': member.user.username,
    #         'telegram_id': member.user.telegram_id,
    #         'phone_number': member.user.phone_number,
    #         'authenticated': member.user.authenticated,
    #         'signup_date': member.user.signup_date
    #     }

    requests.post(config["Site"]["host"] + '/create/callback', json=response)
    return jsonify(response)


@app.route('/fetch/gap', methods=['GET', 'POST'])
def fetch_gap():
    mask = _fetch()
    gap_fields = Gap.get_fields()
    response = {member.gap.id: {f: getattr(member.gap, f) for f in gap_fields} for member in mask}
    # response = {}
    # for member in mask:
    #     response[member.gap.id] = {
    #         'telegram_id': member.gap.telegram_id,
    #         'link': member.gap.link,
    #         'package_id': member.gap.package_id,
    #         'title': member.gap.title,
    #         'bio': member.gap.bio,
    #         'create_date': member.gap.create_date,
    #         'is_group': member.gap.is_group
    #     }

    requests.post(config["Site"]["host"] + '/create/callback', json=response)
    return jsonify(response)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    data = clear_data(dict(request.values))
    if result := check_attributes(data, ['phone_number', 'code']):
        return result

    user = User.get(phone_number=data['phone_number'])
    task = Task.create(
        type=5,
        status='pending',
        create_time=dt.datetime.now()
    )

    verify = Verify.create(
        user=user,
        code=data['code'],
        task=task
       )

    while True:
        time.sleep(3)
        verify = Verify.get_by_id(verify.id)
        if verify.task.status != 'pending':
            break

    if verify.task.status == 'done':
        response = {
                'task_type': 5,
                'message': '201 User authenticated',
                'phone_number': verify.user.phone_number,
                'code': verify.code
            }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            201
        )

    else:
        response = {
                "message": '500 User Not Authenticated',
                "severity": "danger"
            }

        requests.post(config["Site"]["host"] + '/create/callback', json=response)
        return make_response(
            jsonify(response),
            500
        )



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
