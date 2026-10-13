const form = document.getElementById("predict-form");
const input = document.getElementById("leaf_image");
const preview = document.getElementById("preview");
const statusBox = document.getElementById("status");
const result = document.getElementById("result");
const button = document.getElementById("predict-button");

input.addEventListener("change", () => {
  statusBox.textContent = "";
  result.hidden = true;
  const file = input.files[0];
  if (!file) { preview.hidden = true; return; }
  if (!["image/jpeg", "image/png"].includes(file.type) || file.size > 8 * 1024 * 1024) {
    preview.hidden = true;
    statusBox.textContent = "Please choose a JPG or PNG image smaller than 8 MB.";
    input.value = "";
    return;
  }
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusBox.textContent = "";
  result.hidden = true;
  if (!input.files[0]) { statusBox.textContent = "Choose a leaf image first."; return; }
  const body = new FormData();
  body.append("leaf_image", input.files[0]);
  button.disabled = true;
  button.textContent = "Analyzing...";
  try {
    const response = await fetch("/predict", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Prediction failed.");
    document.getElementById("disease").textContent = data.disease;
    document.getElementById("confidence-text").textContent = `Model confidence: ${data.confidence}%`;
    document.getElementById("confidence-bar").style.width = `${Math.min(100, Math.max(0, data.confidence))}%`;
    document.getElementById("note").textContent = data.note;
    result.hidden = false;
  } catch (error) {
    statusBox.textContent = error.message || "Could not connect to the server.";
  } finally {
    button.disabled = false;
    button.textContent = "Predict disease";
  }
});
