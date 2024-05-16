document.addEventListener('DOMContentLoaded', function() {
    // Add click event listener to the "Open Wordle" button
    document.getElementById('aboutKID').addEventListener('click', function() {
        // Open a new tab to the Wordle game
        chrome.tabs.create({ url: "https://kidsindanger.org" });
    });
    document.getElementById("contactKID").addEventListener('click', function(){
        // email pop up
        var mailtoUrl = "mailto:email@kidsindanger.org" ;
        window.open(mailtoUrl);
    })
});
