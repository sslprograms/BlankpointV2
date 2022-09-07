function create_account() {
    var xml = new XMLHttpRequest();
    var data = new FormData();

    xml.open("POST", "/v2/create-account");
    xml.setRequestHeader("x-csrf-token", solveChallenge());
    data.append(
        "data[username]",
        document.getElementById("username").value
    );
    data.append(
        "data[password]",
        document.getElementById("password").value
    );
    
    xml.withCredentials = true;
    xml.send(data);

    xml.onload = function() {
        if (xml.status != 200) {
            document.getElementById("error").innerText = JSON.parse(xml.response)['message'];
            document.getElementById("error").style.backgroundColor = 'rgb(247, 89, 89)';
            document.getElementById("error").style.display = 'flex';
        } else {
            window.location.reload();
        }
    }

}