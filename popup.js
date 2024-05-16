document.addEventListener('DOMContentLoaded', function() {

    // links "about KID" button to KID website
    document.getElementById('aboutKID').addEventListener('click', function() {
        chrome.tabs.create({ url: "https://kidsindanger.org" });
    });
    
    document.getElementById("contactKID").addEventListener('click', function(){
        // email pop up
        var mailtoUrl = "mailto:email@kidsindanger.org" ;
        window.open(mailtoUrl);
    })
});
