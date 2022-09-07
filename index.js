function solveChallenge() {

    var a=sessionStorage.getItem('a');
    var b=sessionStorage.getItem('b');
    var csrf=sessionStorage.getItem('x-csrf-token');

    var answer=a*b/1.5*2;

    return csrf + '/' + Math.round(answer.toString());

}


function sendContact() {
    var xml = new XMLHttpRequest();
    var data = new FormData();

    xml.open("POST", "/v2/send-contact");
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    data.append(
        "data[email]",
        document.getElementById("email").value
    );
    data.append(
        "data[context]",
        document.getElementById("textarea-txt").value
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
