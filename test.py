api = 'https://catalog.api.gamedistribution.com/api/v2.0/rss/All/?collection=best&categories=All&tags=All&subType=all&type=all&mobile=all&rewarded=all&amount=100&page=1&format=json'


import requests
import json, string, random


games = json.loads(
    open('games.json', 'r').read()
)

game = requests.get(
    api
).json()

for g in game:

    download = requests.get(
        g['Asset'][1]
    )

    for chunk in download.iter_content(chunk_size=None):
        if chunk:
            name = ''.join(
                random.choices(
                    string.ascii_letters + string.digits,
                    k=8
                )
            ) + '.jpg'
            open(f'static/{name}', 'wb').write(chunk)

    d = {
        'name':g['Title'],
        'img':f'/static/{name}',
        'src':g['Url'],
        'id':len(games)+1
    }

    games.append(d)

open('games.json', 'w').write(json.dumps(games,indent=3))


