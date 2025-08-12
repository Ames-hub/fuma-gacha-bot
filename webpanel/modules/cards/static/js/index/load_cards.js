function loadCards() {
  const main = document.querySelector(".main");

  fetch("/api/cards/list")
    .then(res => {
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
      return res.json();
    })
    .then(data => {
      main.innerHTML = ""; // Clear existing cards
      let cards = data.cards || [];

      cards.forEach(card => {
        const cardDiv = document.createElement("div");
        let pullable_txt = card.pullable ? "✅" : "❌";
        cardDiv.className = "card";
        cardDiv.innerHTML = `
          <h3>${card.name} ${pullable_txt}</h3>
          <p>${card.description}</p>
          <div class="card-actions">
            <button data-id="${card.identifier}" class="delete-btn">Delete</button>
            <a href="/cards/${card.identifier}" class="manage-btn">Manage</a>
            <button data-id="${card.identifier}" class="pullable-btn">Toggle Pullable</button>
          </div>
        `;
        main.appendChild(cardDiv);
      });

      main.addEventListener("click", e => {
        if (e.target.classList.contains("delete-btn")) {
          console.log("Delete card:", e.target.dataset.id);
        } else if (e.target.classList.contains("manage-btn")) {
          console.log("Manage card:", e.target.dataset.id);
        }
      });
    })
    .catch(err => {
      console.error("Failed to load cards:", err);
      main.innerHTML = "<p>Could not load cards.</p>";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadCards();
});