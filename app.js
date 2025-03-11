document.addEventListener("DOMContentLoaded", () => {
    fetch("/fetch_schema") // Fetch database schema on page load
        .then(res => res.json())
        .then(data => {
            document.getElementById("intro").innerText = data.message;
        });

    document.getElementById("send").addEventListener("click", async () => {
        let chatbox = document.getElementById("chatbox");
        let userMessage = chatbox.value.trim();
        if (!userMessage) return;

        let chatHistory = localStorage.getItem("chatHistory") || "";
        chatHistory += `User: ${userMessage}\n`;
        localStorage.setItem("chatHistory", chatHistory);

        let response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage, chatHistory: chatHistory })
        });

        let data = await response.json();
        chatbox.value = ""; // Clear input box
        chatHistory += `AI: ${data.reply}\n`;
        localStorage.setItem("chatHistory", chatHistory);

        if (userMessage.toLowerCase() === "go") {
            let sqlResponse = await fetch("/execute_sql", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chatHistory: chatHistory })
            });

            let sqlData = await sqlResponse.json();
            let graphResponse = await fetch("/generate_graph", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ dataset: sqlData.dataset })
            });

            let graphData = await graphResponse.json();
            document.getElementById("graphs").innerHTML += `<img src="data:image/png;base64,${graphData.image}" />`;
        }
    });
});
