
function solveChallenge() {

    var a=sessionStorage.getItem('a');
    var b=sessionStorage.getItem('b');
    var csrf=sessionStorage.getItem('x-csrf-token');

    var answer=a*b/1.5*2;

    return csrf + '/' + Math.round(answer.toString());

}

function sleep(milliseconds) {
    let timeStart = new Date().getTime();
    while (true) {
        let elapsedTime = new Date().getTime() - timeStart;
        if (elapsedTime > milliseconds) {
            break;
        }
    }
}

function presence() {
    var xml = new XMLHttpRequest();
    xml.open("POST", "/v2/presence");
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    xml.send();
    setTimeout(presence, 60000)
}


function playGame(placeId) {
    window.open('/play/' + placeId, '_blank', 'new')
}



function getElementsByIds(ids) {
    var idList = ids.split(" ");
    var results = [], item;
    for (var i = 0; i < idList.length; i++) {
        item = document.getElementById(idList[i]);
        if (item) {
            results.push(item);
        }
    }
    return(results);
}

function checkIfFavorited(id) {
    var xml = new XMLHttpRequest();
    xml.open('GET','/v2/favorites')
    xml.send();

    xml.onload = function()  {
        var xmlData = JSON.parse(xml.response);
        var data = document.getElementsByName("gameIdfav_" + id)
        console.log(data)
        for (let i = 0; i < data.length; i++) {
            if (xmlData.includes(id)) {
                data[i].className = 'fi fi-sr-star';
                data[i].style.color = 'gold'
            }
        }
    }

}


function favorite(id) {
    var xml = new XMLHttpRequest();
    xml.open('POST','/v2/favorite?placeId=' + id)
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    xml.send();

    xml.onload = function() {
        if (xml.status == 200) {
            var data = document.getElementsByName("gameIdfav_" + id)
            for (let i = 0; i < data.length; i++) {
                if (data[i].className == 'fi fi-sr-star') {
                    data[i].className = 'fi fi-rr-star';
                    data[i].style.color = 'white'
                
                } else {
                    data[i].className = 'fi fi-sr-star';
                    data[i].style.color = 'gold'
                }

            }
        }
    }
}


function changePFP() {
    const client = filestack.init("Ay7PCSx4eTcGqJmNPsYFQz");

    const options = {

        accept: ["image/*"],

        onFileUploadFinished: file => {

            var xml = new XMLHttpRequest();
            xml.open('PATCH', '/v2/profile')
            xml.setRequestHeader("x-csrf-token", solveChallenge());
            
            var data = new FormData();
            data.append('pfp', file.url)

            xml.send(data)

            xml.onload = function() {
                window.location.reload();
            }

        }
    };

    client.picker(options).open();


}