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


function addMessage(sender, text, className, imageUrl = null) {
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

    if (imageUrl) {
        const img = document.createElement("img");
        img.src = imageUrl;
        img.classList.add("chat-image-preview");
        messageDiv.appendChild(img);
    }

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

    let userText = message || "Uploaded image";

    let imageUrl = null;

    if (file) {
        userText += `\nFile: ${file.name}`;
        imageUrl = URL.createObjectURL(file);
    }

    addMessage("You", userText, "user-message", imageUrl);

    const loadingMessage = addMessage("AI", "Thinking...", "bot-message");
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

        const data = await response.json();

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