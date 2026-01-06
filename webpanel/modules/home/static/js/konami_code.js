// Konami Code
const code = [
  "ArrowUp","ArrowUp","ArrowDown","ArrowDown",
  "ArrowLeft","ArrowRight","ArrowLeft","ArrowRight",
  "b","a"
];

let i = 0;
let explosionMode = false;

// ---- Konami listener ----
window.addEventListener("keydown", e => {
  if (e.key === code[i]) {
    i++;
    if (i === code.length) {
      triggerKonamiEffect();
      i = 0;
    }
  } else {
    i = 0;
  }
});

function triggerKonamiEffect() {
  explosionMode = true;
  document.body.classList.add("explosion-mode");

  setTimeout(() => {
    explosionMode = false;
    document.body.classList.remove("explosion-mode");
  }, 15000);
}

// ---- Click interceptor (capture phase) ----
document.addEventListener("click", e => {
  if (!explosionMode) return;

  e.preventDefault();
  e.stopPropagation();
  e.stopImmediatePropagation();

  const target = e.target;

  if (
    target === document.body ||
    target.classList.contains("shard") ||
    ["HTML", "BODY"].includes(target.tagName)
  ) return;

  explodeElement(target);
}, true);

// ---- Explosion logic ----
function explodeElement(el) {
  const rect = el.getBoundingClientRect();
  const pieces = 12;

  el.style.visibility = "hidden";

  for (let i = 0; i < pieces; i++) {
    const shard = document.createElement("div");
    shard.className = "shard";

    const size = Math.max(rect.width, rect.height) / 4;

    shard.style.width = `${size}px`;
    shard.style.height = `${size}px`;
    shard.style.left = `${rect.left + rect.width / 2}px`;
    shard.style.top = `${rect.top + rect.height / 2}px`;

    const angle = Math.random() * Math.PI * 2;
    const velocity = 120 + Math.random() * 180;

    shard.style.setProperty("--dx", `${Math.cos(angle) * velocity}px`);
    shard.style.setProperty("--dy", `${Math.sin(angle) * velocity}px`);

    document.body.appendChild(shard);
    shard.addEventListener("animationend", () => shard.remove());
  }
}
