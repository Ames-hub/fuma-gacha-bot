document.addEventListener("DOMContentLoaded", () => {
	const btnDelete = document.getElementById("btn-delete");
	if (!btnDelete) return;

	btnDelete.addEventListener("click", async () => {
		// Get card ID from the info row
		let cardId = null;
		const infoRows = document.querySelectorAll('.info-row');
		for (const row of infoRows) {
			const label = row.querySelector('.label');
			if (label && label.textContent.trim() === 'ID:') {
				const value = row.querySelector('.value');
				if (value) {
					cardId = value.textContent.trim();
					break;
				}
			}
		}
		if (!cardId) {
			console.error("Card ID not found on page.");
			return;
		}

		if (!confirm("Are you sure you want to delete this card? This action cannot be undone.")) {
			return;
		}

		try {
			const res = await fetch("/api/cards/delete", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ id: cardId })
			});

			if (!res.ok) throw new Error(`Delete failed (${res.status})`);

			// Redirect to card list or home page on success
			window.location.href = "/cards";
		} catch (err) {
			console.error("Error deleting card:", err);
		}
	});
});
