document.addEventListener("DOMContentLoaded", () => {
    const chatbox = document.getElementById("chatbox");
    const output = document.getElementById("output");
    const sendButton = document.getElementById("send");
    const initialQueryButton = document.getElementById("initial-query");
    const kpiQueryButton = document.getElementById("kpi-query");

    // Initial Database Schema Fetch
    initialQueryButton.addEventListener("click", async () => {
        output.innerHTML = "Fetching database schema...";
        try {
            let response = await fetch("https://fabs-ai-bi.fly.dev/fetch_schema");
            let data = await response.json();
            output.innerHTML = `<strong>Schema Summary:</strong><br>${data.message}`;
            kpiQueryButton.disabled = false; // Enable KPI Query button after schema is fetched
        } catch (error) {
            output.innerHTML = "Error fetching schema. Please try again.";
        }
    });

    // Send Chat (For general questions)
    sendButton.addEventListener("click", async () => {
        let userMessage = chatbox.value.trim();
        if (!userMessage) return;

        output.innerHTML = "Sending your question...";
        try {
            let response = await fetch("https://fabs-ai-bi.fly.dev/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage, chatHistory: "" })
            });
            let data = await response.json();
            output.innerHTML = `<strong>AI Reply:</strong><br>${data.reply}`;
        } catch (error) {
            output.innerHTML = "Error processing your question. Please try again.";
        }
    });

    // KPI Query (Creates SQL and Displays Graph)
    kpiQueryButton.addEventListener("click", async () => {
        output.innerHTML = "Generating SQL query and fetching results...";
        try {
            let sqlResponse = await fetch("https://fabs-ai-bi.fly.dev/execute_sql", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chatHistory: "Generate a SQL query to fetch KPIs." })
            });

            let sqlData = await sqlResponse.json();
            let graphResponse = await fetch("https://fabs-ai-bi.fly.dev/generate_graph", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ dataset: sqlData.dataset })
            });

            let graphData = await graphResponse.json();
            document.getElementById("graphs").innerHTML = `<img src="data:image/png;base64,${graphData.image}" />`;
            output.innerHTML = "Graph generated successfully!";
        } catch (error) {
            output.innerHTML = "Error generating SQL or graph. Please try again.";
        }
    });
});
