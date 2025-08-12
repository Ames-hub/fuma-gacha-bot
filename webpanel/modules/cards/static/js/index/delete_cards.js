document.addEventListener("DOMContentLoaded", () => {
  document.querySelector(".main").addEventListener("click", async e => {
    if (e.target.tagName === "BUTTON" && e.target.textContent.trim() === "Delete") {
      const cardEl = e.target.closest(".card");
      const cardId = e.target.dataset.id;

      if (!cardId) {
        console.error("Card has no ID set");
        return;
      }

      try {
        const res = await fetch("/api/cards/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: cardId })
        });

        if (!res.ok) throw new Error(`Delete failed (${res.status})`);

        // Remove from DOM on success
        cardEl.remove();
        console.log(`Card ${cardId} deleted`);
      } catch (err) {
        console.error("Error deleting card:", err);
      }
    }
  });
});
