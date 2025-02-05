let sortDirection = {};


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





function sortTable(columnIndex, tableId) {
    let table = document.getElementById(tableId);
    let tbody = table.querySelector("tbody");
    let rows = Array.from(tbody.querySelectorAll("tr"));

    // Initialize sort direction per table
    if (!sortDirection[tableId]) {
        sortDirection[tableId] = {};
    }
    if (sortDirection[tableId][columnIndex] === undefined) {
        sortDirection[tableId][columnIndex] = true;  // Ascending by default
    } else {
        sortDirection[tableId][columnIndex] = !sortDirection[tableId][columnIndex];  // Toggle direction
    }

    rows.sort((rowA, rowB) => {
        let cellA = rowA.cells[columnIndex]?.textContent.trim() || "";
        let cellB = rowB.cells[columnIndex]?.textContent.trim() || "";

        // Convert to numbers if applicable
        let numA = parseFloat(cellA);
        let numB = parseFloat(cellB);
        let isNumeric = !isNaN(numA) && !isNaN(numB);

        if (isNumeric) {
            return sortDirection[tableId][columnIndex] ? numA - numB : numB - numA;
        }

        return sortDirection[tableId][columnIndex] ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
    });

    // Append sorted rows back to tbody
    tbody.innerHTML = "";
    rows.forEach(row => tbody.appendChild(row));

    // Update sort icons
    updateSortIcons(columnIndex, tableId);
}

function updateSortIcons(columnIndex, tableId) {
    let table = document.getElementById(tableId);
    let headers = table.querySelectorAll("th i"); // Find all FontAwesome icons inside table headers

    // Reset all icons in the current table
    headers.forEach(icon => {
        icon.classList.remove("fa-arrow-up", "fa-arrow-down");
        icon.classList.add("fa-sort");
    });

    // Update the icon for the active column
    let icon = table.querySelector(`th:nth-child(${columnIndex + 1}) i`);
    if (icon) {
        icon.classList.remove("fa-sort");
        icon.classList.add(sortDirection[tableId][columnIndex] ? "fa-arrow-up" : "fa-arrow-down");
    }
}

