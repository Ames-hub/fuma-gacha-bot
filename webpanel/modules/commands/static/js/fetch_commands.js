async function fetchCommands() {
    try {
        const token = new URLSearchParams(window.location.search).get('token');
        const res = await fetch(`/api/commands/list`);
        const data = await res.json();

        console.log("API response:", data);

        // Convert object of commands into an array
        const commands = data.commands ? Object.values(data.commands) : [];
        const container = document.getElementById("commands-list");
        container.innerHTML = "";

        commands.forEach(cmd => {
            const card = document.createElement("div");
            card.className = "command-card";
            card.innerHTML = `
                <div class="card-header">
                    <span class="cmd-name">${cmd.identifier}</span>
                    <span class="cmd-status ${cmd.enabled ? 'enabled' : 'disabled'}">${cmd.enabled ? 'Enabled' : 'Disabled'}</span>
                </div>
                <button class="toggle-btn ${cmd.enabled ? 'enabled' : 'disabled'}" data-cmd="${cmd.identifier}">
                    ${cmd.enabled ? "Disable" : "Enable"}
                </button>
            `;
            container.appendChild(card);
        });

        // Attach toggle listeners
        document.querySelectorAll(".toggle-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const cmdId = btn.dataset.cmd;
                const res = await fetch(`/api/commands/switch/${cmdId}`);
                if (res.ok) {
                    await fetchCommands(); // refresh the list
                } else {
                    alert("Failed to switch command status.");
                }
            });
        });
    } catch (err) {
        console.error(err);
    }
}

// Initial load
fetchCommands();
