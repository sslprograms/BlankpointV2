function solveChallenge() {

    var a=sessionStorage.getItem('a');
    var b=sessionStorage.getItem('b');
    var csrf=sessionStorage.getItem('x-csrf-token');

    var answer=a*b/1.5*2;

    return csrf + '/' + Math.round(answer.toString());

}

function post_comment(userId) {
    var xml = new XMLHttpRequest();
    var data = new FormData();

    xml.open("POST", "/v2/profile-comment");
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    data.append(
        "comment",
        document.getElementById("comment-space").value
    );
    data.append(
        "userId",
        userId
    );
    
    xml.withCredentials = true;
    xml.send(data);


    xml.onload = function() {
        if (xml.status != 200) {
            document.getElementById("error").innerText = JSON.parse(xml.response)['message'];
            document.getElementById("error").style.backgroundColor = 'rgb(247, 89, 89)';
            document.getElementById("error").style.display = 'flex';
        } else {
            document.getElementById("error").innerText = JSON.parse(xml.response)['message'];
            document.getElementById("error").style.backgroundColor = '#00ff7f';
            document.getElementById("error").style.display = 'flex';
        }
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


presence()
