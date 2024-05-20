// initializes recallBool to false, which indicates that a recall has not been detected
let recallBool = false;
let websiteURL = "";

// sets warning div to be visible/invisible depending on if recall detected
function WarningVisibility(){
    const conditionalContent = document.getElementById('warning-triggered');
    if (recallBool) {
        conditionalContent.style.display = 'block'; // show recall warning
    } else {
        conditionalContent.style.display = 'none'; // hide recall warning
    }
}

// sets recall warning triggered
function setRecallWarningTriggered(bool) {
    recallBool = bool;
    WarningVisibility();
    alert('Possible Recall Detected'); 
}


// Example external function that detects the recall warning
function detectRecallWarning() {
    // Some logic to detect recall warning
    // For demo purposes, let's assume it detects a recall warning and sets the variable to true
    setRecallWarningTriggered(true);

    //const recall-date = access json's recall date info;
}

chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    websiteURL = tabs[0].url;
    // use `url` here inside the callback because it's asynchronous!
});


document.addEventListener('DOMContentLoaded', function() {
    // initializes recall warning visibility
    WarningVisibility();

    // links "about KID" button to KID website
    document.getElementById('aboutKID').addEventListener('click', function() {
        chrome.tabs.create({ url: "https://kidsindanger.org" });
    });

    // email pop up
    document.getElementById("contactKID").addEventListener('click', function(){
        var mailtoUrl = "mailto:email@kidsindanger.org" ;
        window.open(mailtoUrl);
    
    });
   

});

// for demo (comment out when we figure out how to write detectRecallWarning)
// Simulate detecting a recall warning after 3 seconds
    //setTimeout(detectRecallWarning, 3000);
    //setTimeout(processAmazonLink, 3000);

document.getElementById('process-button').addEventListener('click', () => {
            processAmazonLink(websiteURL);
        });

function processAmazonLink(websiteURL) {
    fetch('http://localhost:5000/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ amazon_link: amazon_link })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        document.getElementById('output').innerText = JSON.stringify(data, null, 2);
})
    .catch((error) => {
    console.error('Error:', error);
    });
}
