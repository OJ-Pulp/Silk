import { clearSelection, uuids, refreshGrab } from './graph.js';
import {rerenderGraph} from './topbar.js';
import { clearPopup } from './popup.js';

const modal = document.getElementById("survey-modal");
const formContainer = document.getElementById("survey-form-container");

let currentSurveyMode = null;

export function renderSurvey(mode, data = null) {
  currentSurveyMode = mode;
  modal.classList.remove("hidden");
  formContainer.innerHTML = ""; // clear previous content

  switch (mode) {
    case "edit-toolbar":
      renderEditToolbarForm();
      break;
    case "add-node":
      renderCreateNodeForm();
      break;
    case "add-edge":
      renderCreateEdgeForm();
      break;
    case "new-graph":
      renderCreateGraphForm();
      break;
    case "delete-graph":
      renderDeleteGraphForm();  
      break;
    case "save-graph":
      renderSaveGraphForm();
      break; // Not implemented
    case "edit-entities":
      renderEditEntitiesForm(data);
      break;
    case "display-graph":
      renderDisplayGraphForm();
      break;
    default:
      formContainer.innerHTML = "<p>Unknown mode.</p>";
  }
}

async function renderDisplayGraphForm() {
  formContainer.innerHTML = `
    <label style="margin-top: 6px;">Graph ID:</label>
    <div style="position: relative;">
      <input type="text" id="graph-ids-input" placeholder="Graph ID #1, Graph ID #2..." autocomplete="off" style="width: 100%;">
      <div id="graph-suggestions"
           style="border: 1px solid #ccc; background: white; position: absolute; z-index: 10; top: 100%; left: 0; right: 0;"></div>
    </div>

    <div id="filters-container" style="display: flex; gap: 20px; margin-top: 12px;">

      <!-- Node Filters column -->
      <div id="node-filter-section" style="flex: 1;">
        <label style="margin-bottom: 4px; display: block;">Node Filters:</label>
        <div id="node-filter-list" style="margin-top: 0px;"></div>
        <div style="text-align: center; margin-top: 6px;">
          <button id="add-node-filter-btn" type="button" class="circle-button" title="Add Node Filter">+</button>
        </div>
      </div>

      <!-- Edge Filters column -->
      <div id="edge-filter-section" style="flex: 1;">
        <label style="margin-bottom: 4px; display: block;">Edge Filters:</label>
        <div id="edge-filter-list" style="margin-top: 0px;"></div>
        <div style="text-align: center; margin-top: 6px;">
          <button id="add-edge-filter-btn" type="button" class="circle-button" title="Add Edge Filter">+</button>
        </div>
      </div>

    </div>
  `;
  // Fetch node and edge keys once
  let nodeKeys = [];
  let edgeKeys = [];
  try {
    const [nodeRes, edgeRes] = await Promise.all([
      fetch("http://localhost:8001/get_node_entities"),
      fetch("http://localhost:8001/get_edge_entities")
    ]);
    if (nodeRes.ok) nodeKeys = await nodeRes.json();
    if (edgeRes.ok) edgeKeys = await edgeRes.json();
  } catch (err) {
    console.error("Failed to fetch node/edge keys", err);
  }

  // Set up buttons
  document.getElementById("add-node-filter-btn").onclick = () => addFilterField("node-filter-list", nodeKeys);
  document.getElementById("add-edge-filter-btn").onclick = () => addFilterField("edge-filter-list", edgeKeys);

  // Add initial rows
  addFilterField("node-filter-list", nodeKeys);
  addFilterField("edge-filter-list", edgeKeys);

  setupGraphAutocomplete();
}


// Levenshtein Distance
function levenshtein(a, b) {
    const dp = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));
    for (let i = 0; i <= a.length; i++) dp[i][0] = i;
    for (let j = 0; j <= b.length; j++) dp[0][j] = j;
    for (let i = 1; i <= a.length; i++) {
        for (let j = 1; j <= b.length; j++) {
            if (a[i - 1] === b[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
            }
        }
    }
    return dp[a.length][b.length];
}

// Find Closest Key
function findClosestKey(varName, validKeys) {
    let minDist = Infinity;
    let closest = varName;
    for (const key of validKeys) {
        const dist = levenshtein(varName.toLowerCase(), key.toLowerCase());
        if (dist < minDist) {
            minDist = dist;
            closest = key;
        }
    }
    return closest;
}
function equToSQL(expression, validKeys) {
    expression = expression.trim().replace(/\s+/g, ' ');
    expression = expression.replace(/==/g, '=')
                           .replace(/\bnot like\b/gi, 'NOT LIKE')
                           .replace(/\blike\b/gi, 'LIKE')
                           .replace(/\bnot in\b/gi, 'NOT IN')
                           .replace(/\bin\b/gi, 'IN');

    // Handle BETWEEN-style range queries (e.g. 10 < age < 20)
    let betweenMatch = expression.match(/^(\d+(?:\.\d+)?)\s*<\s*(\w+)\s*<\s*(\d+(?:\.\d+)?)$/);
    if (betweenMatch) {
        let [_, low, variable, high] = betweenMatch;
        variable = findClosestKey(variable, validKeys);
        return `${variable} BETWEEN ${low} AND ${high}`;
    }

    // Handle IN / NOT IN clauses
    let inMatch = expression.match(/^(\w+)\s+(IN|NOT IN)\s+(\[.*\]|\(.*\))$/i);
    if (inMatch) {
        let [_, variable, op, val] = inMatch;
        variable = findClosestKey(variable, validKeys);
        val = val.slice(1, -1).trim();

        // Match quoted strings or individual tokens
        let items = Array.from(val.matchAll(/(['"])(.*?)\1|(\S+)/g), m => {
            const quoted = m[2];
            const unquoted = m[3];
            let item = quoted !== undefined ? quoted : unquoted;
            return `'${item.replace(/'/g, "''")}'`;
        });

        return `${variable} ${op.toUpperCase()} (${items.join(', ')})`;
    }

    // Handle single-value expressions like name = 'John'
    let singleMatch = expression.match(/^(\w+)\s*(=|!=|>=|<=|>|<|LIKE|NOT LIKE)\s*(.+)$/i);
    if (singleMatch) {
        let [_, variable, operator, val] = singleMatch;
        variable = findClosestKey(variable, validKeys);
        val = val.trim();
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
            val = `'${val.slice(1, -1).replace(/'/g, "''")}'`;
        }
        return `${variable} ${operator.toUpperCase()} ${val}`;
    }

    throw new Error(`Invalid or unsupported expression: ${expression}`);
}

// Add Filter Field
function addFilterField(containerId, validKeys) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const rows = container.querySelectorAll("div.entity-row");
  if (rows.length > 0) {
    const lastInput = rows[rows.length - 1].querySelector("input.entity-value");
    if (!lastInput.value.trim()) return;
  }

  createFilterRow(container, validKeys);
}
// Create Filter Row
function createFilterRow(container, validKeys) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("entity-row");

  const inputCol = document.createElement("div");
  inputCol.classList.add("entity-column");

  const input = document.createElement("input");
  input.type = "text";
  input.classList.add("entity-value");
  input.placeholder = "Filter text...";

  input.addEventListener("blur", () => {
    const raw = input.value.trim();
    if (!raw) return;

    try {
      const corrected = equToSQL(raw, validKeys); // directly get corrected string
      input.value = corrected;                      // set corrected expression
    } catch (err) {
      console.warn("Invalid expression:", err.message);
      // optionally leave the input as is or clear it
    }
  });

  inputCol.appendChild(input);

  const removeBtn = document.createElement("button");
  removeBtn.textContent = "✕";
  removeBtn.type = "button";
  removeBtn.classList.add("remove-btn");
  removeBtn.onclick = () => wrapper.remove();

  wrapper.appendChild(inputCol);
  wrapper.appendChild(removeBtn);
  container.appendChild(wrapper);
}



function renderEditEntitiesForm(data) {
  const formContainer = document.getElementById("survey-form-container");
  if (!formContainer) {
    console.error("Form container not found");
    return;
  }

  console.log("Rendering editable Data form with:", data);

  const entityData = data.Data || {};
  let html = "<h4>Edit Entities</h4>";

  for (const [key, value] of Object.entries(entityData)) {
    html += `
      <div class="data-row" id="row-${key}">
        <label for="data-${key}">${key}:</label>
        <input type="text" id="data-${key}" value="${value}">
        <button type="button" class="delete-button" data-key="${key}">×</button>
      </div>
    `;
  }

  formContainer.innerHTML = html;

  // Prevent Enter key from triggering deletes or form submission
  formContainer.querySelectorAll("input").forEach(input => {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
      }
    });
  });

  // Handle delete buttons
  formContainer.querySelectorAll(".delete-button").forEach(button => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const keyToDelete = e.target.getAttribute("data-key");
      const row = document.getElementById(`row-${keyToDelete}`);
      if (row) row.remove();
      delete data.Data[keyToDelete];
    });
  });
}



// Edit Toolbar form
function renderEditToolbarForm() {
  const tools = [
    "Weight Nodes", 
    "Weight Edges", 
    "Traverse Graph", 
    "Cluster Graph", 
    "Compare Graph"
  ];

  formContainer.innerHTML = tools.map(tool => `
    <div class="form-row">
      <label for="${tool.toLowerCase().replace(/ /g, '-')}-methods">${tool}:</label>
      <select id="${tool.toLowerCase().replace(/ /g, '-')}-methods">
        <option>Loading...</option>
      </select>
    </div>
  `).join('');

  tools.forEach(async tool => {
    const toolId = `${tool.toLowerCase().replace(/ /g, '-')}-methods`;
    const select = document.getElementById(toolId);
    const methods = await fetch(`/api/tool-methods?tool=${encodeURIComponent(tool)}`).then(res => res.json());
    select.innerHTML = methods.map(m => `<option value="${m}">${m}</option>`).join('');
  });
}


  // TODO: Make it so I can put in graph ids and it is a text input seperated by commas
  // And it auto-completes with existing graph ids. If the id does not exist then show read lines under the text
  // and dont allow for the form to be submitted until it is corrected
  // Make entities similar for the key-value pairs but allow for submition even if they keys are 
  // not found within the database
// Create Node form
function renderCreateNodeForm() {
  formContainer.innerHTML = `

    <label style="margin-top: 6px;">Graph ID:</label>
    <div style="position: relative;">
      <input type="text" id="graph-ids-input" placeholder="Graph ID #1, Graph ID #2..." autocomplete="off" style="width: 100%;">
      <div id="graph-suggestions"
           style="border: 1px solid #ccc; background: white; position: absolute; z-index: 10; top: 100%; left: 0; right: 0;"></div>
    </div>
    
    <label>Node ID:</label>
    <input type="text" id="node-id" placeholder="Node ID...">
    <div id="node-id-error" style="color: red; font-size: 0.85em; margin-top: 4px;"></div>



    <div id="entity-list-container" style="margin-top: 0px;">
        <label style="margin-top: 0px;">Entities:</label>
    </div>

    <div id="entity-list-container"  style="text-align: center; margin-top: 0px;">
    
      <button id="add-entity-btn" type="button" class="circle-button" title="Add Entity">+</button>
    </div>
  `;

  document.getElementById("add-entity-btn").onclick = () => {
    addKeyValueEntityField("entity-list-container");
  };

  addKeyValueEntityField("entity-list-container");

  setupGraphAutocomplete();
}



// Create Edge form
function renderCreateEdgeForm() {
  formContainer.innerHTML = `
    <label>Source:</label>
    <select id="source">
      <option value="" disabled selected>--</option>
      ${uuids.map(n => `<option value="${n}">${n}</option>`).join('')}
    </select>

    <label>Target:</label>
    <select id="target">
      <option value="" disabled selected>--</option>
      ${uuids.map(n => `<option value="${n}">${n}</option>`).join('')}
    </select>

    <!-- Directed checkbox -->
    <div style="margin-top: 10px;">
      <input type="checkbox" id="directed" name="directed">
      <label for="directed">Directed</label>
    </div>

    <div id="edge-id-error" style="color: red; font-size: 0.85em; margin-top: 4px;"></div>
    <div id="entity-list-container" style="margin-top: 0px;">
      <label style="margin-top: 0px;">Entities:</label>
    </div>

    <div id="entity-list-container" style="text-align: center; margin-top: 0px;">
      <button id="add-entity-btn" type="button" class="circle-button" title="Add Entity">+</button>
    </div>
  `;

  function syncDropdownOptions() {
    const sourceSelect = document.getElementById("source");
    const targetSelect = document.getElementById("target");

    const sourceVal = sourceSelect.value;
    const targetVal = targetSelect.value;

    Array.from(sourceSelect.options).forEach(opt => opt.disabled = false);
    Array.from(targetSelect.options).forEach(opt => opt.disabled = false);

    if (sourceVal) {
      Array.from(targetSelect.options).forEach(opt => {
        if (opt.value === sourceVal) opt.disabled = true;
      });
    }
    if (targetVal) {
      Array.from(sourceSelect.options).forEach(opt => {
        if (opt.value === targetVal) opt.disabled = true;
      });
    }
  }

  document.getElementById("source").addEventListener("change", syncDropdownOptions);
  document.getElementById("target").addEventListener("change", syncDropdownOptions);

  syncDropdownOptions();

  addKeyValueEntityField("entity-list-container");

  document.getElementById("add-entity-btn").onclick = () => {
    addKeyValueEntityField("entity-list-container");
  };
}



async function setupGraphAutocomplete() {
  const input = document.getElementById("graph-ids-input");
  const suggestionsBox = document.getElementById("graph-suggestions");

  let allGraphs = [];

  // Fetch graph IDs once
  try {
    const res = await fetch("http://localhost:8001/get_graphs");
    const data = await res.json();
    allGraphs = data.graphs || [];
  } catch (err) {
    console.error("Error fetching graphs:", err);
  }

  input.addEventListener("input", () => {
    const value = input.value;
    const parts = value.split(",").map(s => s.trim());
    const current = parts[parts.length - 1].toLowerCase();

    suggestionsBox.innerHTML = "";
    if (!current) return;

    const matches = allGraphs.filter(g => g.toLowerCase().startsWith(current));
    matches.slice(0, 10).forEach(graph => {
      const div = document.createElement("div");
      div.textContent = graph;
      div.className = "suggestion-item";
      div.style.padding = "6px";
      div.style.cursor = "pointer";

      div.addEventListener("click", () => {
        parts[parts.length - 1] = graph;
        input.value = parts.join(", ") + ", ";
        suggestionsBox.innerHTML = "";
      });

      suggestionsBox.appendChild(div);
    });
  });

  // Hide suggestions and clean input on blur
  input.addEventListener("blur", () => {
    setTimeout(() => {  // Delay so click events on suggestions can still register
      suggestionsBox.innerHTML = "";

      const validSet = new Set(allGraphs.map(g => g.toLowerCase()));
      const seen = new Set();
      const parts = input.value
        .split(",")
        .map(s => s.trim())
        .filter(Boolean)
        .filter(s => {
          const lower = s.toLowerCase();
          return validSet.has(lower) && !seen.has(lower) && seen.add(lower);
        });

      input.value = parts.join(", ");
    }, 150); // slight delay to allow suggestion click
  });

  // Optional: hide if clicked outside input or suggestion box
  document.addEventListener("click", (e) => {
    if (e.target !== input && !suggestionsBox.contains(e.target)) {
      suggestionsBox.innerHTML = "";
    }
  });
}



function addKeyValueEntityField(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const rows = container.querySelectorAll("div.entity-row");
  if (rows.length > 0) {
    // Get the last row
    const lastRow = rows[rows.length - 1];
    const lastKeyInput = lastRow.querySelector(".entity-key");
    const lastValInput = lastRow.querySelector(".entity-value");

    // If either key or value is empty, do NOT add a new row
    if (!lastKeyInput.value.trim() || !lastValInput.value.trim()) {
      return;
    }
  }

  // Add new row since last row is filled or no rows yet
  createEntityRow(container);
}

function createEntityRow(container) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("entity-row");

  const keyCol = document.createElement("div");
  keyCol.classList.add("entity-column");
  keyCol.innerHTML = `
    <input type="text" class="entity-key" placeholder="Entity Name...">
  `;

  const valCol = document.createElement("div");
  valCol.classList.add("entity-column");
  valCol.innerHTML = `
    <input type="text" class="entity-value" placeholder="Entity Value...">
  `;

  const removeBtn = document.createElement("button");
  removeBtn.textContent = "✕";
  removeBtn.type = "button";
  removeBtn.classList.add("remove-btn");
  removeBtn.onclick = () => wrapper.remove();

  wrapper.appendChild(keyCol);
  wrapper.appendChild(valCol);
  wrapper.appendChild(removeBtn);

  container.appendChild(wrapper);
}



// Create Graph form
function renderCreateGraphForm() {
  formContainer.innerHTML = `
    <label>Graph ID:</label>
    <input type="text" id="graph-id">
  `;
}

// Delete Graph form
async function renderDeleteGraphForm() {
  const res = await fetch("http://localhost:8001/get_graphs");
  const data = await res.json();
  const graphs = data.graphs || [];

  if (graphs.length === 0) {
    formContainer.innerHTML = `<p>No graphs available to delete.</p>`;
    return;
  }

  formContainer.innerHTML = `
    <label for="graph-select">Select Graph to Delete:</label>
    <select id="graph-select" style="margin-bottom: 12px;">
      ${graphs.map(g => `<option value="${g}">${g}</option>`).join("")}
    </select>
    <div style="margin-top: 12px;">
      <input type="checkbox" id="confirm-delete-checkbox">
      I understand this will permanently delete the graph.
    </div>
  `;
}

async function renderSaveGraphForm() {
    formContainer.innerHTML = `
    <label>Graph ID:</label>
    <input type="text" id="graph-id">
  `;
}

// Close modal button
document.getElementById("close-survey").addEventListener("click", () => {
  modal.classList.add("hidden");
});

// Generic Save button handler

// Generic save button
document.getElementById("save-survey").addEventListener("click", async () => {
  if (currentSurveyMode === "delete-graph") {
    const dropdown = document.getElementById("graph-select");
    const checkbox = document.getElementById("confirm-delete-checkbox");

    // Create or reuse error message div
    let errorDiv = document.getElementById("delete-graph-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.id = "delete-graph-error";
      errorDiv.style.color = "red";
      errorDiv.style.fontSize = "0.85em";
      errorDiv.style.marginTop = "8px";
      formContainer.appendChild(errorDiv);
    }
    errorDiv.textContent = "";

    if (!dropdown || !checkbox) {
      errorDiv.textContent = "Unexpected error: form elements not found.";
      return;
    }

    if (!checkbox.checked) {
      errorDiv.textContent = "Please confirm deletion by checking the box.";
      return;
    }

    const selectedGraph = dropdown.value;
    if (!selectedGraph) {
      errorDiv.textContent = "Please select a graph to delete.";
      return;
    }

    try {
      const res = await fetch("http://localhost:8001/delete_graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: selectedGraph }),
      });
      if (res.ok) {
        errorDiv.remove(); // Clean up
        clearSelection();
        clearPopup();
        await refreshGrab();
        rerenderGraph();
        modal.classList.add("hidden");
      } else {
        errorDiv.textContent = "Failed to delete graph.";
        console.error(await res.text());
      }
    } catch (err) {
      console.error("Error deleting graph:", err);
      errorDiv.textContent = "An unexpected error occurred.";
    }
  } else if (currentSurveyMode == "display-graph") {
  const input = document.getElementById("graph-ids-input");
  const graphFilters = input.value.split(",").map(s => s.trim()).filter(Boolean);

  // Helper to extract key from SQL string (first token before space)
  function extractKey(sqlExpr) {
    const match = sqlExpr.match(/^(\w+)\s+/);
    return match ? match[1] : null;
  }

  function collectFilters(containerId) {
    const inputs = document.querySelectorAll(`#${containerId} input.entity-value`);
    const grouped = {};

    for (const input of inputs) {
      const val = input.value.trim();
      if (!val) continue;

      const keyMatch = val.match(/^(\w+)\s+(.*)$/);  // matches key + rest
      if (!keyMatch) continue;

      const [, key, condition] = keyMatch;

      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(condition.trim());
    }

    return grouped;
  }


  const nodeFilters = collectFilters("node-filter-list");
  const edgeFilters = collectFilters("edge-filter-list");

  try {
    const res = await fetch("http://localhost:8001/filter_graphs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        graph_filters: graphFilters,
        node_filters: nodeFilters,
        edge_filters: edgeFilters,
      }),
    });

    if (res.ok) {
      clearSelection();
      clearPopup();
      modal.classList.add("hidden");
      await refreshGrab();
      rerenderGraph();
    } else {
      console.error(await res.text());
      alert("Failed to display graph.");
    }
  } catch (err) {
    console.error("Error displaying graph:", err);
    alert("An unexpected error occurred.");
  }
}
else if (currentSurveyMode == "save-graph") {
    const input = document.getElementById("graph-id");
    const id = input?.value?.trim();

    // Create or reuse error div
    let errorDiv = document.getElementById("graph-id-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.id = "graph-id-error";
      errorDiv.style.color = "red";
      errorDiv.style.fontSize = "0.85em";
      errorDiv.style.marginTop = "4px";
      input.insertAdjacentElement("afterend", errorDiv);
    }

    // Clear any previous error
    errorDiv.textContent = "";

    if (!id) {
      errorDiv.textContent = "Graph ID is required.";
      return;
    }

    try {
      const checkRes = await fetch("http://localhost:8001/check_id", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const checkJson = await checkRes.json();

      if (checkJson.exists) {
        errorDiv.textContent = "This Graph ID is already taken.";
        return;
      }

      const createRes = await fetch("http://localhost:8001/save_current_graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });

      if (createRes.ok) {
        if (errorDiv) errorDiv.remove();
        clearSelection();
        clearPopup();
        modal.classList.add("hidden");
      } else {
        errorDiv.textContent = "Failed to create graph.";
        console.error(await createRes.text());
      }
    } catch (err) {
      console.error("Error during graph creation:", err);
      errorDiv.textContent = "An unexpected error occurred.";
    }
  } else if (currentSurveyMode === "add-node") {
{
  const id = document.getElementById("node-id")?.value?.trim();
  const errorDiv = document.getElementById("node-id-error");
  errorDiv.textContent = "";

  if (!id) {
    errorDiv.textContent = "Node ID is required.";
    return;
  }

  try {
    // Check if Node ID already exists
    const checkRes = await fetch("http://localhost:8001/check_id", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });

    const checkJson = await checkRes.json();
    if (checkJson.exists) {
      errorDiv.textContent = "This Node ID already exists.";
      return;
    }

    // Collect entity key-value pairs
    const keyEls = document.querySelectorAll("#entity-list-container .entity-key");
    const valEls = document.querySelectorAll("#entity-list-container .entity-value");

    const entities = {};
    for (let i = 0; i < keyEls.length; i++) {
      const key = keyEls[i].value.trim();
      const value = valEls[i].value.trim();
      if (key) entities[key] = value;
    }

    // Get graph IDs (already validated and cleaned)
    const graphInput = document.getElementById("graph-ids-input");
    const graph_ids = graphInput.value.split(",").map(s => s.trim()).filter(Boolean);

    // Final payload
    const res = await fetch("http://localhost:8001/create_node", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        node_id: id,
        graph_ids,
        ...entities,
      }),
    });

    if (res.ok) {
      errorDiv.textContent = "";
      clearSelection();
      clearPopup();
      await refreshGrab();
      rerenderGraph();
      modal.classList.add("hidden");
    } else {
      errorDiv.textContent = "Failed to create node.";
    }
  } catch (err) {
    console.error("Node creation error:", err);
    errorDiv.textContent = "Unexpected error.";
  }
}
} else if (currentSurveyMode === "add-edge") {
  const source = document.getElementById("source")?.value?.trim();
  const target = document.getElementById("target")?.value?.trim();
  const directed = document.getElementById("directed")?.checked;
  const errorDiv = document.getElementById("edge-id-error");
  errorDiv.textContent = "";

  if (!source || !target) {
    errorDiv.textContent = "Both source and target nodes must be selected.";
    return;
  }

  if (source === target) {
    errorDiv.textContent = "Source and target nodes cannot be the same.";
    return;
  }

  try {
    const keyEls = document.querySelectorAll("#entity-list-container .entity-key");
    const valEls = document.querySelectorAll("#entity-list-container .entity-value");

    const entities = {};
    for (let i = 0; i < keyEls.length; i++) {
      const key = keyEls[i].value.trim();
      const value = valEls[i].value.trim();
      if (key) entities[key] = value;
    }

    if (directed) {
      // Send single directed edge
      const res = await fetch("http://localhost:8001/create_edge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source, target, ...entities }),
      });

      if (!res.ok) throw new Error("Failed to create edge.");

    } else {
      // Send both directions for undirected edge
      const res1 = await fetch("http://localhost:8001/create_edge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source, target, ...entities }),
      });

      if (!res1.ok) throw new Error("Failed to create edge.");

      const res2 = await fetch("http://localhost:8001/create_edge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: target, target: source, ...entities }),
      });

      if (!res2.ok) throw new Error("Failed to create edge.");
    }

    // If both requests succeeded:
    errorDiv.textContent = "";
    clearSelection();
    clearPopup();
    await refreshGrab();
    rerenderGraph();
    modal.classList.add("hidden");

  } catch (err) {
    console.error("Edge creation error:", err);
    errorDiv.textContent = "Unexpected error.";
  }
}
 else if (currentSurveyMode === "new-graph") {
    const input = document.getElementById("graph-id");
    const id = input?.value?.trim();

    // Create or reuse error div
    let errorDiv = document.getElementById("graph-id-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.id = "graph-id-error";
      errorDiv.style.color = "red";
      errorDiv.style.fontSize = "0.85em";
      errorDiv.style.marginTop = "4px";
      input.insertAdjacentElement("afterend", errorDiv);
    }

    // Clear any previous error
    errorDiv.textContent = "";

    if (!id) {
      errorDiv.textContent = "Graph ID is required.";
      return;
    }

    try {
      const checkRes = await fetch("http://localhost:8001/check_id", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const checkJson = await checkRes.json();

      if (checkJson.exists) {
        errorDiv.textContent = "This Graph ID is already taken.";
        return;
      }

      const createRes = await fetch("http://localhost:8001/create_graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });

      if (createRes.ok) {
        if (errorDiv) errorDiv.remove();
        clearSelection();
        clearPopup();
        await refreshGrab();
        rerenderGraph();
        modal.classList.add("hidden");
      } else {
        errorDiv.textContent = "Failed to create graph.";
        console.error(await createRes.text());
      }
    } catch (err) {
      console.error("Error during graph creation:", err);
      errorDiv.textContent = "An unexpected error occurred.";
    }
  } else {
      modal.classList.add("hidden");
    }
});

