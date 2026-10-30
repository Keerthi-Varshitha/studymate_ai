
// ----------------------------------
// 1. GET HTML ELEMENTS
// ----------------------------------

const fileInput = document.getElementById("fileInput");
const uploadArea = document.getElementById("uploadArea");
const selectedFiles = document.getElementById("selectedFiles");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");

const focusUpload = document.getElementById("focusUpload");
const focusChat = document.getElementById("focusChat");


// ----------------------------------
// 2. STORE SELECTED FILES
// ----------------------------------

let selectedDocuments = [];

let documentsProcessed = false;


// ----------------------------------
// 3. DISPLAY SELECTED FILES
// ----------------------------------

function displayFiles() {

    selectedFiles.innerHTML = "";

    selectedDocuments.forEach(file => {

        const fileItem = document.createElement("div");

        fileItem.className = "file-item";

        fileItem.textContent = "📄 " + file.name;

        selectedFiles.appendChild(fileItem);

    });

}


// ----------------------------------
// 4. SELECT FILES
// ----------------------------------

fileInput.addEventListener("change", function () {

    const newFiles = Array.from(fileInput.files);

    selectedDocuments = [
        ...selectedDocuments,
        ...newFiles
    ];

    selectedDocuments = selectedDocuments.filter(
        (file, index, self) =>
            index === self.findIndex(
                item => item.name === file.name &&
                        item.size === file.size
            )
    );

    fileInput.value = "";

    documentsProcessed = false;

    uploadStatus.textContent = "New documents selected.";

    displayFiles();

});


// ----------------------------------
// 5. DRAG AND DROP
// ----------------------------------

uploadArea.addEventListener("dragover", function (event) {

    event.preventDefault();

    uploadArea.classList.add("drag-over");

});

uploadArea.addEventListener("dragleave", function () {

    uploadArea.classList.remove("drag-over");

});

uploadArea.addEventListener("drop", function (event) {

    event.preventDefault();

    uploadArea.classList.remove("drag-over");

    const droppedFiles = Array.from(event.dataTransfer.files);

    selectedDocuments.push(...droppedFiles);

    displayFiles();

    documentsProcessed = false;

    uploadStatus.textContent = "New documents selected.";

});


// ----------------------------------
// 6. UPLOAD DOCUMENTS TO BACKEND
// ----------------------------------

uploadButton.addEventListener("click", async function () {

    if (selectedDocuments.length === 0) {

        uploadStatus.textContent = "Please select documents first.";

        return;

    }

    const formData = new FormData();

    selectedDocuments.forEach(file => {

        formData.append("files", file);

    });

    uploadButton.disabled = true;

    uploadStatus.textContent = "Processing documents...";

    try {

        const response = await fetch("/api/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(data.error || "Upload failed.");

        }

        documentsProcessed = true;

        uploadStatus.textContent = data.message;

    }

    catch (error) {

        uploadStatus.textContent = "Error: " + error.message;

    }

    finally {

        uploadButton.disabled = false;

    }

});


// ----------------------------------
// 7. DISPLAY CHAT MESSAGES
// ----------------------------------

function addMessage(message, sender, sources = []) {

    const messageRow = document.createElement("div");

    messageRow.className = "message-row " + sender;

    const messageContent = document.createElement("div");

    messageContent.className = "message-content";

    const heading = document.createElement("strong");

    heading.textContent = sender === "user"
        ? "You"
        : "StudyMate AI";

    const paragraph = document.createElement("p");

    paragraph.textContent = message;

    messageContent.appendChild(heading);

    messageContent.appendChild(paragraph);

    if (sources.length > 0) {

        const sourceList = document.createElement("div");

        sourceList.className = "source-list";

        sourceList.textContent =
            "Sources: " + sources.join(", ");

        messageContent.appendChild(sourceList);

    }

    if (sender === "assistant") {

        const avatar = document.createElement("div");

        avatar.className = "bot-avatar";

        avatar.textContent = "AI";

        messageRow.appendChild(avatar);

    }

    messageRow.appendChild(messageContent);

    chatMessages.appendChild(messageRow);

    chatMessages.scrollTop = chatMessages.scrollHeight;

}


// ----------------------------------
// 8. ASK QUESTIONS
// ----------------------------------

async function askQuestion() {

    const question = questionInput.value.trim();

    if (!question) {

        return;

    }

    if (!documentsProcessed) {

        addMessage(
            "Please upload and process your documents first.",
            "assistant"
        );

        return;

    }

    addMessage(question, "user");

    questionInput.value = "";

    sendButton.disabled = true;

    try {

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: question

            })

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(data.error || "Unable to get answer.");

        }

        addMessage(
            data.answer,
            "assistant",
            data.sources || []
        );

    }

    catch (error) {

        addMessage(
            "Error: " + error.message,
            "assistant"
        );

    }

    finally {

        sendButton.disabled = false;

    }

}


// ----------------------------------
// 9. SEND BUTTON
// ----------------------------------

sendButton.addEventListener("click", askQuestion);


// Press Enter to send.
// Shift + Enter creates a new line.

questionInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        askQuestion();

    }

});


// ----------------------------------
// 10. SIDEBAR NAVIGATION
// ----------------------------------

focusUpload.addEventListener("click", function () {

    document.getElementById("documents").scrollIntoView({

        behavior: "smooth"

    });

});

focusChat.addEventListener("click", function () {

    document.getElementById("chat").scrollIntoView({

        behavior: "smooth"

    });

});

