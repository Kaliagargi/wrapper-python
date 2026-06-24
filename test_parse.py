{% extends "base.html" %}
{% block title %}Report — Licence Manager{% endblock %}

{% block content %}
<div class="page-header">
    <h2>📋 Licence Report</h2>
    <p>All tables computed per software.</p>
</div>

<!-- Software Tabs -->
<div style="display:flex; gap:0; margin-bottom:24px;
            border-bottom:2px solid #E5E7EB; overflow-x:auto;">
    <div id="swTabs" style="display:flex; gap:0;"></div>
</div>

<!-- Tab Content -->
<div id="tabContent"></div>

<!-- Bottom Actions -->
<div style="display:flex; gap:12px; margin-top:24px; flex-wrap:wrap;
            padding:20px; background:white; border-radius:8px;
            border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
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
let activeSw       = null;
let allTableData   = {};
let keystoreData   = {};
let keystoreLimits = {};

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
                style="padding:10px 24px; border:none; cursor:pointer;
                       font-size:13px; font-weight:600; white-space:nowrap;
                       background:${i === 0 ? 'white' : 'transparent'};
                       color:${i === 0 ? '#2563EB' : '#6B7280'};
                       border-bottom:${i === 0 ? '2px solid #2563EB' : '2px solid transparent'};
                       margin-bottom:-2px; transition:all 0.15s;">
            🖥️ ${sw}
            <span id="tabstatus_${sw}"
                  style="margin-left:6px; font-size:10px;
                         background:#E5E7EB; color:#6B7280;
                         padding:2px 6px; border-radius:10px;">
                ⏳
            </span>
        </button>
    `).join('');
}


// ─────────────────────────────────────────────
// SWITCH TAB
// ─────────────────────────────────────────────

function switchTab(sw) {
    const software = getSoftware();

    software.forEach(s => {
        const tab = document.getElementById(`tab_${s}`);
        if (!tab) return;
        const isActive        = s === sw;
        tab.style.color       = isActive ? '#2563EB' : '#6B7280';
        tab.style.background  = isActive ? 'white'   : 'transparent';
        tab.style.borderBottom = isActive
            ? '2px solid #2563EB'
            : '2px solid transparent';
    });

    activeSw = sw;
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

        const p1 = new URLSearchParams({
            session_id: sid, software: sw,
            annual: inputs.annual, advent: inputs.advent
        });
        const d1 = await apiFetch(`/tables/table1?${p1}`);

        const p2 = new URLSearchParams({
            session_id: sid, software: sw,
            advent: inputs.advent, onshore: inputs.onshore
        });
        const d2 = await apiFetch(`/tables/table2?${p2}`);

        const p3 = new URLSearchParams({
            session_id: sid, software: sw,
            annual: inputs.annual, advent: inputs.advent, onshore: inputs.onshore
        });
        const d3 = await apiFetch(`/tables/table3?${p3}`);

        const p4 = new URLSearchParams({session_id: sid, software: sw});
        const d4 = await apiFetch(`/tables/table4?${p4}`);

        allTableData[sw] = {
            t1: d1?.success ? d1.data  : [],
            t2: d2?.success ? d2.data  : {},
            t3: d3?.success ? d3.data  : {},
            t4: d4?.success ? d4.data  : {},
        };

        const badge = document.getElementById(`tabstatus_${sw}`);
        if (badge) {
            badge.textContent      = '✅';
            badge.style.background = '#ECFDF5';
            badge.style.color      = '#059669';
        }
    }
}


// ─────────────────────────────────────────────
// RENDER TAB CONTENT
// ─────────────────────────────────────────────

function renderTabContent(sw, data) {
    document.getElementById('tabContent').innerHTML = `
        <div class="card">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">
                    📊 Licence Summary
                </div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)"
                        data-editing="false">✏️ Edit</button>
            </div>
            <div id="t1_${sw}"></div>
        </div>

        <div class="card">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">
                    📋 Department Lease Distribution
                </div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)"
                        data-editing="false">✏️ Edit</button>
            </div>
            <div id="t2_${sw}"></div>
        </div>

        <div class="card">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">
                    🔢 Sub Location Breakups
                </div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)"
                        data-editing="false">✏️ Edit</button>
            </div>
            <div id="t3_${sw}"></div>
        </div>

        <div class="card">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:16px">
                <div class="card-title" style="margin:0">
                    🏦 ISL — Dept Wise Breakdown
                </div>
                <button class="btn btn-outline btn-sm"
                        onclick="toggleEdit(this)"
                        data-editing="false">✏️ Edit</button>
            </div>
            <div id="t4_${sw}"></div>
        </div>
    `;

    // Table 1
    renderTable(`t1_${sw}`,
        ['Developer', 'Software', 'Total Lic', 'Own Lic',
         'Lease Lic', 'Annual', 'Advent', 'Order'],
        data.t1.map(r => ({
            developer: r.developer, software:  r.software,
            total_lic: r.total_lic, own_lic:   r.own_lic,
            lease_lic: r.lease_lic, annual:    r.annual,
            advent:    r.advent,    order:     r.order_lic,
        })), true
    );

    // Table 2
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

    // Table 3
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

    // Table 4
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

    const params = new URLSearchParams({
        session_id: sid,
        software:   software.join(','),
    });

    const data = await apiFetch(`/keystore/table?${params}`);
    hideLoading();

    if (!data?.success) {
        toast('Failed to load keystore', 'error');
        return;
    }

    keystoreData = data.data;
    buildKeystoreLimits();
    renderKeystoreInline();
    toast('Keystore generated!', 'success');
}


// ─────────────────────────────────────────────
// BUILD KEYSTORE LIMITS
// ─────────────────────────────────────────────

function buildKeystoreLimits() {
    keystoreLimits = {};

    Object.keys(keystoreData).forEach(sw => {
        keystoreLimits[sw] = {};
        const data = allTableData[sw];
        if (!data) return;

        // Order limit from table1
        const t1row = data.t1.find(r =>
            r.software?.toLowerCase() === sw.toLowerCase()
        );
        if (t1row) {
            keystoreLimits[sw]['_order'] = t1row.order_lic || t1row.order || 0;
        }

        // Allocated limits — NPP, PP, CV
        Object.values(data.t2).forEach(swData => {
            swData.rows.forEach(r => {
                if (['NPP','PP','CV'].includes(r.label)) {
                    keystoreLimits[sw][r.label] = r.value;
                }
            });
        });

        // Required limits — CEC, VEC
        Object.values(data.t3).forEach(swData => {
            swData.rows.forEach(r => {
                if (['CEC','VEC'].includes(r.label)) {
                    keystoreLimits[sw][r.label] = r.value;
                }
            });
        });
    });
}


// ─────────────────────────────────────────────
// RENDER KEYSTORE
// ─────────────────────────────────────────────

function renderKeystoreInline() {
    let html = '<div class="card"><div class="card-title">🔑 Keystore</div>';

    Object.entries(keystoreData).forEach(([sw, swData]) => {
        const orderLimit = keystoreLimits[sw]?._order || 0;

        // Current total of all active keys
        const currentTotal = swData.keys
            .filter(k => k.active)
            .reduce((sum, k) => sum + (parseFloat(k.value) || 0), 0);

        const totalExceeds = currentTotal > orderLimit;

        html += `
        <h4 style="margin:20px 0 8px; color:#1A2B4A;
                   font-size:14px; font-weight:700;">
            ${swData.developer} — ${sw}
        </h4>

        <!-- Global summary bar -->
        <div data-sw-summary="${sw}"
             style="margin-bottom:12px; padding:10px 14px;
                    border-radius:6px;
                    background:${totalExceeds ? '#FEF2F2' : '#ECFDF5'};
                    border:1px solid ${totalExceeds ? '#FECACA' : '#A7F3D0'};
                    font-size:12px; font-weight:600;
                    color:${totalExceeds ? '#DC2626' : '#059669'};">
            Total Active Keys: <strong>${currentTotal}</strong> &nbsp;|&nbsp;
            Order Limit: <strong>${orderLimit}</strong>
            &nbsp;
            ${totalExceeds
                ? `⚠️ Exceeds by <strong>${currentTotal - orderLimit}</strong>`
                : '✅ Within limit'}
        </div>

        <div class="table-wrapper" style="margin-bottom:16px;">
        <table>
            <thead>
                <tr>
                    <th>Label</th>
                    <th>Key ID</th>
                    <th>Active</th>
                    <th>Value</th>
                    <th>Label Limit</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>`;

        // Group by label for per-label sum
        const byLabel = {};
        swData.keys.forEach(k => {
            if (!byLabel[k.label]) byLabel[k.label] = [];
            byLabel[k.label].push(k);
        });

        swData.keys.forEach(k => {
            const limit    = keystoreLimits[sw]?.[k.label];
            const labelSum = (byLabel[k.label] || [])
                .filter(lk => lk.active)
                .reduce((sum, lk) => sum + (parseFloat(lk.value) || 0), 0);
            const exceeds  = limit !== undefined && labelSum > limit;

            const valueDisplay = k.value !== null
                ? `<span style="font-weight:600;">${k.value}</span>`
                : `<input type="number"
                          id="kval_${sw}_${k.label}_${k.key_id}"
                          placeholder="Enter value"
                          onchange="validateKeystoreInput('${sw}','${k.label}',this)"
                          oninput="validateKeystoreInput('${sw}','${k.label}',this)"
                          style="width:100px; padding:4px 8px; border-radius:4px;
                                 font-size:13px; outline:none;
                                 border:1px solid ${exceeds ? '#DC2626' : '#2563EB'};
                                 background:${exceeds ? '#FEF2F2' : '#EFF6FF'};">`;

            const limitDisplay = limit !== undefined
                ? `<span style="font-size:11px; color:#6B7280;">${limit}</span>`
                : `<span style="font-size:11px; color:#9CA3AF;">—</span>`;

            const statusHtml = k.value === null && !exceeds
                ? `<span style="color:#DC2626; font-weight:600; background:#FEF2F2;
                                padding:3px 8px; border-radius:4px; font-size:11px;">
                    ⚠️ Needs Input
                   </span>`
                : exceeds
                ? `<span style="color:#DC2626; font-weight:600; background:#FEF2F2;
                                padding:3px 8px; border-radius:4px; font-size:11px;">
                    ⚠️ Exceeds Limit
                   </span>`
                : `<span style="color:#059669; font-weight:600; background:#ECFDF5;
                                padding:3px 8px; border-radius:4px; font-size:11px;">
                    ✅ OK
                   </span>`;

            html += `
            <tr id="krow_${sw}_${k.label}_${k.key_id}"
                style="${exceeds ? 'background:#FFF5F5 !important;' : ''}">
                <td style="font-weight:600;">${k.label}</td>
                <td style="font-family:monospace; font-size:12px;">${k.key_id}</td>
                <td>
                    <label class="toggle">
                        <input type="checkbox" ${k.active ? 'checked' : ''}
                               onchange="toggleKeyInline('${sw}','${k.label}','${k.key_id}',this)">
                        <span class="toggle-slider"></span>
                    </label>
                </td>
                <td>${valueDisplay}</td>
                <td>${limitDisplay}</td>
                <td id="kstatus_${sw}_${k.label}_${k.key_id}">${statusHtml}</td>
            </tr>`;
        });

        html += `</tbody></table></div>`;
    });

    html += `
    <div style="margin-top:16px; padding-top:16px; border-top:1px solid #E5E7EB;">
        <button class="btn btn-navy btn-sm" onclick="saveKeystoreValues()">
            💾 Save Input Values
        </button>
    </div>
    </div>`;

    document.getElementById('keystoreSection').innerHTML = html;
    document.getElementById('keystoreSection')
        .scrollIntoView({behavior:'smooth'});
}


// ─────────────────────────────────────────────
// VALIDATE KEYSTORE INPUT
// ─────────────────────────────────────────────

function validateKeystoreInput(sw, label, inputEl) {
    const limit = keystoreLimits[sw]?.[label];

    // Sum all inputs for this label + fixed values
    const swData   = keystoreData[sw];
    let labelSum   = 0;

    if (swData) {
        swData.keys.forEach(k => {
            if (k.label !== label || !k.active) return;
            if (k.value !== null) {
                labelSum += parseFloat(k.value) || 0;
            } else {
                const inp = document.getElementById(
                    `kval_${sw}_${label}_${k.key_id}`
                );
                labelSum += parseFloat(inp?.value) || 0;
            }
        });
    }

    const exceeds = limit !== undefined && labelSum > limit;

    // Update input style
    inputEl.style.borderColor = exceeds ? '#DC2626' : '#2563EB';
    inputEl.style.background  = exceeds ? '#FEF2F2' : '#EFF6FF';

    // Update row and status
    const keyId    = inputEl.id.replace(`kval_${sw}_${label}_`, '');
    const rowEl    = document.getElementById(`krow_${sw}_${label}_${keyId}`);
    const statusEl = document.getElementById(`kstatus_${sw}_${label}_${keyId}`);

    if (rowEl)    rowEl.style.background = exceeds ? '#FFF5F5' : '';
    if (statusEl) {
        statusEl.innerHTML = exceeds
            ? `<span style="color:#DC2626; font-weight:600; background:#FEF2F2;
                            padding:3px 8px; border-radius:4px; font-size:11px;">
                ⚠️ Exceeds ${label} limit (${limit})
               </span>`
            : `<span style="color:#059669; font-weight:600; background:#ECFDF5;
                            padding:3px 8px; border-radius:4px; font-size:11px;">
                ✅ OK
               </span>`;
    }

    // Update global summary bar
    updateGlobalTotal(sw);
}


// ─────────────────────────────────────────────
// UPDATE GLOBAL TOTAL
// ─────────────────────────────────────────────

function updateGlobalTotal(sw) {
    const orderLimit = keystoreLimits[sw]?._order || 0;
    const swData     = keystoreData[sw];
    if (!swData) return;

    let total = 0;
    swData.keys.forEach(k => {
        if (!k.active) return;
        if (k.value !== null) {
            total += parseFloat(k.value) || 0;
        } else {
            const inp = document.getElementById(
                `kval_${sw}_${k.label}_${k.key_id}`
            );
            total += parseFloat(inp?.value) || 0;
        }
    });

    const summaryEl = document.querySelector(`[data-sw-summary="${sw}"]`);
    if (!summaryEl) return;

    const exceeds = total > orderLimit;
    summaryEl.style.background  = exceeds ? '#FEF2F2' : '#ECFDF5';
    summaryEl.style.borderColor = exceeds ? '#FECACA' : '#A7F3D0';
    summaryEl.style.color       = exceeds ? '#DC2626' : '#059669';
    summaryEl.innerHTML = `
        Total Active Keys: <strong>${total}</strong> &nbsp;|&nbsp;
        Order Limit: <strong>${orderLimit}</strong>
        &nbsp;
        ${exceeds
            ? `⚠️ Exceeds by <strong>${total - orderLimit}</strong>`
            : '✅ Within limit'}`;
}


// ─────────────────────────────────────────────
// TOGGLE KEY INLINE
// ─────────────────────────────────────────────

async function toggleKeyInline(sw, dept, keyId, checkbox) {
    const params = new URLSearchParams({
        software: sw, dept, key_id: keyId
    });
    const data = await apiFetch(
        `/keystore/keys/toggle?${params}`, {method:'POST'}
    );
  