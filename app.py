from utils import *


@app.route('/', methods=['GET'])
def home():
    return "home"


@app.route('/create', methods=['GET', 'POST'])
def create_ch_group():
    request_data = request.get_json()
    return jsonify('ok')

    if 'task_type' not in request_data:
        data = {'message': 'Task type can not be empty'}
        return jsonify(data)

    task_type = int(request_data['task_type'])
    if request.method == 'POST':

        if (task_type == 1):
            if 'username' not in request_data:
                data = {'message': 'username can not be empty'}
                return jsonify(data)

            if 'phone_number' not in request_data:
                data = {"message": 'phone number can not be empty'}
                return jsonify(data)

            if 'channel_title' not in request_data:
                data = {"message": 'channel can not be empty'}
                return jsonify(data)

            username = request_data['username']
            phone_number = request_data['phone_number']
            channel_title = request_data['channel_title']
            channel_bio = request_data['channel_bio'] if 'channel_bio' in request_data else ''

            if len(username) == 0:
                data = {"message": 'username can not be an empty string'}
                return jsonify(data)

            if len(phone_number) == 0:
                data = {"message": 'phone_number can not be an empty string'}
                return jsonify(data)

            if len(channel_title) == 0:
                data = {"message": 'channel_title can not be an empty string'}
                return jsonify(data)

            inserted_id = actions_collection.insert_one({
                "username": username,
                "phone_number": phone_number,
                "channel_title": channel_title,
                "channel_bio": channel_bio,
                'type': task_type,
                'status': 'waiting',
                'insert_date': datetime.now()
            }).inserted_id
            if inserted_id:
                response = make_response(
                    jsonify(
                        {"message": '201 Channel created', "severity": "info"}
                    ),
                    201,
                )
            else:
                response = make_response(
                    jsonify(
                        {"message": '500 Channel not created', "severity": "danger"}
                    ),
                    500,
                )
        if (task_type == 2):
            if 'group_title' not in request_data:
                data = {"message": 'Group title can not be empty'}
                return jsonify(data)

            if 'username' not in request_data:
                data = {"message": 'username can not be empty'}
                return jsonify(data)

            if 'phone_number' not in request_data:
                data = {"message": 'Phone number can not be empty'}
                return jsonify(data)

            username = request_data['username']
            phone_number = request_data['phone_number']
            group_title = request_data['group_title']
            group_bio = request.json.get('group_bio') if 'group_bio' in request_data else ''

            if len(username) == 0:
                data = {"message": 'username can not be an empty string'}
                return jsonify(data)

            if len(phone_number) == 0:
                data = {"message": 'phone_number can not be an empty string'}
                return jsonify(data)

            if len(group_title) == 0:
                data = {"message": 'group_title can not be an empty string'}
                return jsonify(data)

            inserted_id = actions_collection.insert_one({
                "username": username,
                "phone_number": phone_number,
                "group_title": group_title,
                "group_bio": group_bio,
                'status': 'waiting',
                'type': task_type,
                'insert_date': datetime.now()
            }).inserted_id

            if inserted_id:
                response = make_response(
                    jsonify(
                        {"message": '201 Group created', "severity": "danger"}
                    ),
                    201,
                )
            else:
                response = make_response(
                    jsonify(
                        {"message": '500 Group Not Created', "severity": "danger"}
                    ),
                    500
                )

        if (task_type == 3):
            if 'group_title' not in request_data:
                data = {"message": 'group_title can not be empty'}
                return jsonify(data)

            if 'channel_title' not in request_data:
                data = {"message": 'channel_title can not be empty'}
                return jsonify(data)

            if 'username' not in request_data:
                data = {"message": 'username can not be empty'}
                return jsonify(data)

            if 'phone_number' not in request_data:
                data = {"message": 'phone_number can not be empty'}
                return jsonify(data)

            username = request_data['username']
            phone_number = request_data['phone_number']
            channel_title = request_data['channel_title']
            channel_bio = request_data['channel_bio'] if 'channel_bio' in request_data else ''
            group_title = request_data['group_title']
            group_bio = request.json.get('group_bio') if 'group_bio' in request_data else ''

            if len(username) == 0:
                data = {"message": 'username can not be an empty string'}
                return jsonify(data)

            if len(phone_number) == 0:
                data = {"message": 'phone_number can not be an empty string'}
                return jsonify(data)

            if len(group_title) == 0:
                data = {"message": 'group_title can not be an empty string'}
                return jsonify(data)

            if len(channel_title) == 0:
                data = {"message": 'channel_title can not be an empty string'}
                return jsonify(data)

            inserted_id = actions_collection.insert_one({
                "username": username,
                "phone_number": phone_number,
                "group_title": group_title,
                "group_bio": group_bio,
                "channel_title": channel_title,
                "channel_bio": channel_bio,
                'status': 'waiting',
                'type': task_type,
                'insert_date': datetime.now()
            }).inserted_id

            if inserted_id:
                response = make_response(
                    jsonify(
                        {"message": '201 Channel and Group created', "severity": "danger"}
                    ),
                    201,
                )
            else:
                response = make_response(
                    jsonify(
                        {"message": '500 Not Created', "severity": "danger"}
                    ),
                    500
                )

        return response


    else:
        return jsonify({'message': 'method not supported :('})


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    request_data = request.get_json()

    # if 'channel_id' or 'group_id' not in request_data:
    #     data = {'message':'Enter a channel id or group id'}
    #     return jsonify(data)

    if request.method == 'POST':
        if 'username' not in request_data:
            data = {'message': 'username can not be empty'}
            return jsonify(data)

        if 'phone_number' not in request_data:
            data = {"message": 'phone number can not be empty'}
            return jsonify(data)

        username = request_data['username']
        phone_number = request_data['phone_number']
        group_id = int(request_data['group_id']) if 'group_id' in request_data else 0
        channel_id = int(request_data['channel_id']) if 'channel_id' in request_data else 0

        if len(username) == 0:
            data = {"message": 'username can not be an empty string'}
            return jsonify(data)

        if len(phone_number) == 0:
            data = {"message": 'phone_number can not be an empty string'}
            return jsonify(data)

        if len(group_id) == 0 and len(channel_id) == 0:
            data = {"message": 'You must at least enter one id/channel or group'}
            return jsonify(data)

        inserted_id = actions_collection.insert_one({
            "username": username,
            "phone_number": phone_number,
            "group_id": group_id,
            "channel_id": channel_id,
            'type': 4,
            'status': 'waiting',
            'insert_date': datetime.now()
        }).inserted_id

        if inserted_id:
            response = make_response(
                jsonify(
                    {"message": '200 user added', "severity": "info"}
                ),
                200,
            )
        else:
            response = make_response(
                jsonify(
                    {"message": '500 User Could Not Be Added', "severity": "danger"}
                ),
                500
            )

        return response
    else:
        return jsonify({'message': 'method not supported :('})



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
