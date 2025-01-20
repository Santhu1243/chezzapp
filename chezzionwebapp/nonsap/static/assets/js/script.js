function confirmLogout() {
  const confirmation = window.confirm("Are you sure you want to log out?");
  if (confirmation) {
    document.getElementById("logout-form").submit();
  }
}

document.getElementById("add-more").addEventListener("click", function () {
  const container = document.getElementById("file-input-container");
  const inputCount = container.getElementsByTagName("input").length; // To maintain unique ID for each input

  // Create a new wrapper for the file input
  const newFileInputWrapper = document.createElement("div");
  newFileInputWrapper.classList.add("file-input-wrapper");

  // Create the new label and input elements
  const newLabel = document.createElement("label");
  newLabel.setAttribute("for", `id_attachment_${inputCount}`);
  newLabel.innerText = "Attach File";

  const newInput = document.createElement("input");
  newInput.setAttribute("type", "file");
  newInput.setAttribute("name", "attachment");
  newInput.setAttribute("id", `id_attachment_${inputCount}`);

  // Append the label and input to the new wrapper
  newFileInputWrapper.appendChild(newLabel);
  newFileInputWrapper.appendChild(newInput);

  // Append the new file input wrapper to the container
  container.appendChild(newFileInputWrapper);
});
