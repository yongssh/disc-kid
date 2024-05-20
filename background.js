// Listen for tab updates
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    // Check if the tab has finished loading
    if (changeInfo.status === 'complete') {
        // Do something when the tab finishes loading
        console.log('Tab finished loading:', tab.url);
    }
});