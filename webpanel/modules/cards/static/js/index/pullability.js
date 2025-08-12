document.addEventListener("DOMContentLoaded", () => {
  const main = document.querySelector(".main");

  // Delegate click event for dynamically loaded .pullable-btn buttons
  main.addEventListener("click", e => {
    if (e.target.classList.contains("pullable-btn")) {
      const cardId = e.target.dataset.id;
      fetch("/api/cards/set_pullable", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ "card_id": cardId })
      })
        .then(res => {
          if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
          return res.text();
        })
        .then(data => {
          loadCards(); // Reload cards to reflect changes
        })
        .catch(err => {
          console.error("Failed to toggle pullable status:", err);
        });
    }});
});