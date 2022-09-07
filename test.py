api = 'https://gamemonetize.com/rssfeed.php?format=json&category=All&type=html5&popularity=bestgames&company=All&amount=250'


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
        g['thumb']
    )

    for chunk in download.iter_content(chunk_size=None):
        if chunk:
            name = ''.join(
                random.choices(
                    string.ascii_letters + string.digits,
                    k=8
                )
            ) + '.jpg'
            open(f'static/game-images/{name}', 'wb').write(chunk)

    d = {
        'name':g['title'],
        'img':f'/static/game-images/{name}',
        'src':g['url'],
        'id':len(games)+1
    }

    games.append(d)

open('games.json', 'w').write(json.dumps(games,indent=3))


