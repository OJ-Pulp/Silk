import { renderSurvey } from "./survey.js";

export function clearPopup() {
  const panel = document.getElementById("popup");
  if (panel) {
    panel.innerHTML = "";
    panel.classList.add("hidden");

    // Reset stored state
    panel.sortAsc = true;
    panel.filterTypes = new Set(["Node", "Edge"]);
    panel.searchTerm = "";
  }
}

export function updatePopup(
  dataList,
  selectedNodes,
  selectedEdges,
  updateSelectionVisuals,
  updatePopupFromSelection
) {
  const panel = document.getElementById("popup");
  if (!panel) {
    console.error("Popup panel not found in DOM.");
    return;
  }

  panel.innerHTML = ""; // Clear existing content (list only)

  // --- State init
  if (panel.sortAsc === undefined) panel.sortAsc = true;
  if (!panel.filterTypes) panel.filterTypes = new Set(["Node", "Edge"]);
  if (panel.searchTerm === undefined) panel.searchTerm = "";

  // --- Controls container (sort button, filter checkboxes, clear selection)
  const controlsDiv = document.createElement("div");
  controlsDiv.style.display = "flex";
  controlsDiv.style.alignItems = "center";
  controlsDiv.style.justifyContent = "space-between";
  controlsDiv.style.marginBottom = "8px";
  controlsDiv.style.padding = "4px 10px";

  // Sort button
  const sortBtn = document.createElement("button");
  sortBtn.classList.add("sort-button");
  sortBtn.title = "Sort by weight";

  const arrowUp = "▲";
  const arrowDown = "▼";

  function renderSortButton() {
    sortBtn.textContent = `Sort by Weight ${panel.sortAsc ? arrowUp : arrowDown}`;
  }
  renderSortButton();

  sortBtn.addEventListener("click", () => {
    panel.sortAsc = !panel.sortAsc;
    renderSortButton();
    updatePopupFromSelection();
  });

  // Filter checkboxes container
  const filterContainer = document.createElement("div");
  filterContainer.style.display = "flex";
  filterContainer.style.alignItems = "center";
  filterContainer.style.gap = "10px";
  filterContainer.style.marginLeft = "12px";

  ["Node", "Edge"].forEach(type => {
    const label = document.createElement("label");
    label.style.display = "flex";
    label.style.alignItems = "center";
    label.style.gap = "4px";
    label.style.fontSize = "0.9em";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "custom-checkbox";
    checkbox.checked = panel.filterTypes.has(type);

    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        panel.filterTypes.add(type);
      } else {
        panel.filterTypes.delete(type);
      }
      updatePopupFromSelection();
    });

    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(type));
    filterContainer.appendChild(label);
  });

  // Clear selection button
  const clearSelectionBtn = document.createElement("button");
  clearSelectionBtn.textContent = "Clear";
  clearSelectionBtn.title = "Clear selected nodes and edges";
  clearSelectionBtn.style.marginLeft = "12px";
  clearSelectionBtn.style.cursor = "pointer";
  clearSelectionBtn.style.padding = "2px 4px";
  clearSelectionBtn.style.fontSize = "0.9em";

  clearSelectionBtn.addEventListener("click", () => {
    selectedNodes.clear();
    selectedEdges.clear();
    panel.searchTerm = ""; // clear search term as well
    updateSelectionVisuals();
    updatePopupFromSelection();
  });

  // Append controls to container
  controlsDiv.appendChild(sortBtn);
  controlsDiv.appendChild(filterContainer);
  controlsDiv.appendChild(clearSelectionBtn);
  panel.appendChild(controlsDiv);

  // --- Search bar container (below controls)
  const searchContainer = document.createElement("div");
  searchContainer.style.display = "flex";
  searchContainer.style.alignItems = "center";
  searchContainer.style.gap = "6px";
  searchContainer.style.marginBottom = "8px";

  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.placeholder = "Search Data (press Enter)...";
  searchInput.style.flex = "1";
  searchInput.style.padding = "4px 8px";
  searchInput.style.fontSize = "0.9em";
  searchInput.style.border = "1px solid #ccc";
  searchInput.style.borderRadius = "4px";

  // Keep input in sync with panel.searchTerm
  searchInput.value = panel.searchTerm || "";

  searchContainer.appendChild(searchInput);
  panel.appendChild(searchContainer);

  // Update searchTerm and refresh popup on Enter key press
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      panel.searchTerm = searchInput.value.trim().toLowerCase();
      updatePopupFromSelection();
    }
  });

  // --- Filter and sort data

  const searchTerm = panel.searchTerm;

  // Filter only selected nodes/edges and filtered by type
  let filteredDataList = dataList.filter(data => {
    if (!panel.filterTypes.has(data.Type)) return false;

    const isSelected =
      (data.Type === "Node" && selectedNodes.has(data.ID)) ||
      (data.Type === "Edge" && selectedEdges.has(data.ID));

    return isSelected;
  });

  // Sort by whether data.Data values contain searchTerm, then by weight
  filteredDataList = filteredDataList.sort((a, b) => {
    const aMatches = searchTerm
      ? Object.values(a.Data || {}).some(v =>
          String(v).toLowerCase().includes(searchTerm)
        )
      : false;

    const bMatches = searchTerm
      ? Object.values(b.Data || {}).some(v =>
          String(v).toLowerCase().includes(searchTerm)
        )
      : false;

    if (aMatches && !bMatches) return -1;
    if (!aMatches && bMatches) return 1;

    // If equal match ranking, sort by weight
    const wA = a.Weight ?? (a.Data?.weight ?? 0);
    const wB = b.Weight ?? (b.Data?.weight ?? 0);
    return panel.sortAsc ? wA - wB : wB - wA;
  });

  // --- Create popup entries
  filteredDataList.forEach(data => {
    const entry = document.createElement("div");
    entry.classList.add("popup-entry");
    entry.style.display = "flex";
    entry.style.justifyContent = "space-between";
    entry.style.alignItems = "center";
    entry.style.borderBottom = "1px solid #ccc";
    entry.style.padding = "6px 4px";

    const infoDiv = document.createElement("div");
    infoDiv.style.flex = "1";

    const idStr = Array.isArray(data.ID) ? data.ID.join(">") : data.ID;
    entry.dataset.type = data.Type;
    entry.dataset.id = idStr;

    // Top-level keys except Data
    for (const key in data) {
      if (key === "Data") continue;
      const p = document.createElement("p");
      p.style.margin = "2px 0";
      p.style.fontSize = "0.9em";
      p.innerHTML = `<strong>${key}:</strong> ${data[key]}`;
      infoDiv.appendChild(p);
    }

    // Divider + nested Data fields
    if (data.Data && typeof data.Data === "object" && Object.keys(data.Data).length > 0) {
      const divider = document.createElement("hr");
      divider.className = "popup-divider";
      infoDiv.appendChild(divider);

      for (const subKey in data.Data) {
        const p = document.createElement("p");
        p.style.margin = "2px 0";
        p.style.fontSize = "0.9em";
        p.innerHTML = `<strong>${subKey}:</strong> ${data.Data[subKey]}`;
        infoDiv.appendChild(p);
      }
    }

    entry.appendChild(infoDiv);

    // --- Buttons: Edit & Delete
    const btnsDiv = document.createElement("div");
    btnsDiv.style.display = "flex";
    btnsDiv.style.gap = "6px";

    const createIconButton = (imgPath, titleText, clickHandler) => {
      const btn = document.createElement("button");
      btn.title = titleText;
      btn.className = "popup-button";

      const img = document.createElement("img");
      img.src = imgPath;
      img.alt = titleText;
      img.classList.add("popout-icon");

      // Click animation: scale on press
      img.addEventListener("mousedown", () => {
        img.style.transform = "scale(0.95)";
      });
      img.addEventListener("mouseup", () => {
        img.style.transform = "scale(1)";
      });

      btn.appendChild(img);
      btn.addEventListener("click", clickHandler);
      return btn;
    };

    const editBtn = createIconButton("./images/Edit.png", `Edit this ${data.Type.toLowerCase()}`, (e) => {
      e.stopPropagation();
      const mode = "edit-entities";
      renderSurvey(mode, data);
    });

    const deleteBtn = createIconButton("./images/Delete.png", `Delete this ${data.Type.toLowerCase()}`, (e) => {
      e.stopPropagation();
      alert(`Delete functionality not implemented yet for ${data.Type} ${data.ID}`);
    });

    btnsDiv.appendChild(editBtn);
    btnsDiv.appendChild(deleteBtn);
    entry.appendChild(btnsDiv);

    // --- Double-click to deselect
    entry.addEventListener("dblclick", () => {
      if (data.Type === "Node") {
        selectedNodes.delete(data.ID);
      } else if (data.Type === "Edge") {
        selectedEdges.delete(data.ID);
      }
      updateSelectionVisuals();
      updatePopupFromSelection();
    });

    panel.appendChild(entry);
  });

  panel.classList.remove("hidden");
}
