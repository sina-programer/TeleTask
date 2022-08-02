from flask import Flask, jsonify, request, make_response
import datetime as dt
import time

from database import User, Task, Gap, Member


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
                return jsonify({'message': f"you have to enter at least one of {attr}"})

        elif not data.get(attr, None):
            return jsonify({'message': f"<{attr}> is invalid"})


def _create_channel():
    if result := check_attributes(request.args, ['username', 'phone_number', 'channel_title']):
        return result

    task = Task.create(
        type=1,
        status='pending',
        create_time=dt.datetime.now()
    )

    channel = Gap.create(
        title=request.args['channel_title'],
        bio=request.args.get('channel_bio', ''),  # maybe there is not at all
        create_date=dt.date.today(),
    )

    user = User.get_or_none(
        username=request.args['username'],
        phone_number=request.args['phone_number'],
    )
    if not user:
        user = User.create(
            username=request.args['username'],
            phone_number=request.args['phone_number'],
            authenticated=False,
            signup_date=dt.date.today()
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
        return make_response(
            jsonify({
                'task_type': 1,
                'message': '201 Channel created',
                'severity': "info",
                'id': member.gap.telegram_id,
                'link': member.gap.link,
                'title': member.gap.title,
                'bio': member.gap.bio
            }),
            201
        )

    else:
        return make_response(
            jsonify({
                "message": '500 Channel not created',
                "severity": "danger"
            }),
            500
        )


def _create_group():
    if result := check_attributes(request.args, ['username', 'phone_number', 'group_title']):
        return result

    task = Task.create(
        type=2,
        status='pending',
        create_time=dt.datetime.now()
    )

    group = Gap.create(
        title=request.args['group_title'],
        bio=request.args.get('group_bio', ''),  # might there is not at all
        create_date=dt.date.today(),
        task=task
    )

    user = User.get_or_none(
        username=request.args['username'],
        phone_number=request.args['phone_number']
    )
    if not user:
        user = User.create(
            username=request.args['username'],
            phone_number=request.args['phone_number'],
            authenticated=False,
            signup_date=dt.date.today()
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
        return make_response(
            jsonify({
                'task_type': 2,
                'message': '201 Group created',
                'severity': "info",
                'id': member.gap.telegram_id,
                'link': member.gap.link,
                'title': member.gap.title,
                'bio': member.gap.bio
            }),
            201
        )

    else:
        return make_response(
            jsonify({
                "message": '500 Group Not Created',
                "severity": "danger"
            }),
            500
        )


def _create_both():
    if result := check_attributes(request.args, ['username', 'phone_number', 'title']):
        return result

    channel_task = Task.create(
        type=1,
        status='pending',
        create_time=dt.datetime.now()
    )
    group_task = Task.create(
        type=2,
        status='pending',
        create_time=dt.datetime.now()
    )

    channel = Gap.create(
        title=request.args['title'],
        bio=request.args.get('channel_bio', ''),  # might there is not at all
        create_date=dt.date.today(),
    )
    group = Gap.create(
        title=request.args['title'],
        bio=request.args.get('group_bio', ''),
        create_date=dt.date.today(),
    )

    user = User.get_or_none(
        username=request.args['username'],
        phone_number=request.args['phone_number'],
    )
    if not user:
        user = User.create(
            username=request.args['username'],
            phone_number=request.args['phone_number'],
            authenticated=False,
            signup_date=dt.date.today()
        )

    group_member = Member.create(
        user=user,
        gap=channel,
        is_admin=True,
        task=channel_task,
        add_date=dt.date.today()
    )
    channel_member = Member.create(
        user=user,
        gap=group,
        is_admin=True,
        task=group_task,
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

    if group_member.task.status == 'done' or channel_member.task.status == 'done':
        return make_response(
            jsonify({
                'task_type': 3,
                'message': '201 Channel and Group created',
                'title': channel_member.gap.title,
                'channel_id': channel_member.gap.telegram_id,
                'channel_bio': channel_member.gap.bio,
                'channel_link': channel_member.gap.link,
                'group_id': group_member.gap.telegram_id,
                'group_bio': group_member.gap.bio,
                'group_link': group_member.gap.link,
                'severity': "info"
            }),
            201
        )

    else:
        return make_response(
            jsonify({
                "message": '500 Not Created',
                "severity": "danger"
            }),
            500
        )


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "home"


@app.route('/create', methods=['GET', 'POST'])
def create():
    task_type = request.args.get('task_type', None)
    if not task_type:
        return jsonify({'message': 'Please enter task type!'})


    if task_type == '1':
        return _create_channel()

    elif task_type == '2':
        return _create_group()

    elif task_type == '3':
        return _create_both()

    else:
        return jsonify({"message": 'Please enter a valid task type!'})


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    if result := check_attributes(request.args, ['username', 'phone_number', ['channel_id', 'group_id']]):
        return result


    added_chat_ids = bot.add_user(request.args)

    if added_chat_ids:
        return make_response(
            jsonify({
                "message": '200 user added',
                "added_chat_ids": str(added_chat_ids),
                "severity": "info"
                }),
            200
        )

    else:
        return make_response(
            jsonify({
                "message": '500 User Could Not Be Added',
                "severity": "danger"
                }),
            500
        )


@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    return 'Please use /fetch/user to get users. \nYou can do the same with "gap" & "package"'


@app.route('/fetch/user', methods=['GET', 'POST'])
def fetch_user():
    return jsonify({
        'first': {
            'username': 'test_username',
            'phone_number': '+980123456789',
            'is_authenticated': True,
            'signup_date': dt.date.today()
        }
    })


@app.route('/fetch/gap', methods=['GET', 'POST'])
def fetch_gap():
    return jsonify({
        'first': {
            'title': 'test_title',
            'bio': 'lorem ipsum bio',
            'id': '012345678987654321',
            'link': 'https://www.google.com',
            'create_date': dt.date.today(),
            'task_type': 2
        }
    })


@app.route('/fetch/package', methods=['GET', 'POST'])
def fetch_package():
    return jsonify({
        'first': {
            'teacher': 'test_teacher',
            'student': 'test_student',
            'expire_date': dt.date.today() + dt.timedelta(days=100),
            'signup_date': dt.date.today(),
            'description': 'long text',
            'title': 'NewPackage',
            'channel': 'my channel',
            'group': 'my group'
        }
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
