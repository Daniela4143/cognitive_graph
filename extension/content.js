let lastSelectedText = "";

document.addEventListener("mouseup", () => {
    const selection = window.getSelection().toString();
    if (selection) {
        lastSelectedText = selection;
    }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "getSelectedText") {
        sendResponse({ text: lastSelectedText });
    }
});