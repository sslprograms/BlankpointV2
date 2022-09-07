function solveChallenge() {

    var a=sessionStorage.getItem('a');
    var b=sessionStorage.getItem('b');
    var csrf=sessionStorage.getItem('x-csrf-token');

    var answer=a*b/1.5*2;

    return csrf + '/' + Math.round(answer.toString());

}

function ping(placeId, token) {
    var xml = new XMLHttpRequest();
    var data = new FormData();

    xml.open('PATCH', '/v2/'+placeId+'/ping')
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    data.append('verify', token)
    xml.withCredentials =true 
    xml.send(data)

    xml.onload = function() {
        var token = xml.getResponseHeader('v')
        setTimeout(ping.bind(0, placeId, token), 10000)

    }
}

function joinGame(placeId) {
    var xml = new XMLHttpRequest();
    var data = new FormData();

    xml.open('POST', '/v2/requestGameJoin')
    data.append('gameId', placeId)
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    xml.withCredentials =true 
    xml.send(data)

    xml.onload = function() {
        var token = xml.getResponseHeader('v')
        setTimeout(ping.bind(0, placeId, token), 10000)
    }

}

function presence() {
    var xml = new XMLHttpRequest();
    xml.open("POST", "/v2/presence");
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    xml.withCredentials =true 
    xml.send();
    
    setTimeout(presence, 60000)
}


presence()
