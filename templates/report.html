{% extends "base.html" %}
{% block title %}Report — Licence Manager{% endblock %}

{% block content %}
<div class="page-header">
    <h2>📋 Licence Report</h2>
    <p>All tables computed per software.</p>
</div>

<!-- Software Tabs -->
<div style="display:flex; gap:4px; margin-bottom:24px; 
            border-bottom:2px solid #E5E7EB; padding-bottom:0;">
    <div id="swTabs" style="display:flex; gap:4px;"></div>
</div>

<!-- Tab Content -->
<div id="tabContent"></div>

<!-- Bottom Actions -->
<div style="display:flex; gap:12px; margin-top:24px; flex-wrap:wrap;">
    <button class="btn btn-navy" onclick="generateKeystore()">
        🔑 Generate Keystore
    </button>
    <button class="btn btn-primary" onclick="downloadAll()">
        ⬇️ Download All
    </button>
    <a href="/dashboard" class="btn btn-ghost">
        ← Back to Dashboard
    </a>
</div>

<!-- Keystore Section -->
<div id="keystoreSection" style="margin-top:24px;"></div>

{% endblock %}

{% block scripts %}
<script>
let activeSw      = null;
let allTableData  = {};  // {sw: {t1, t2, t3, t4}}

// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    const software = getSoftware();
    if (!software || software.length === 0) {
        window.location.href = '/dashboard';
        return;
    }

    renderTabs(software);
    await loadAllData(software);
    switchTab(software[0]);
});

// ─────────────────────────────────────────────
// RENDER TABS
// ─────────────────────────────────────────────

function renderTabs(software) {
    const container = document.getElementById('swTabs');
    container.innerHTML = software.map((sw, i) => `
        <button id="tab_${sw}"
                onclick="switchTab('${sw}')"
                style="padding:10px 20px; border:none; cursor:pointer;
                       font-size:13px; font-weight:600;
                       background:${i === 0 ? 'white' : 'transparent'};
                       color:${i === 0 ? '#2563EB' : '#6B7280'};
                       border-bottom:${i === 0 ? '2px solid #2563EB' : '2px solid transparent'};
                       margin-bottom:-2px; transition:all 0.15s;">
            🖥️ ${sw}
            <span id="tabstatus_${sw}"
                  style="margin-left:6px; font-size:10px; 
                         background:#E5E7EB; color:#6B7280;
                         padding:2px 6px; border-radius:10px;">
                Loading...
            </span>
        </button>
    `).join('');
}

// ─────────────────────────────────────────────
// SWITCH TAB
// ─────────────────────────────────────────────

function switchTab(sw) {
    const software = getSoftware();

    // Update tab styles
    software.forEach(s => {
        const tab = document.getElementById(`tab_${s}`);
        if (!tab) return;
        const isActive = s === sw;
        tab.style.color       = isActive ? '#2563EB' : '#6B7280';
        tab.style.background  = isActive ? 'white'   : 'transparent';
        tab.style.borderBottom = isActive
            ? '2px solid #2563EB'
            : '2px solid transparent';
    });

    activeSw = sw;

    // Render content for this software
    const data = allTableData[sw];
    if (!data) {
        document.getElementById('tabContent').innerHTML = `
            <div class="alert alert-info">Loading data for ${sw}...</div>`;
        return;
    }

    renderTabContent(sw, data);
}

// ─────────────────────────────────────────────
// LOAD ALL DATA
// ─────────────────────────────────────────────

async function loadAllData(software) {
    const sid       = getSessionId();
    const allInputs = Session.get('inputs') || {};

    for (const sw of software) {
        const inputs = allInputs[sw] || {annual:0, advent:0, onshore:0};

        // Table 1
        const p1 = new URLSearchParams({
            session_id: sid, software: sw, annual: inputs.annual, advent: inputs.advent
        });
        const d1 = await apiFetch(`/tables/table1?${p1}`);

        // Table 2
        const p2 = new URLSearchParams({
            session_id: sid, software: sw, advent: inputs.advent, onshore: inputs.onshore
        });
        const d2 = await apiFetch(`/tables/table2?${p2}`);

        // Table 3
        const p3 = new URLSearchParams({
            session_id: sid, software: sw,
            annual: inputs.annual, advent: inputs.advent, onshore: inputs.onshore
        });
        const d3 = await apiFetch(`/tables/table3?${p3}`);

        // Table 4
        const p4 = new URLSearchParams({session_id: sid, software: sw});
        const d4 = await apiFetch(`/tables/table4?${p4}`);

        allTableData[sw] = {
            t1: d1?.success ? d1.data : [],
            t2: d2?.success ? d2.data : {},
            t3: d3?.success ? d3.data : {},
            t4: d4?.success ? d4.data : {},
        };

        // Update tab badge
        const badge = document.getElementById(`tabstatus_${sw}`);
        if (badge) {
            badge.textContent    = '✅';
            badge.style.background = '#ECFDF5';
            badge.style.color      = '#059669';
        }
    }
}

// ─────────────────────────────────────────────
// RENDER TAB CONTENT
// ─────────────────────────────────────────────

function renderTabContent(sw, data) {
    const container = document.getElementById('tabContent');
    container.innerHTML = `
        <div id="t1_${sw}_wrap" class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">📊 Licence Summary</div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)" data-editing="false">✏️ Edit</button>
            </div>
            <div id="t1_${sw}"></div>
        </div>

        <div id="t2_${sw}_wrap" class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">📋 Department Lease Distribution</div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)" data-editing="false">✏️ Edit</button>
            </div>
            <div id="t2_${sw}"></div>
        </div>

        <div id="t3_${sw}_wrap" class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">🔢 Sub Location Breakups</div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)" data-editing="false">✏️ Edit</button>
            </div>
            <div id="t3_${sw}"></div>
        </div>

        <div id="t4_${sw}_wrap" class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">🏦 ISL — Dept Wise Breakdown</div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)" data-editing="false">✏️ Edit</button>
            </div>
            <div id="t4_${sw}"></div>
        </div>
    `;

    // Render Table 1
    renderTable(`t1_${sw}`,
        ['Developer', 'Software', 'Total Lic', 'Own Lic', 'Lease Lic', 'Annual', 'Advent', 'Order'],
        data.t1.map(r => ({
            developer: r.developer, software:  r.software,
            total_lic: r.total_lic, own_lic:   r.own_lic,
            lease_lic: r.lease_lic, annual:    r.annual,
            advent:    r.advent,    order:     r.order_lic,
        })), true
    );

    // Render Table 2
    const t2rows = [];
    Object.entries(data.t2).forEach(([s, d]) =>
        d.rows.forEach(r => t2rows.push({
            category:    r.label,
            description: r.description || '',
            value:       r.value,
        }))
    );
    renderTable(`t2_${sw}`,
        ['Category', 'Description', 'Value'],
        t2rows, true
    );

    // Render Table 3
    const t3rows = [];
    Object.entries(data.t3).forEach(([s, d]) =>
        d.rows.forEach(r => t3rows.push({
            category: r.label,
            value:    r.value,
        }))
    );
    renderTable(`t3_${sw}`,
        ['Category', 'Value'],
        t3rows, true
    );

    // Render Table 4
    const t4rows = [];
    Object.entries(data.t4).forEach(([s, d]) =>
        d.rows.forEach(r => t4rows.push({
            dept:  r.dept,
            ltm:   r.ltm,
            share: r.share,
            total: r.total,
        }))
    );
    renderTable(`t4_${sw}`,
        ['Dept', 'LTM', 'Share', 'Total'],
        t4rows, true
    );
}

// ─────────────────────────────────────────────
// GENERATE KEYSTORE
// ─────────────────────────────────────────────

async function generateKeystore() {
    const sid      = getSessionId();
    const software = getSoftware();

    showLoading('Generating Keystore...');

    const data = await apiFetch('/keystore/table', {
        method:  'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            session_id:  sid,
            software:    software,
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
        <h4 style="margin:16px 0 8px; color:#1A2B4A; font-size:14px; font-weight:700;">
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
                ? `<span style="font-weight:600;">${k.value}</span>`
                : `<input type="number" class="edit-cell"
                          placeholder="Enter value"
                          id="kval_${sw}_${k.label}_${k.key_id}"
                          style="width:100px; padding:4px 8px;
                                 border:1px solid #2563EB; border-radius:4px;
                                 background:#EFF6FF; font-size:13px;">`;

            const status = k.value === null
                ? `<span style="color:#DC2626; font-weight:600;
                                background:#FEF2F2; padding:3px 8px;
                                border-radius:4px; font-size:11px;">
                    ⚠️ Needs Input
                   </span>`
                : `<span style="color:#059669; font-weight:600;
                                background:#ECFDF5; padding:3px 8px;
                                border-radius:4px; font-size:11px;">
                    ✅ OK
                   </span>`;

            html += `
            <tr style="${k.value === null ? 'background:#FFF5F5;' : ''}">
                <td>${k.label}</td>
                <td style="font-family:monospace; font-size:12px;">${k.key_id}</td>
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
    <div style="margin-top:16px;">
        <button class="btn btn-navy btn-sm" onclick="saveKeystoreValues()">
            💾 Save Input Values
        </button>
    </div></div>`;

    document.getElementById('keystoreSection').innerHTML = html;
    document.getElementById('keystoreSection').scrollIntoView({behavior:'smooth'});
}

async function toggleKeyInline(software, dept, keyId, checkbox) {
    const params = new URLSearchParams({software, dept, key_id: keyId});
    const data   = await apiFetch(`/keystore/keys/toggle?${params}`, {method:'POST'});
    if (!data?.success) {
        checkbox.checked = !checkbox.checked;
        toast('Failed to toggle key', 'error');
    } else {
        toast(`${keyId} ${checkbox.checked ? 'activated ✅' : 'deactivated'}`,
              checkbox.checked ? 'success' : 'warn');
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
    toast('Values saved!', 'success');
}

// ─────────────────────────────────────────────
// DOWNLOAD ALL
// ─────────────────────────────────────────────

async function downloadAll() {
    const sid         = getSessionId();
    const software    = getSoftware();
    const allInputs   = Session.get('inputs') || {};
    const perSwInputs = {};

    software.forEach(sw => {
        perSwInputs[sw] = allInputs[sw] || {annual:0, advent:0, onshore:0};
    });

    const keystoreValues = JSON.parse(
        sessionStorage.getItem('keystore_values_temp') || '{}'
    );

    showLoading('Generating Excel report...');

    try {
        const response = await fetch('/download/', {
            method:  'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id:      sid,
                software:        software,
                t1_software:     software,
                t2_software:     software,
                t3_software:     software,
                t4_software:     software,
                per_sw_inputs:   perSwInputs,
                keystore_values: keystoreValues,
            }),
        });

        if (!response.ok) {
            const err = await response.json();
            toast(err.detail || 'Download failed', 'error');
            hideLoading();
            return;
        }

        const blob = await response.blob();
        const url  = window.URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href     = url;
        a.download = 'licence_report.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        sessionStorage.removeItem('keystore_values_temp');
        hideLoading();
        toast('Download complete! ✅', 'success');

    } catch(e) {
        hideLoading();
        toast('Download failed: ' + e.message, 'error');
    }
}
</script>
{% endblock %}