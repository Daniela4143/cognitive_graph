window.addEventListener("DOMContentLoaded", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.tabs.sendMessage(tab.id, { action: "getSelectedText" }, (response) => {
        if (response && response.text) {
            document.getElementById("inputText").value = response.text;
        }
    });
});

// Show/hide the "otherNote" input field based on the selected radio button
document.querySelectorAll('input[name="reaction"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
        var otherNote = document.getElementById("otherNote");
        if (this.value === 'other') {
            otherNote.style.display = 'block';
        } else {
            otherNote.style.display = 'none';
        }
    });
});

// Button click event listener for the "Extract" button
document.getElementById("extractBtn").addEventListener("click", async () => {
    const text = document.getElementById("inputText").value;
    const resultDiv = document.getElementById("result");

    // Get the selected reaction type and optional note
    var selectedReaction = document.querySelector('input[name="reaction"]:checked');
    var reactionType = selectedReaction ? selectedReaction.value : null;
    var reactionNote = document.getElementById("otherNote").value.trim() || null;

    resultDiv.textContent = "Processing...(This may take a few seconds)";

    // local server for testing
    // const response = await fetch("http://127.0.0.1:8000/extract", {
    // remote server for production
    const response = await fetch("https://cognitive-graph-api.onrender.com/extract", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            text: text,
            reaction_type: reactionType,
            reaction_note: reactionNote
        })
    });

    const data = await response.json();
    resultDiv.textContent = "Extract finished! Node count: " + data.node_count;
});