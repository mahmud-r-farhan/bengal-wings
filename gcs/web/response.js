"use strict";

// Shomoy is deliberately device-local: no fetch/XHR, analytics, or server writes.
const STORE_KEY = "bengal-wings.shomoy.v1";
const MAX_RECORDS = 500;
const $ = (id) => document.getElementById(id);
const dialogs = { request: $("request-dialog"), resource: $("resource-dialog"), detail: $("detail-dialog") };
let data = { requests: [], resources: [] };
let toastTimer;

function uid() {
  return globalThis.crypto && crypto.randomUUID ? crypto.randomUUID() : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
}
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}
function cleanText(value, max = 600) { return String(value ?? "").trim().slice(0, max); }
function validDate(value) { const n = Date.parse(value); return Number.isFinite(n) ? new Date(n).toISOString() : new Date().toISOString(); }
function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
    if (saved && Array.isArray(saved.requests) && Array.isArray(saved.resources)) {
      data.requests = saved.requests.slice(0, MAX_RECORDS).filter((r) => r && typeof r.id === "string").map(normalizeRequest);
      data.resources = saved.resources.slice(0, MAX_RECORDS).filter((r) => r && typeof r.id === "string").map(normalizeResource);
    }
  } catch (_) { showToast("Saved board could not be read. Export/import backups may recover it."); }
}
function normalizeRequest(r) {
  const categories = ["Rescue", "Medical", "Safe water", "Food", "Shelter", "Sanitation", "Access", "Other"];
  const statuses = ["New", "Verified", "Assigned", "Resolved"];
  const latValue = r.lat === null || r.lat === "" || r.lat === undefined ? null : Number(r.lat);
  const lonValue = r.lon === null || r.lon === "" || r.lon === undefined ? null : Number(r.lon);
  const validPin = Number.isFinite(latValue) && Math.abs(latValue) <= 90 && Number.isFinite(lonValue) && Math.abs(lonValue) <= 180;
  return {
    id: cleanText(r.id, 100), title: cleanText(r.title, 100), category: categories.includes(r.category) ? r.category : "Other",
    priority: ["P1", "P2", "P3"].includes(r.priority) ? r.priority : "P2", location: cleanText(r.location, 180),
    people: Math.max(0, Math.min(100000, Number(r.people) || 0)), vulnerable: Math.max(0, Math.min(100000, Number(r.vulnerable) || 0)),
    details: cleanText(r.details, 600), access: ["Unknown", "Reachable", "Difficult", "Cut off"].includes(r.access) ? r.access : "Unknown",
    contact: cleanText(r.contact, 80), lat: validPin ? latValue : null, lon: validPin ? lonValue : null,
    status: statuses.includes(r.status) ? r.status : "New", assignee: cleanText(r.assignee, 100),
    createdAt: validDate(r.createdAt), updatedAt: validDate(r.updatedAt || r.createdAt)
  };
}
function normalizeResource(r) {
  const statuses = ["Available", "Busy", "Unavailable"];
  return { id: cleanText(r.id, 100), name: cleanText(r.name, 100), type: cleanText(r.type, 40), quantity: cleanText(r.quantity, 50),
    location: cleanText(r.location, 160), status: statuses.includes(r.status) ? r.status : "Available", createdAt: validDate(r.createdAt), updatedAt: validDate(r.updatedAt || r.createdAt) };
}
function save() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(data)); render(); return true; }
  catch (_) { showToast("Could not save: browser storage may be full or disabled. Export/delete records and retry."); return false; }
}
function showToast(message) {
  const el = $("toast"); el.textContent = message; el.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove("show"), 3500);
}
function formatDate(value) {
  try { return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value)); }
  catch (_) { return "time unavailable"; }
}
function priorityRank(p) { return ({ P1: 0, P2: 1, P3: 2 })[p] ?? 3; }
function openDialog(dialog) { if (!dialog.open) dialog.showModal(); }
function closeDialog(dialog) { if (dialog.open) dialog.close(); }

function render() {
  const active = data.requests.filter((r) => r.status !== "Resolved");
  $("metric-open").textContent = String(active.length);
  $("metric-critical").textContent = String(active.filter((r) => r.priority === "P1").length);
  $("metric-people").textContent = String(active.reduce((n, r) => n + r.people, 0).toLocaleString());
  $("metric-resources").textContent = String(data.resources.filter((r) => r.status === "Available").length);
  renderRequests(); renderResources();
}
function renderRequests() {
  const root = $("request-list");
  const status = $("status-filter").value, category = $("category-filter").value;
  const query = $("search").value.trim().toLocaleLowerCase();
  const filtered = data.requests.filter((r) => {
    if (status === "active" && r.status === "Resolved") return false;
    if (status === "resolved" && r.status !== "Resolved") return false;
    if (category !== "all" && r.category !== category) return false;
    return !query || [r.title, r.location, r.category, r.details, r.contact, r.id].join(" ").toLocaleLowerCase().includes(query);
  }).sort((a, b) => priorityRank(a.priority) - priorityRank(b.priority) || Date.parse(a.createdAt) - Date.parse(b.createdAt));
  if (!filtered.length) {
    root.innerHTML = `<div class="empty-state"><strong>${data.requests.length ? "No reports match these filters" : "No community needs logged yet"}</strong><p>${data.requests.length ? "Try another search or filter." : "Add a verified report when a community shares a need."}</p></div>`;
  } else {
    root.innerHTML = filtered.map((r) => {
      const people = `${r.people.toLocaleString()} people` + (r.vulnerable ? ` · ${r.vulnerable.toLocaleString()} need extra assistance` : "");
      const access = r.access === "Cut off" ? " · ISOLATED" : r.access === "Difficult" ? " · difficult access" : "";
      return `<article class="request-card" role="button" tabindex="0" data-request="${escapeHTML(r.id)}" aria-label="Open report ${escapeHTML(r.title)}">
        <div><div class="request-title">${escapeHTML(r.title)}</div><div class="request-place">⌖ ${escapeHTML(r.location)}</div></div>
        <span class="badge priority-${r.priority}">${r.priority} · ${escapeHTML(r.category)}</span>
        <div class="request-summary"><span>${escapeHTML(people)}</span><span>${escapeHTML(r.access)}${escapeHTML(access)}</span></div>
        <div class="request-bottom"><span class="badge status-chip status-${r.status}">${escapeHTML(r.status)}</span>${r.assignee ? `<span class="request-place">Assigned: ${escapeHTML(r.assignee)}</span>` : ""}<span class="request-time">Updated ${escapeHTML(formatDate(r.updatedAt))}</span></div>
      </article>`;
    }).join("");
  }
  $("list-count").textContent = `${filtered.length} report${filtered.length === 1 ? "" : "s"} shown · P1 first, oldest first`;
}
function renderResources() {
  const root = $("resource-list");
  const records = data.resources.slice().sort((a, b) => (a.status === "Available" ? -1 : 1) - (b.status === "Available" ? -1 : 1) || a.name.localeCompare(b.name));
  if (!records.length) {
    root.innerHTML = `<div class="empty-state" style="padding:20px 8px"><strong>No help registered</strong><p>Add a boat, team, supply or shelter with permission.</p></div>`;
    return;
  }
  root.innerHTML = records.map((r) => `<article class="resource-card" data-resource-card="${escapeHTML(r.id)}">
    <div class="resource-top"><span class="resource-name">${escapeHTML(r.name)}</span><span class="availability availability-${r.status}">${escapeHTML(r.status)}</span></div>
    <div class="resource-meta">${escapeHTML(r.type)}${r.quantity ? ` · ${escapeHTML(r.quantity)}` : ""}<br>${escapeHTML(r.location)}</div>
    <div class="resource-actions"><button class="text-action" data-resource-action="toggle" data-id="${escapeHTML(r.id)}">${r.status === "Available" ? "Mark busy" : r.status === "Busy" ? "Mark unavailable" : "Mark available"}</button><button class="text-action remove" data-resource-action="remove" data-id="${escapeHTML(r.id)}">Remove</button></div>
  </article>`).join("");
}

function requestFromForm(form) {
  const fd = new FormData(form), people = Number(fd.get("people") || 0), vulnerable = Number(fd.get("vulnerable") || 0);
  const latText = String(fd.get("lat") || "").trim(), lonText = String(fd.get("lon") || "").trim();
  if (vulnerable > people) { showToast("People needing extra assistance cannot exceed the total affected."); return null; }
  if ((latText && !lonText) || (!latText && lonText)) { showToast("Enter both latitude and longitude, or leave both blank."); return null; }
  const lat = latText ? Number(latText) : null, lon = lonText ? Number(lonText) : null;
  if ((lat !== null && (!Number.isFinite(lat) || Math.abs(lat) > 90)) || (lon !== null && (!Number.isFinite(lon) || Math.abs(lon) > 180))) { showToast("The optional location pin is outside valid coordinate ranges."); return null; }
  const now = new Date().toISOString();
  return normalizeRequest({ id: uid(), title: fd.get("title"), category: fd.get("category"), priority: fd.get("priority"), location: fd.get("location"),
    people, vulnerable, details: fd.get("details"), access: fd.get("access"), contact: fd.get("contact"), lat, lon,
    status: "New", assignee: "", createdAt: now, updatedAt: now });
}
$("new-request").addEventListener("click", () => { $("request-form").reset(); $("request-form").elements.people.value = 1; $("request-form").elements.vulnerable.value = 0; openDialog(dialogs.request); });
$("request-form").addEventListener("submit", (event) => {
  event.preventDefault(); const record = requestFromForm(event.currentTarget); if (!record) return;
  if (data.requests.length >= MAX_RECORDS) return showToast("Board limit reached. Export and archive older reports first.");
  data.requests.unshift(record); if (save()) { closeDialog(dialogs.request); showToast("Report saved on this device."); }
});
$("new-resource").addEventListener("click", () => { $("resource-form").reset(); openDialog(dialogs.resource); });
$("new-resource-mini").addEventListener("click", () => $("new-resource").click());
$("resource-form").addEventListener("submit", (event) => {
  event.preventDefault(); const fd = new FormData(event.currentTarget), now = new Date().toISOString();
  if (data.resources.length >= MAX_RECORDS) return showToast("Resource limit reached. Remove an inactive entry first.");
  data.resources.unshift(normalizeResource({ id: uid(), name: fd.get("name"), type: fd.get("type"), quantity: fd.get("quantity"), location: fd.get("location"), status: fd.get("status"), createdAt: now, updatedAt: now }));
  if (save()) { closeDialog(dialogs.resource); showToast("Help registered on this device."); }
});

document.querySelectorAll(".close-dialog").forEach((b) => b.addEventListener("click", () => { const d = b.closest("dialog"); if (d) closeDialog(d); }));
Object.values(dialogs).forEach((d) => d.addEventListener("click", (e) => { if (e.target === d) closeDialog(d); }));
$("print-board").addEventListener("click", () => window.print());
$("search").addEventListener("input", renderRequests);
$("status-filter").addEventListener("change", renderRequests);
$("category-filter").addEventListener("change", renderRequests);
$("request-list").addEventListener("click", (event) => { const card = event.target.closest("[data-request]"); if (card) openRequest(card.dataset.request); });
$("request-list").addEventListener("keydown", (event) => { if ((event.key === "Enter" || event.key === " ") && event.target.matches("[data-request]")) { event.preventDefault(); openRequest(event.target.dataset.request); } });

function openRequest(id) {
  const r = data.requests.find((x) => x.id === id); if (!r) return;
  const coords = Number.isFinite(r.lat) && Number.isFinite(r.lon) ? `${r.lat.toFixed(5)}, ${r.lon.toFixed(5)}` : "Not recorded";
  $("detail-content").innerHTML = `<div class="dialog-head"><div><p class="eyebrow">${escapeHTML(r.id.slice(0, 12))} · CREATED ${escapeHTML(formatDate(r.createdAt))}</p><h2 class="detail-title">${escapeHTML(r.title)}</h2></div><button class="icon-button close-dialog" type="button" aria-label="Close">×</button></div>
    <div class="detail-meta">${escapeHTML(r.category)} · ${escapeHTML(r.location)}</div>
    ${r.details ? `<p class="detail-description">${escapeHTML(r.details)}</p>` : ""}
    <div class="detail-grid"><div class="detail-field"><label>People affected</label><strong>${r.people.toLocaleString()} (${r.vulnerable.toLocaleString()} need extra assistance)</strong></div><div class="detail-field"><label>Access</label><strong>${escapeHTML(r.access)}</strong></div><div class="detail-field"><label>Reference / route</label><strong>${escapeHTML(r.contact || "Not recorded")}</strong></div><div class="detail-field"><label>Optional pin (device-local)</label><strong>${escapeHTML(coords)}</strong></div></div>
    <div class="detail-edit"><label>Urgency<select id="edit-priority"><option value="P1" ${r.priority === "P1" ? "selected" : ""}>P1 · Immediate safety risk</option><option value="P2" ${r.priority === "P2" ? "selected" : ""}>P2 · Urgent, within hours</option><option value="P3" ${r.priority === "P3" ? "selected" : ""}>P3 · Follow-up</option></select></label><label>Follow-up status<select id="edit-status">${["New", "Verified", "Assigned", "Resolved"].map((s) => `<option ${r.status === s ? "selected" : ""}>${s}</option>`).join("")}</select></label><label class="span-2">Assigned team / resource<input id="edit-assignee" maxlength="100" value="${escapeHTML(r.assignee)}" placeholder="Team name or resource reference"></label></div>
    <div class="detail-actions"><button class="text-action remove" id="delete-request">Delete report</button><div><button class="button secondary close-dialog">Close</button><button class="button primary" id="save-request">Save updates</button></div></div>`;
  $("detail-content").querySelectorAll(".close-dialog").forEach((b) => b.addEventListener("click", () => closeDialog(dialogs.detail)));
  $("save-request").addEventListener("click", () => {
    r.priority = $("edit-priority").value; r.status = $("edit-status").value; r.assignee = cleanText($("edit-assignee").value, 100); r.updatedAt = new Date().toISOString();
    if (save()) { closeDialog(dialogs.detail); showToast("Report updated."); }
  });
  $("delete-request").addEventListener("click", () => {
    if (!confirm("Delete this report from this browser? Export a backup first if you may need it.")) return;
    data.requests = data.requests.filter((x) => x.id !== id); save(); closeDialog(dialogs.detail); showToast("Report deleted from this device.");
  });
  openDialog(dialogs.detail);
}

$("resource-list").addEventListener("click", (event) => {
  const button = event.target.closest("[data-resource-action]"); if (!button) return;
  const resource = data.resources.find((r) => r.id === button.dataset.id); if (!resource) return;
  if (button.dataset.resourceAction === "remove") {
    if (!confirm(`Remove “${resource.name}” from this device's board?`)) return;
    data.resources = data.resources.filter((r) => r.id !== resource.id); save(); showToast("Resource removed."); return;
  }
  resource.status = resource.status === "Available" ? "Busy" : resource.status === "Busy" ? "Unavailable" : "Available";
  resource.updatedAt = new Date().toISOString(); save();
});

$("get-location").addEventListener("click", () => {
  if (!navigator.geolocation) return showToast("Location is not available in this browser.");
  const button = $("get-location"); button.disabled = true; button.textContent = "Requesting permission…";
  navigator.geolocation.getCurrentPosition((position) => {
    $("request-form").elements.lat.value = position.coords.latitude.toFixed(6);
    $("request-form").elements.lon.value = position.coords.longitude.toFixed(6);
    button.disabled = false; button.textContent = "Use this device's location"; showToast("Location added to this local form only.");
  }, (error) => {
    button.disabled = false; button.textContent = "Use this device's location";
    showToast(error.code === 1 ? "Location permission was not granted." : "Could not get a location fix. You can enter coordinates manually.");
  }, { enableHighAccuracy: false, timeout: 12000, maximumAge: 60000 });
});

function download(name, text, type) {
  const blob = new Blob([text], { type }), url = URL.createObjectURL(blob), a = document.createElement("a");
  a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$("export-data").addEventListener("click", () => {
  const backup = { app: "Shomoy Community Response Board", version: 1, exportedAt: new Date().toISOString(), requests: data.requests, resources: data.resources };
  download(`shomoy-backup-${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(backup, null, 2), "application/json");
  showToast("Backup downloaded. It contains potentially sensitive field information—store it safely.");
});
$("export-csv").addEventListener("click", () => {
  const columns = ["Reference", "Created (UTC)", "Updated (UTC)", "Title", "Category", "Urgency", "Status", "Location", "People affected", "Need extra assistance", "Access", "Assigned team/resource", "Reference/contact route", "Details", "Latitude", "Longitude"];
  const cell = (value) => {
    let text = String(value ?? "");
    // Avoid spreadsheet formula execution when exported text is opened in Excel/Sheets.
    if (typeof value === "string" && /^[=+@-]/.test(text.trimStart())) text = `'${text}`;
    return `"${text.replace(/"/g, '""')}"`;
  };
  const lines = [columns, ...data.requests.map((r) => [r.id, r.createdAt, r.updatedAt, r.title, r.category, r.priority, r.status, r.location, r.people, r.vulnerable, r.access, r.assignee, r.contact, r.details, r.lat, r.lon])];
  download(`shomoy-needs-${new Date().toISOString().slice(0, 10)}.csv`, String.fromCharCode(0xFEFF) + lines.map((row) => row.map(cell).join(",")).join(String.fromCharCode(13, 10)), "text/csv;charset=utf-8");
  showToast("CSV downloaded. It includes report details—handle it as sensitive information.");
});
$("import-file").addEventListener("change", async (event) => {
  const file = event.target.files && event.target.files[0]; event.target.value = ""; if (!file) return;
  if (file.size > 3 * 1024 * 1024) return showToast("Backup is too large (maximum 3 MB).");
  try {
    const parsed = JSON.parse(await file.text());
    if (!parsed || !Array.isArray(parsed.requests) || !Array.isArray(parsed.resources) || parsed.requests.length > MAX_RECORDS || parsed.resources.length > MAX_RECORDS) throw new Error("unexpected backup structure");
    const requests = new Map(data.requests.map((r) => [r.id, r]));
    for (const item of parsed.requests) if (item && typeof item.id === "string" && item.title && item.location) {
      const incoming = normalizeRequest(item), current = requests.get(incoming.id);
      if (!current || Date.parse(incoming.updatedAt) >= Date.parse(current.updatedAt)) requests.set(incoming.id, incoming);
    }
    const resources = new Map(data.resources.map((r) => [r.id, r]));
    for (const item of parsed.resources) if (item && typeof item.id === "string" && item.name && item.location) {
      const incoming = normalizeResource(item), current = resources.get(incoming.id);
      if (!current || Date.parse(incoming.updatedAt) >= Date.parse(current.updatedAt)) resources.set(incoming.id, incoming);
    }
    if (requests.size > MAX_RECORDS || resources.size > MAX_RECORDS) throw new Error("merged board exceeds 500 entries per list");
    data = { requests: [...requests.values()], resources: [...resources.values()] };
    if (save()) showToast("Backup merged into this device. Review any recently changed records.");
  } catch (error) { showToast(`Import failed: ${cleanText(error.message, 100)}`); }
});

function updateConnectivity() {
  const el = $("connection-state");
  const offline = !navigator.onLine; el.className = `connection ${offline ? "offline" : "online"}`;
  el.querySelector("span").textContent = offline ? "Offline · local data" : "Network available · local data";
}
window.addEventListener("online", updateConnectivity); window.addEventListener("offline", updateConnectivity);
if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost" || location.hostname === "127.0.0.1")) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/response-sw.js").catch(() => {}));
}
load(); render(); updateConnectivity();
