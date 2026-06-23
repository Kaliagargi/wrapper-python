{% extends "base.html" %}
{% block title %}Dashboard — Licence Manager{% endblock %}

{% block content %}
<div class="page-header">
    <h2>⚙️ Dashboard</h2>
    <p>Select developers, software, set inputs and generate all tables.</p>
</div>

<!-- Developer Select -->
<div class="card">
    <div class="card-title">👤 Step 1 — Select Developers</div>
    <div id="developerList"
         style="display:flex; flex-wrap:wrap; gap:8px; padding:4px; min-height:48px;">
        <div style="color:#9CA3AF; font-size:13px; padding:8px;">Loading...</div>
    </div>
</div>

<!-- Software + Inputs -->
<div class="card">
    <div class="card-title">🖥️ Step 2 — Select Software & Set Inputs</div>
    <p style="font-size:13px; color:#6B7280; margin-bottom:16px">
        Select software and fill in values. Advent only appears for SP3D.
    </p>
    <div id="softwareInputList">
        <div style="padding:12px; color:#9CA3AF; font-size:13px">
            Select developers first...
        </div>
    </div>
</div>

<!-- Generate Button -->
<div style="display:flex; gap:12px; align-items:center; margin-top:8px;">
    <button class="btn btn-primary btn-lg" onclick="generateAllTables()">
        ⚡ Generate Tables
    </button>
    <span id="generateStatus" style="font-size:13px; color:#6B7280"></span>
</div>

<!-- Tables Section -->
<div id="tablesSection" style="display:none; margin-top:32px;">

    <!-- Table 1 -->
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
            <div class="card-title" style="margin:0">📊 Licence Summary</div>
            <button class="btn btn-outline btn-sm" onclick="toggleEdit(this)"
                    data-editing="false">✏️ Edit</button>
        </div>
        <div id="t1Container">
            <div class="alert alert-info">Click Generate Tables to load.</div>
        </div>
    </div>

    <!-- Table 2 -->
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
            <div class="card-title" style="margin:0">📋 Department Lease Distribution</div>
            <button class="btn btn-outline btn-sm" onclick="toggleEdit(this)"
                    data-editing="false">✏️ Edit</button>
        </div>
        <div id="t2Container">
            <div class="alert alert-info">Click Generate Tables to load.</div>
        </div>
    </div>

    <!-- Table 3 -->
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
            <div class="card-title" style="margin:0">🔢 Sub Location Breakups</div>
            <button class="btn btn-outline btn-sm" onclick="toggleEdit(this)"
                    data-editing="false">✏️ Edit</button>
        </div>
        <div id="t3Container">
            <div class="alert alert-info">Click Generate Tables to load.</div>
        </div>
    </div>

    <!-- Table 4 -->
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
            <div class="card-title" style="margin:0">🏦 ISL — Dept Wise Breakdown</div>
            <button class="btn btn-outline btn-sm" onclick="toggleEdit(this)"
                    data-editing="false">✏️ Edit</button>
        </div>
        <div id="t4Container">
            <div class="alert alert-info">Click Generate Tables to load.</div>
        </div>
    </div>

    <!-- Keystore + Download buttons -->
    <div style="display:flex; gap:12px; margin-top:8px; flex-wrap:wrap;">
        <button class="btn btn-navy" onclick="generateKeystore()">
            🔑 Generate Keystore
        </button>
        <button class="btn btn-primary" onclick="downloadAll()">
            ⬇️ Download All
        </button>
    </div>

    <!-- Keystore Section -->
    <div id="keystoreSection" style="margin-top:20px;"></div>

</div>
{% endblock %}

{% block scripts %}
<script>
const SP3D_NAMES = ['sp3d', 'smartplant', 'smartplant 3d'];

let selectedDevelopers = [];
let selectedSoftware   = [];

// ─────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────

function isSP3D(sw) {
    return SP3D_NAMES.some(n => sw.toLowerCase().includes(n));
}

function getSavedInputs() {
    return Session.get('inputs') || {};
}

function autoSaveInputs(sw) {
    const annual  = parseFloat(document.getElementById(`annual_${sw}`)?.value)  || 0;
    const advent  = parseFloat(document.getElementById(`advent_${sw}`)?.value)  || 0;
    const onshore = parseFloat(document.getElementById(`onshore_${sw}`)?.value) || 0;
    const all     = getSavedInputs();
    all[sw]       = {annual, advent, onshore};
    Session.set('inputs', all);
}

// ─────────────────────────────────────────────
// LOAD DEVELOPERS
// ─────────────────────────────────────────────

async function loadDevelopers() {
    const sid = getSessionId();
    if (!sid) { window.location.href = '/'; return; }

    const data = await apiFetch(`/tables/developer-list?session_id=${sid}`);
    if (!data?.success) return;

    const container = document.getElementById('developerList');
    container.innerHTML = data.data.map(dev => `
        <div id="devcard_${dev}"
             onclick="toggleDeveloper('${dev}', this)"
             style="display:inline-flex; align-items:center; gap:8px;
                    padding:10px 18px; border-radius:8px;
                    border:1.5px solid #E5E7EB; background:white;
                    cursor:pointer; font-size:13px; font-weight:600;
                    transition:all 0.15s;">
            <input type="checkbox" id="dev_${dev}"
                   style="width:15px; height:15px; accent-color:#2563EB"
                   onclick="event.stopPropagation()">
            👤 ${dev}
        </div>
    `).join('');
}

// ─────────────────────────────────────────────
// TOGGLE DEVELOPER
// ─────────────────────────────────────────────

async function toggleDeveloper(dev, el) {
    const checkbox      = document.getElementById(`dev_${dev}`);
    const isNowSelected = !checkbox.checked;
    checkbox.checked    = isNowSelected;

    if (isNowSelected) {
        if (!selectedDevelopers.includes(dev)) selectedDevelopers.push(dev);
        el.style.borderColor = '#2563EB';
        el.style.background  = '#EFF6FF';
        el.style.color       = '#2563EB';
    } else {
        selectedDevelopers   = selectedDevelopers.filter(d => d !== dev);
        el.style.borderColor = '#E5E7EB';
        el.style.background  = 'white';
        el.style.color       = '#111827';
    }

    await loadSoftwareWithInputs();
}

// ─────────────────────────────────────────────
// LOAD SOFTWARE WITH INPUTS
// ─────────────────────────────────────────────

async function loadSoftwareWithInputs() {
    if (selectedDevelopers.length === 0) {
        document.getElementById('softwareInputList').innerHTML =
            '<div style="padding:12px; color:#9CA3AF; font-size:13px">Select developers first...</div>';
        return;
    }

    const sid  = getSessionId();
    const devs = selectedDevelopers.join(',');
    const data = await apiFetch(
        `/tables/software-by-developer?session_id=${sid}&developers=${encodeURIComponent(devs)}`
    );
    if (!data?.success) return;

    const savedInputs  = getSavedInputs();
    const prevSelected = Session.get('software') || [];

    const container = document.getElementById('softwareInputList');
    container.innerHTML = data.data.map(sw => {
        const swName     = sw.software;
        const isSelected = prevSelected.includes(swName);
        const inputs     = savedInputs[swName] || {annual:0, advent:0, onshore:0};
        const showAdvent = isSP3D(swName);

        return `
        <div id="swcard_${swName}"
             style="border:1.5px solid ${isSelected ? '#2563EB' : '#E5E7EB'};
                    border-radius:8px; padding:16px; margin-bottom:12px;
                    background:${isSelected ? '#EFF6FF' : 'white'};
                    transition:all 0.15s;">
            <div style="display:flex; align-items:center; gap:12px;
                        margin-bottom:${isSelected ? '16px' : '0'}">
                <input type="checkbox" id="sw_${swName}"
                       ${isSelected ? 'checked' : ''}
                       onchange="toggleSoftware('${swName}', this)"
                       style="width:16px; height:16px; accent-color:#2563EB; cursor:pointer;">
                <label for="sw_${swName}"
                       style="font-size:14px; font-weight:600; cursor:pointer; flex:1; color:#111827;">
                    🖥️ ${swName}
                    <span style="font-size:11px; color:#9CA3AF; font-weight:400; margin-left:6px;">
                        ${sw.developer}
                    </span>
                </label>
                ${showAdvent
                    ? '<span style="background:#EFF6FF; color:#2563EB; font-size:10px; font-weight:700; padding:2px 8px; border-radius:10px; border:1px solid #BFDBFE;">SP3D</span>'
                    : ''}
            </div>
            <div id="inputs_${swName}"
                 style="display:${isSelected ? 'grid' : 'none'};
                        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                        gap:12px;">
                <div class="form-group" style="margin:0">
                    <label class="form-label">Annual</label>
                    <input type="number" class="form-control"
                           id="annual_${swName}" value="${inputs.annual}" min="0"
                           oninput="autoSaveInputs('${swName}')">
                </div>
                ${showAdvent ? `
                <div class="form-group" style="margin:0">
                    <label class="form-label">Advent</label>
                    <input type="number" class="form-control"
                           id="advent_${swName}" value="${inputs.advent}" min="0"
                           oninput="autoSaveInputs('${swName}')">
                </div>` : ''}
                <div class="form-group" style="margin:0">
                    <label class="form-label">Onshore</label>
                    <input type="number" class="form-control"
                           id="onshore_${swName}" value="${inputs.onshore}" min="0"
                           oninput="autoSaveInputs('${swName}')">
                </div>
            </div>
        </div>`;
    }).join('');

    selectedSoftware = prevSelected;
}

// ─────────────────────────────────────────────
// TOGGLE SOFTWARE
// ─────────────────────────────────────────────

function toggleSoftware(sw, checkbox) {
    const card      = document.getElementById(`swcard_${sw}`);
    const inputsDiv = document.getElementById(`inputs_${sw}`);
    const labelDiv  = card.querySelector('div');

    if (checkbox.checked) {
        if (!selectedSoftware.includes(sw)) selectedSoftware.push(sw);
        card.style.borderColor     = '#2563EB';
        card.style.background      = '#EFF6FF';
        inputsDiv.style.display    = 'grid';
        if (labelDiv) labelDiv.style.marginBottom = '16px';
    } else {
        selectedSoftware           = selectedSoftware.filter(s => s !== sw);
        card.style.borderColor     = '#E5E7EB';
        card.style.background      = 'white';
        inputsDiv.style.display    = 'none';
        if (labelDiv) labelDiv.style.marginBottom = '0';
    }

    Session.set('software', selectedSoftware);
    updateNav();
}

// ─────────────────────────────────────────────
// GENERATE ALL TABLES
// ─────────────────────────────────────────────

async function generateAllTables() {
    if (selectedSoftware.length === 0) {
        toast('Please select at least one software', 'error');
        return;
    }

    selectedSoftware.forEach(sw => autoSaveInputs(sw));
    Session.set('software', selectedSoftware);

    showLoading('Generating all tables...');

    const sid  = getSessionId();
    const allT1 = [];
    const allT2 = {};
    const allT3 = {};
    const allT4 = {};

    for (const sw of selectedSoftware) {
        const inputs = getSavedInputs()[sw] || {annual:0, advent:0, onshore:0};

        const p1 = new URLSearchParams({session_id:sid, software:sw, annual:inputs.annual, advent:inputs.advent});
        const d1 = await apiFetch(`/tables/table1?${p1}`);
        if (d1?.success) allT1.push(...d1.data);

        const p2 = new URLSearchParams({session_id:sid, software:sw, advent:inputs.advent, onshore:inputs.onshore});
        const d2 = await apiFetch(`/tables/table2?${p2}`);
        if (d2?.success) Object.assign(allT2, d2.data);

        const p3 = new URLSearchParams({session_id:sid, software:sw, annual:inputs.annual, advent:inputs.advent, onshore:inputs.onshore});
        const d3 = await apiFetch(`/tables/table3?${p3}`);
        if (d3?.success) Object.assign(allT3, d3.data);

        const p4 = new URLSearchParams({session_id:sid, software:sw});
        const d4 = await apiFetch(`/tables/table4?${p4}`);
        if (d4?.success) Object.assign(allT4, d4.data);
    }

    hideLoading();
    document.getElementById('tablesSection').style.display = 'block';

    // Render all tables
    renderTable('t1Container',
        ['Developer', 'Software', 'Total Lic', 'Own Lic', 'Lease Lic', 'Annual', 'Advent', 'Order'],
        allT1.map(r => ({
            developer: r.developer, software: r.software,
            total_lic: r.total_lic, own_lic:  r.own_lic,
            lease_lic: r.lease_lic, annual:   r.annual,
            advent:    r.advent,    order:    r.order_lic,
        })), true
    );

    const t2rows = [];
    Object.entries(allT2).forEach(([sw, d]) =>
        d.rows.forEach(r => t2rows.push({
            software: sw, developer: d.developer,
            category: r.label, description: r.description || '', value: r.value,
        }))
    );
    renderTable('t2Container',
        ['Software', 'Developer', 'Category', 'Description', 'Value'],
        t2rows, true
    );

    const t3rows = [];
    Object.entries(allT3).forEach(([sw, d]) =>
        d.rows.forEach(r => t3rows.push({
            software: sw, developer: d.developer,
            category: r.label, value: r.value,
        }))
    );
    renderTable('t3Container',
        ['Software', 'Developer', 'Category', 'Value'],
        t3rows, true
    );

    const t4rows = [];
    Object.entries(allT4).forEach(([sw, d]) =>
        d.rows.forEach(r => t4rows.push({
            software: sw, developer: d.developer,
            dept: r.dept, ltm: r.ltm, share: r.share, total: r.total,
        }))
    );
    renderTable('t4Container',
        ['Software', 'Developer', 'Dept', 'LTM', 'Share', 'Total'],
        t4rows, true
    );

    updateNav();
    toast('All tables generated!', 'success');
    document.getElementById('generateStatus').textContent = '✅ Generated!';
}

// ─────────────────────────────────────────────
// GENERATE KEYSTORE
// ─────────────────────────────────────────────

async function generateKeystore() {
    const sid = getSessionId();
    if (!sid || selectedSoftware.length === 0) {
        toast('Please generate tables first', 'error');
        return;
    }

    showLoading('Generating Keystore...');

    const data = await apiFetch('/keystore/table', {
        method:  'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            session_id:  sid,
            software:    selectedSoftware,
            user_values: {},
        }),
    });

    hideLoading();
    if (!data?.success) { toast('Failed to load keystore', 'error'); return; }

    renderKeystoreInline(data.data);
    toast('Keystore generated!', 'success');
}

function renderKeystoreInline(keystoreData) {
    let html = '<div class="card"><div class="card-title">🔑 Keystore</div>';

    Object.entries(keystoreData).forEach(([sw, swData]) => {
        html += `
        <h4 style="margin:16px 0 8px; color:#1A2B4A; font-size:14px;">
            ${swData.developer} — ${sw}
        </h4>
        <div class="table-wrapper" style="margin-bottom:16px;">
        <table>
            <thead>
                <tr>
                    <th>Label</th>
                    <th>Key ID</th>
                    <th>Active</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>`;

        swData.keys.forEach(k => {
            const valueDisplay = k.value !== null
                ? `<span>${k.value}</span>`
                : `<input type="number" class="edit-cell"
                          placeholder="Enter value"
                          id="kval_${sw}_${k.label}_${k.key_id}"
                          style="width:100px; padding:4px 8px;
                                 border:1px solid #2563EB; border-radius:4px;
                                 background:#EFF6FF; font-size:13px;">`;

            const status = k.value === null
                ? `<span style="color:#DC2626; font-weight:600; background:#FEF2F2;
                                padding:3px 8px; border-radius:4px; font-size:11px;">
                    ⚠️ Needs Input
                   </span>`
                : `<span style="color:#059669; font-weight:600; background:#ECFDF5;
                                padding:3px 8px; border-radius:4px; font-size:11px;">
                    ✅ OK
                   </span>`;

            html += `
            <tr style="${k.value === null ? 'background:#FEF9F9;' : ''}">
                <td>${k.label}</td>
                <td style="font-family:monospace;">${k.key_id}</td>
                <td>
                    <label class="toggle">
                        <input type="checkbox" ${k.active ? 'checked' : ''}
                               onchange="toggleKeyInline('${sw}','${k.label}','${k.key_id}',this)">
                        <span class="toggle-slider"></span>
                    </label>
                </td>
                <td>${valueDisplay}</td>
                <td>${status}</td>
            </tr>`;
        });

        html += `</tbody></table></div>`;
    });

    html += `
    <div style="margin-top:16px; display:flex; gap:12px;">
        <button class="btn btn-navy btn-sm" onclick="saveKeystoreValues()">
            💾 Save Keystore Values
        </button>
    </div>
    </div>`;

    document.getElementById('keystoreSection').innerHTML = html;
}

async function toggleKeyInline(software, dept, keyId, checkbox) {
    const params = new URLSearchParams({software, dept, key_id: keyId});
    const data   = await apiFetch(`/keystore/keys/toggle?${params}`, {method:'POST'});
    if (!data?.success) {
        checkbox.checked = !checkbox.checked;
        toast('Failed to toggle key', 'error');
    } else {
        toast(`${keyId} ${checkbox.checked ? 'activated' : 'deactivated'}`, 'success');
    }
}

function saveKeystoreValues() {
    const userValues = {};
    document.querySelectorAll('[id^="kval_"]').forEach(inp => {
        if (inp.value !== '') {
            const parts  = inp.id.replace('kval_', '').split('_');
            const sw     = parts[0];
            const label  = parts[1];
            const keyId  = parts.slice(2).join('_');
            if (!userValues[sw])        userValues[sw] = {};
            if (!userValues[sw][label]) userValues[sw][label] = {};
            userValues[sw][label][keyId] = parseFloat(inp.value) || 0;
        }
    });
    sessionStorage.setItem('keystore_values_temp', JSON.stringify(userValues));
    toast('Keystore values saved!', 'success');
}

// ─────────────────────────────────────────────
// DOWNLOAD ALL
// ─────────────────────────────────────────────

async function downloadAll() {
    const sid         = getSessionId();
    const software    = selectedSoftware;
    const allInputs   = getSavedInputs();
    const perSwInputs = {};

    software.forEach(sw => {
        perSwInputs[sw] = allInputs[sw] || {annual: