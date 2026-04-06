const reserveButtons = document.querySelectorAll("button.secondary-button");

reserveButtons.forEach((button) => {
  button.addEventListener("click", () => {
    button.textContent = "Reserved!";
    button.disabled = true;
  });
});
