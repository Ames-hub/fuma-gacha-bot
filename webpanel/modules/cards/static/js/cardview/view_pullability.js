document.addEventListener("DOMContentLoaded", () => {
  const btnToggle = document.getElementById("btn-toggle");
  if (btnToggle) {
    btnToggle.addEventListener("click", () => {
      // Get card ID from the page by searching for the info-row with label 'ID:'
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
        // fallback: try to get from a data attribute
        cardId = btnToggle.dataset.id;
      }
      if (!cardId) {
        console.error("Card ID not found on page.");
        return;
      }
      // First, toggle pullable status
      fetch("/api/cards/set_pullable", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ "card_id": cardId })
      })
        .then(res => {
          if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
          // After toggling, fetch the updated card data
          return fetch(`/api/cards/view/${encodeURIComponent(cardId)}`);
        })
        .then(res => {
          if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
          return res.json();
        })
        .then(card => {
          // Update DOM elements with new card data
          // Update image
          const img = document.querySelector('.card-image img');
          if (img && card.img_bytes) {
            img.src = `data:image/png;base64,${card.img_bytes}`;
            img.alt = card.name;
          }
          // Update info fields
          const updateField = (labelText, value) => {
            for (const row of infoRows) {
              const label = row.querySelector('.label');
              if (label && label.textContent.trim() === labelText) {
                const valSpan = row.querySelector('.value');
                if (valSpan) valSpan.textContent = value;
                break;
              }
            }
          };
          updateField('ID:', card.identifier);
          updateField('Name:', card.name);
          updateField('Description:', card.description);
          updateField('Rarity:', card.rarity);
          updateField('Tier:', card.tier);
          updateField('Pullable:', card.pullable ? 'Yes' : 'No');
          // Update card title
          const h2 = document.querySelector('.card-info h2');
          if (h2) h2.textContent = card.name;
          // Update toggle button text
          btnToggle.textContent = card.pullable ? 'Disable Pull' : 'Enable Pull';
        })
        .catch(err => {
          console.error("Failed to update card info:", err);
        });
    });
  }
});