document.addEventListener('DOMContentLoaded', function() {

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


// visible only if recall detected (similarity score high enough

document.addEventListener('DOMContentLoaded', function() {
    // Assume this variable determines whether the recall warning is triggered
    let recallBool = false;

    // **TO-DO**:
    // need to be implemented:
    // if recall-matching returns results, then set recallBool to True
    

    // Function to toggle the visibility of the warning div based on the variable
    function toggleContentVisibility() {
        const conditionalContent = document.getElementById('warning-triggered');
        if (recallBool) {
            conditionalContent.style.display = 'block'; // show recall warning
        } else {
            conditionalContent.style.display = 'none'; // hide recall warning
        }
    }
    // Call the function initially to set the initial visibility state
    toggleContentVisibility();
});

