window.addEventListener("DOMContentLoaded", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.tabs.sendMessage(tab.id, { action: "getSelectedText" }, (response) => {
        if (response && response.text) {
            document.getElementById("inputText").value = response.text;
        }
    });
});

document.getElementById("extractBtn").addEventListener("click", async () => {
    const text = document.getElementById("inputText").value;
    const resultDiv = document.getElementById("result");

    resultDiv.textContent = "Processing...(This may take a few seconds)";

    const response = await fetch("http://127.0.0.1:8000/extract", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: text })
    });

    const data = await response.json();
    resultDiv.textContent = "Extract finished! Node count: " + data.node_count;
});