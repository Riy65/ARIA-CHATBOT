const API_URL = window.ARIA_API_URL || "";
const token = localStorage.getItem("token");
let currentPortfolio, currentVersion;
const template = { projects: [], experience: [], skills: [], education: [] };
const dialog = document.getElementById("create-dialog");
const escapeHtml = value => { const node = document.createElement("span"); node.textContent = value; return node.innerHTML; };
async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(options.headers || {}) } });
  const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Something went wrong. Please try again."); return body;
}
if (!token) window.location.replace("login.html");
document.getElementById("new-portfolio-btn").onclick = () => dialog.showModal();
document.getElementById("empty-create-btn").onclick = () => dialog.showModal();
document.getElementById("dialog-close-btn").onclick = () => dialog.close();
document.getElementById("preview-close-btn").onclick = () => document.getElementById("preview-dialog").close();
function showPortfolio(portfolio) {
  currentPortfolio = portfolio; currentVersion = portfolio.versions.at(-1);
  document.getElementById("empty-workspace").hidden = true; document.getElementById("portfolio-form").hidden = false;
  document.getElementById("editor-title").textContent = portfolio.name; document.getElementById("version-badge").textContent = `Version ${currentVersion.version_number}`;
  document.getElementById("portfolio-content").value = JSON.stringify(currentVersion.content || template, null, 2); document.getElementById("change-summary").value = ""; document.getElementById("assessment-card").hidden = true;
}
async function loadPortfolio(id) { showPortfolio(await request(`/portfolios/${id}`)); await renderList(); }
async function renderList() {
  const portfolios = await request("/portfolios"), list = document.getElementById("portfolio-list"); list.innerHTML = portfolios.length ? "" : '<p class="muted-copy">No portfolios yet. Create one to begin.</p>';
  portfolios.forEach(item => { const button = document.createElement("button"); button.className = `portfolio-item${currentPortfolio?.portfolio_id === item.portfolio_id ? " active" : ""}`; button.innerHTML = `<strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(item.target_role || "No target role")} · ${item.version_count} version${item.version_count === 1 ? "" : "s"}</span>`; button.onclick = () => loadPortfolio(item.portfolio_id).catch(showError); list.appendChild(button); });
}
function showError(error) { document.getElementById("form-status").textContent = error.message; }
async function versionHtml(endpoint) {
  const response = await fetch(`${API_URL}${endpoint}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) { const body = await response.json(); throw new Error(body.detail || "Unable to generate the portfolio page."); }
  return response;
}
document.getElementById("preview-btn").onclick = async () => {
  try {
    const response = await versionHtml(`/portfolios/${currentPortfolio.portfolio_id}/versions/${currentVersion.version_id}/render`);
    document.getElementById("portfolio-preview").srcdoc = await response.text();
    document.getElementById("preview-dialog-title").textContent = `${currentPortfolio.name} · version ${currentVersion.version_number}`;
    document.getElementById("preview-dialog").showModal();
  } catch (error) { showError(error); }
};
document.getElementById("download-btn").onclick = async () => {
  try {
    const response = await versionHtml(`/portfolios/${currentPortfolio.portfolio_id}/versions/${currentVersion.version_id}/download`);
    const link = document.createElement("a");
    link.href = URL.createObjectURL(await response.blob());
    link.download = `${currentPortfolio.name.toLowerCase().replace(/[^a-z0-9]+/g, "-") || "portfolio"}-v${currentVersion.version_number}.html`;
    link.click(); URL.revokeObjectURL(link.href);
    document.getElementById("form-status").textContent = "Standalone HTML portfolio downloaded.";
  } catch (error) { showError(error); }
};
document.getElementById("create-portfolio-form").addEventListener("submit", async event => { event.preventDefault(); try { const portfolio = await request("/portfolios", { method: "POST", body: JSON.stringify({ name: document.getElementById("new-portfolio-name").value.trim(), target_role: document.getElementById("new-target-role").value.trim() || null, initial_content: template }) }); dialog.close(); event.target.reset(); showPortfolio(portfolio); await renderList(); } catch (error) { alert(error.message); } });
document.getElementById("portfolio-form").addEventListener("submit", async event => { event.preventDefault(); try { const content = JSON.parse(document.getElementById("portfolio-content").value); if (!content || Array.isArray(content) || typeof content !== "object") throw new Error("Portfolio content must be a JSON object."); const version = await request(`/portfolios/${currentPortfolio.portfolio_id}/versions`, { method: "POST", body: JSON.stringify({ content, label: `Version ${currentVersion.version_number + 1}`, change_summary: document.getElementById("change-summary").value.trim() || null }) }); currentVersion = version; document.getElementById("version-badge").textContent = `Version ${version.version_number}`; document.getElementById("form-status").textContent = "New version saved. Your earlier version is unchanged."; await loadPortfolio(currentPortfolio.portfolio_id); } catch (error) { showError(error); } });
document.getElementById("assess-btn").onclick = async () => { try { const assessment = await request(`/portfolios/${currentPortfolio.portfolio_id}/versions/${currentVersion.version_id}/assess`, { method: "POST" }), card = document.getElementById("assessment-card"); card.hidden = false; card.innerHTML = `<p class="eyebrow">Portfolio readiness</p><div class="score-row"><strong>${assessment.overall_score}</strong><span>/100</span></div><h3>Next best actions</h3><ul>${assessment.recommended_actions.map(action => `<li>${escapeHtml(action)}</li>`).join("")}</ul>`; } catch (error) { showError(error); } };
renderList().catch(error => { document.getElementById("portfolio-list").innerHTML = `<p class="muted-copy">${escapeHtml(error.message)}</p>`; });
