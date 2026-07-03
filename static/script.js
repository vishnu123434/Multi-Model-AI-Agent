const chatForm = document.getElementById("chat-form");
const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const fileInput = document.getElementById("file");
const fileName = document.getElementById("file-name");


fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
    } else {
        fileName.textContent = "No file selected";
    }
});


function addTextMessage(sender, text, className) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", className);

    const labelDiv = document.createElement("div");
    labelDiv.classList.add("message-label");
    labelDiv.textContent = sender;

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");
    contentDiv.textContent = text;

    messageDiv.appendChild(labelDiv);
    messageDiv.appendChild(contentDiv);

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    return messageDiv;
}


function addUserMessageWithImage(text, file) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "user-message");

    const labelDiv = document.createElement("div");
    labelDiv.classList.add("message-label");
    labelDiv.textContent = "You";

    messageDiv.appendChild(labelDiv);

    if (file) {
        const img = document.createElement("img");
        img.classList.add("user-image-preview");
        img.src = URL.createObjectURL(file);
        img.alt = file.name;
        messageDiv.appendChild(img);
    }

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");
    contentDiv.textContent = text || "Uploaded image";

    messageDiv.appendChild(contentDiv);

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    return messageDiv;
}


chatForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = messageInput.value.trim();
    const file = fileInput.files[0];

    if (!message && !file) {
        alert("Please enter a message or upload an image.");
        return;
    }

    addUserMessageWithImage(message, file);

    const loadingMessage = addTextMessage("AI", "Thinking...", "bot-message");
    loadingMessage.classList.add("loading");

    const formData = new FormData();
    formData.append("message", message);

    if (file) {
        formData.append("file", file);
    }

    messageInput.value = "";
    fileInput.value = "";
    fileName.textContent = "No file selected";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            body: formData
        });

        let data;

        try {
            data = await response.json();
        } catch (jsonError) {
            throw new Error("Server returned invalid JSON. Check Flask terminal.");
        }

        loadingMessage.classList.remove("loading");

        const contentDiv = loadingMessage.querySelector(".message-content");

        if (data.success) {
            contentDiv.textContent = data.response;
        } else {
            contentDiv.textContent = data.response || "Something went wrong.";
        }

    } catch (error) {
        loadingMessage.classList.remove("loading");

        const contentDiv = loadingMessage.querySelector(".message-content");
        contentDiv.textContent = `Error: ${error.message}`;
    }
});