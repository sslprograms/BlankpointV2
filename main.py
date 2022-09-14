from flask import Flask, jsonify, render_template, redirect, session, url_for, make_response, request, send_from_directory, send_file

import requests, threading, time, random, string, json

app = Flask(__name__)

accounts = json.loads(open('accounts.json', 'r').read())
games = []


for game in json.loads(open('games.json', 'r').read()):

    games.append(
        {
            "name":game['name'],
            "src":game['src'],
            "img":game['img'],
            'players':[

            ],
            "id":game['id']
        }
    )

ALLOWED = string.ascii_letters + string.digits
CSRF_TOKENS = []
RATELIMITED = []

JOIN_TOKENS = []



def save_database():

    open('accounts.json', 'w').write(json.dumps(accounts, indent=3))


ratelimit_index = {
    'comment':1,
    'signup':1,
    'login':10
}

def get_friend_from_id(player_id):

    for account in accounts:
        if account['userId'] == int(player_id):
            return account

    return {}

def get_game_from_id(gameId):
    for game in games:

        if game['id'] == int(gameId):
            return game

def getFriends(account):

    friends = []
    ids_ = account['friends']

    for friend in ids_:

        for fc in accounts:
            if fc['userId'] == friend['userId']:
                if fc['status']:
                    data = {
                        'userId':fc['userId'],
                        'pfp':fc['pfp'],
                        'status':fc['status'],
                        'usermame':fc['username']
                    }
                    friends.append(data)  
    return friends


def getFavorites(account):

    local_games = []

    for fav in account['favorites']:
        for game in games:

            if int(fav['id']) == int(game['id']):
                local_games.append(game)
    
    return local_games


def getRecents(account):

    local_games = []

    for fav in account['recent_games']:
        for game in games:

            if int(fav['id']) == int(game['id']):
                local_games.append(game)
    
    return local_games

def removePresence(account):
    time.sleep(50)
    account['status'] = 'Offline'

def removeJoinToken(token):
    time.sleep(1250)
    try:
        JOIN_TOKENS.remove(token)
    except:
        pass

def removePlayer(game, player):
    global games

    for game_ in  games:
        if game_['id'] == game['id']:
            game=game_
            if game['players'].count({"userId":player['userId']}) == 0:
                game['players'].append({"userId":player['userId']})
                time.sleep(10)
                game['players'].remove({"userId":player['userId']})
    

def checkCSRF(x_csrf_token):
    for csrf in CSRF_TOKENS:

        if csrf['token'] == x_csrf_token.split('/')[0]:

            if str(x_csrf_token.split('/')[1]) == str(round(csrf['answer'])):

                return True
            


def remove_rl(addr, type):

    time.sleep(30)

    for r in RATELIMITED:

        if r['addr'] == addr:

            r[type]['count'] -= 1

            break

def CHECK_RATELIMIT(addr, type):

    for r in RATELIMITED:

        if r['addr'] == addr:
            if r[type]['count'] >= ratelimit_index[type]:
                return True
            else:
                r[type]['count'] += 1
                threading.Thread(target=remove_rl, args=(addr,type,)).start()
                return False

    addr_data = {'addr':addr}

    for i in ratelimit_index:
        addr_data.update(
            {
                f'{i}':{
                    'count':0
                }
            }
        )

    addr_data[type]['count'] += 1


    RATELIMITED.append(addr_data)

    threading.Thread(target=remove_rl, args=(addr,type,)).start()
    return False

    


def REMOVE_CSRF(token):

    time.sleep(3600)

    CSRF_TOKENS.remove(token)


def GENERATE_CSRF_TOKEN():

    token = ''.join(
        random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=30)
    )

    a = random.randint(10, 1000)
    b = random.randint(10, 1000)

    token = {
        'token':token,
        'a':a,
        'b':b,
        'answer':a*b/1.5*2
    }

    print(token)

    CSRF_TOKENS.append(token)

    threading.Thread(target=REMOVE_CSRF, args=(token,)).start()

    return token

@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('static', 'ads.txt')

@app.route('/Ads.txt')
def ads_txt1():
    return send_from_directory('static', 'ads.txt')

@app.route('/')
def indexPage():

    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            return redirect(url_for('homePage')), 302

    csrf = GENERATE_CSRF_TOKEN()

    mc = {
        'csrf':csrf['token'],
        'a':csrf['a'],
        'b':csrf['b']
    }

    return render_template('index.html', csrf=mc['csrf'], a=mc['a'], b=mc['b']), 200

@app.route('/play/<gameId>')
def playGame(gameId):
    for account in accounts:
        if account['token'] == request.cookies.get('token'):

            csrf = GENERATE_CSRF_TOKEN()

            mc = {
                'csrf':csrf['token'],
                'a':csrf['a'],
                'b':csrf['b']
            }
            game_playing = gameId
            for game in games:

                if game['id'] == int(game_playing):
                    game_playing = game
                    break
            
            return render_template('client.html', account=account, csrf=mc['csrf'], a=mc['a'], b=mc['b'], game = game_playing), 200

    return redirect(url_for('indexPage')), 302
    
@app.route('/discover', methods=['GET'])
def discoverPage():

    def key_sort_popular(data):
        return len(data['players'])

    for account in accounts:
        if account['token'] == request.cookies.get('token'):

            csrf = GENERATE_CSRF_TOKEN()

            mc = {
                'csrf':csrf['token'],
                'a':csrf['a'],
                'b':csrf['b']
            }

            popular_games = games
            popular_games.sort(key=key_sort_popular, reverse=True)
            new_pop = []
            i_count = 0
            for i in popular_games:
                i_count += 1
                new_pop.append(i)
                if i_count >= 20:
                    break
            
            popular = new_pop


            friends_games = []
            try:
                for x in range(7):
                    friends_games.append(
                        get_game_from_id(
                            random.choice(
                                get_friend_from_id(
                                    random.choice(account['friends'])['userId']
                                )['recent_games']
                            )['id']
                        )
                    )
            except:
                pass


            new_games = json.loads(open('games.json', 'r').read())
            d = []
            new_games.reverse()

            for g in new_games:
                for game in games:

                    if game['id'] == g['id']:
                        d.append(game)

            new_games = d

            # new_games.reverse() New games are last in a list

            newgames = []

            count = 0
            for game in new_games:
                count += 1
                newgames.append(game)

                if count >=50:
                    break
            
            suggested = []
            for x in range(50):
                suggested.append(random.choice(games))
            
            

            
            return render_template('discover.html', suggested=suggested, new_games=newgames, account=account, csrf=mc['csrf'], a=mc['a'], b=mc['b'], popular=popular, friends_playing=friends_games), 200

    return redirect(url_for('indexPage')), 302
    
# @app.route('/p/<userId>/profile')
# def profilePage(userId):
#     for account in accounts:
#         if account['token'] == request.cookies.get('token'):

#             csrf = GENERATE_CSRF_TOKEN()

#             mc = {
#                 'csrf':csrf['token'],
#                 'a':csrf['a'],
#                 'b':csrf['b']
#             }

#             suggested = []
#             for x in range(25):
#                 suggested.append(random.choice(games))


#             for user in accounts:
#                 if user['userId'] == int(userId): 
#                     userFavorites = getFavorites(user)

#                     return render_template('profile.html', userFavorites=userFavorites, user=user, csrf=mc['csrf'], account=account, suggested=suggested, a=mc['a'], b=mc['b']), 200

    # return redirect(url_for('indexPage')), 302

@app.route('/c', methods=['GET'])
def cPage():

    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            return redirect(url_for('homePage')), 302

    username = request.args.get('username')

    if username == None:

        username = ''

    csrf = GENERATE_CSRF_TOKEN()

    mc = {
        'csrf':csrf['token'],
        'a':csrf['a'],
        'b':csrf['b']
    }

    return render_template('c.html', csrf=mc['csrf'], a=mc['a'], b=mc['b'], username=username), 200


@app.route('/home', methods=['GET'])
def homePage():
    for account in accounts:
        if account['token'] == request.cookies.get('token'):

            csrf = GENERATE_CSRF_TOKEN()

            mc = {
                'csrf':csrf['token'],
                'a':csrf['a'],
                'b':csrf['b']
            }

            suggested = []
            for x in range(25):
                suggested.append(random.choice(games))


            friends = getFriends(account)
            favorites = getFavorites(account)
            recents = getRecents(account)
            recents.reverse()
            favorites.reverse()

            
            return render_template('home.html', csrf=mc['csrf'], client=account, suggested=suggested, recents = recents, favorites=favorites, a=mc['a'], b=mc['b'], friends=friends), 200

    return redirect(url_for('indexPage')), 302

@app.route('/settings')
def settingsPage():
    for account in accounts:
        if account['token'] == request.cookies.get('token'):

            csrf = GENERATE_CSRF_TOKEN()

            mc = {
                'csrf':csrf['token'],
                'a':csrf['a'],
                'b':csrf['b']
            }

            suggested = []
            for x in range(25):
                suggested.append(random.choice(games))

            
            return render_template('settings.html', csrf=mc['csrf'], account=account, suggested=suggested, a=mc['a'], b=mc['b']), 200

    return redirect(url_for('indexPage')), 302

@app.route('/l', methods=['GET'])
def lPage():

    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            return redirect(url_for('homePage')), 302



    csrf = GENERATE_CSRF_TOKEN()

    mc = {
        'csrf':csrf['token'],
        'a':csrf['a'],
        'b':csrf['b']
    }

    return render_template('l.html', csrf=mc['csrf'], a=mc['a'], b=mc['b']), 200




# API

@app.route('/v2/login', methods=['POST'])
def loginAPI():

    # s = CHECK_RATELIMIT(request.remote_addr, 'login')

    # if s!=False:
    #     return jsonify({'message':"Sorry, try again later to perform this action!"}),429

    username = request.form.get('data[username]').lower()
    password = request.form.get('data[password]')

    for account in accounts:

        if account['username'] == username:

            if account['password'] == password:

                mr = make_response(jsonify({}), 200)

                mr.set_cookie('token', account['token'])

                return mr
    
    return {'message':'Login details are not valid, try again!'}, 400




@app.route('/v2/send-contact', methods=['POST'])
def send_comment_api():

    if len(request.form.get('data[context]')) < 30:
        return jsonify({'message':"You need a minimum of 30 characters to send us a message!"}),400

    if len(request.form.get('data[email]')) <= 0:
        return jsonify({'message':"This is not a valid email!"}),400


    s = CHECK_RATELIMIT(request.remote_addr, 'comment')

    if s!=False:
        return jsonify({'message':"Sorry, try again later to perform this action!"}),429

    x_csrf_token = request.headers.get('x-csrf-token')

    for csrf in CSRF_TOKENS:

        if csrf['token'] == x_csrf_token.split('/')[0]:

            if str(x_csrf_token.split('/')[1]) == str(round(csrf['answer'])):

                email = request.form.get('data[email]')
                context = request.form.get('data[context]')

                send = requests.post(
                    'https://discord.com/api/webhooks/957760450790051871/djlIoCOfBeOX89_69uvlk6O9okDzF3NJVQxSuVji8PYb4oEpCes8tEmooiTLGFYlBfY1',
                    json ={
                        'content':'```\n' + f'Email: {email}\n\nContext: {context}' + '\n```\n@here'
                    }
                )

                

                return jsonify({'message':'We have received your message!'}), 200

    
    return jsonify({'message':"We could not authenticate you!"}),400


@app.route('/v2/create-account', methods=['POST'])
def createAccount():

    account_token = ''.join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits,
            k = random.randint(10, 20)
        )
    ) + '.' + ''.join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits,
            k = 15
        )
    )

    x_csrf_token = request.headers.get('x-csrf-token')

    for csrf in CSRF_TOKENS:

        if csrf['token'] == x_csrf_token.split('/')[0]:

            if str(x_csrf_token.split('/')[1]) == str(round(csrf['answer'])):

                username = request.form.get('data[username]').lower()
                password = request.form.get('data[password]')

                if len(username) < 3 or len(username) > 20:
                    return jsonify({'message':"Username must be between 3-20 characters!"}),400


                if username == None:

                    return jsonify({'message':"You need to provide a username to create an account!"}),400


                for account in accounts:
                    if account['username'] == username:
                        return jsonify({'message':"Sorry, this username is already taken!"}),400
                    if account['token'] == account_token:
                        return jsonify({'message':"Something went wrong, refresh the page and try again!"}),400
                
                for character in username:

                    if ALLOWED.count(character) < 1:

                        return jsonify({'message':"Characters and numbers are only allowed! (Username)"}), 400

                for character in password:

                    if ALLOWED.count(character) < 1:

                        return jsonify({'message':"Characters and numbers are only allowed! (Password)"}), 400

                # s = CHECK_RATELIMIT(request.remote_addr, 'signup')

                # if s!=False:
                #     return jsonify({'message':"Sorry, try again later to perform this action!"}),429
                
                account_data = {
                    'username':username,
                    'password':password,
                    'token':account_token,
                    'friends':[

                    ],

                    'friend_requests':[

                    ],

                    'followers':[

                    ],

                    'following':[

                    ],

                    'messages':[

                    ],
                    
                    'requests_sent':[

                    ],
                    
                    'favorites':[

                    ],

                    'badges':[

                    ],

                    'recent_games':[

                    ],

                    "profile_comments":[

                    ],

                    'admin':False,
                    
                    'addr':request.remote_addr,
                    
                    'pfp':'/static/unkown.jpg',

                    'status':'Offline',
                    
                    'last_seen':'Dashboard',
                    
                    'description':'This is your description, you can change this easily in your settings or profile tab!',

                    'premium':False,
                    
                    'verified_not_robot':False,

                    'email':'',
                    
                    'userId':len(accounts)+1
                }

            accounts.append(account_data)
            save_database()


            mr = make_response(jsonify({'message':'Account was successfully created!'}), 200)
            mr.set_cookie('token', account_data['token'])

            return mr


@app.route('/v2/presence', methods=['POST'])
def setPrecense():
    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            if checkCSRF(request.headers.get('x-csrf-token')) == True:
                threading.Thread(target=removePresence,args=(account,)).start()
                account['status'] = 'Online'
                return jsonify({'success':True})

    return jsonify({'success':False})

@app.route('/v2/favorite', methods=['POST'])
def favoriteGame():
    placeId = request.args.get('placeId')

    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            if checkCSRF(request.headers.get('x-csrf-token')) == True:

                for game in games:

                    if game['id'] == int(placeId):
                        index={'id':placeId}
                        if account['favorites'].count(index) > 0:
                            account['favorites'].remove(index)
                        else:

                            account['favorites'].append(index)
                        
                        save_database()

                        return jsonify({'success':True}), 200
    return jsonify({'success':False}), 400



@app.route('/v2/profile', methods=['PATCH'])
def changeProfile():
    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            if checkCSRF(request.headers.get('x-csrf-token')) == True:

                profile_url = request.form.get('pfp')

                if profile_url != None:

                    account['pfp'] = profile_url
                
                
                save_database()
                return account
    
    return redirect(url_for('indexPage'))



@app.route('/v2/favorites', methods=['GET'])
def favorites_req():

    for account in accounts:

        if account['token'] == request.cookies.get('token'):
            favs = []

            for x in account['favorites']:
                favs.append(str(x['id']))

            return jsonify(favs)


@app.route('/v2/requestGameJoin', methods=['POST'])
def requestGameJoin():
    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            gameId = request.form.get('gameId')


            for game in games:
                if game['id'] == int(gameId):
                    game = game
                    break

            recents = account['recent_games']

            if len(recents) >= 8:
                account['recent_games'] = []
            
            try:
                if recents[0]['id'] != str(game['id']):

                    account['recent_games'].append(
                        {
                            "id":str(game['id'])
                        }
                    )
            except:
                account['recent_games'].append(
                    {
                        "id":str(game['id'])
                    }
                )

            
            # account['recent_games'].reverse()


            if checkCSRF(request.headers.get('x-csrf-token')) == True:

                token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=350))

                mr = make_response('')
                mr.headers.add_header('v', token)

                JOIN_TOKENS.append(token)
                threading.Thread(target=removePlayer, args=(game, account,)).start()
                threading.Thread(target=removeJoinToken, args=(token,)).start()
                save_database()
                return mr

    return '', 404



@app.route('/v2/<gameId>/ping', methods=['PATCH'])
def pingGame(gameId):
    global games
    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            if checkCSRF(request.headers.get('x-csrf-token')) == True:

                for game in games:

                    if int(gameId) == game['id']:

                        verify_token = request.form.get('verify')
                        

                        if JOIN_TOKENS.count(verify_token) != 0:
                            JOIN_TOKENS.remove(verify_token)
                            threading.Thread(target=removePlayer, args=(game, account,)).start()
                            token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=350))
                            JOIN_TOKENS.append(token)
                            mr = make_response('')
                            mr.headers.add_header('v', token)
                            threading.Thread(target=removeJoinToken, args=(token,)).start()
                            return mr
    return '', 404


@app.route('/v2/settings/save', methods=['POST'])
def saveSettings():

    description_new = request.form.get('description')
    username_new = request.form.get('username').lower()

    
    for character in username_new:

        if ALLOWED.count(character) < 1:

            return jsonify({'message':"Characters and numbers are only allowed! (Username)"}), 400

    for account in accounts:

        if account['token'] == request.cookies.get('token'):

            if checkCSRF(request.headers.get('x-csrf-token')) == True:
                
                if len(username_new) < 3 or len(username_new) > 20:
                    return jsonify({'message':"Username must be between 3-20 characters!"}),400


                if username_new == None:

                    return jsonify({'message':"You need to provide a username to create an account!"}),400

                if username_new != account['username']:
                    for account_check in accounts:
                        if account_check['username'] == username_new:
                            return jsonify({'message':"Sorry, this username is already taken!"}),400
                    
                    account['username'] = username_new


            if len(description_new) > 500:
                return jsonify({'message':"Keep your description under 500 Characters!"}),400

            account['description'] = description_new

            return jsonify({'message':'Account Settings Saved!'}), 200
    

    return jsonify({'message':'Unauthenticated'}), 400
    

@app.route('/v2/logout')
def logoutLink():
    mr = make_response(redirect(url_for('indexPage')))
    mr.set_cookie('token', '')
    return mr



# app.run(debug=False, host='0.0.0.0', port=80)
app.run(debug=True)