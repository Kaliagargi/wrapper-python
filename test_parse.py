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

    if (!data?.success) { toast('Failed to load keystore', 'error'); return; }

    renderKeystoreInline(data.data);
    toast('Keystore generated!', 'success');
}

// Store limits for validation
let keystoreLimits = {};  // {sw: {label: limit, _order: orderLimit}}

function renderKeystoreInline(keystoreData, tableData) {
    // Build limits from allTableData
    Object.entries(allTableData).forEach(([sw, data]) => {
        keystoreLimits[sw] = {};

        // Order limit from table1
        const t1row = data.t1.find(r => r.software === sw || r.software?.toLowerCase() === sw.toLowerCase());
        if (t1row) keystoreLimits[sw]['_order'] = t1row.order_lic || t1row.order || 0;

        // Allocated limits (NPP, PP, CV)
        Object.entries(data.t2).forEach(([s, swData]) => {
            swData.rows.forEach(r => {
                if (['NPP','PP','CV'].includes(r.label)) {
                    keystoreLimits[sw][r.label] = r.value;
                }
            });
        });

        // Required limits (CEC, VEC)
        Object.entries(data.t3).forEach(([s, swData]) => {
            swData.rows.forEach(r => {
                if (['CEC','VEC'].includes(r.label)) {
                    keystoreLimits[sw][r.label] = r.value;
                }
            });
        });
    });

    let html = '<div class="card"><div class="card-title">🔑 Keystore</div>';

    Object.entries(keystoreData).forEach(([sw, swData]) => {
        const orderLimit = keystoreLimits[sw]?._order || 0;

        // Calculate current total of all active keys
        const currentTotal = swData.keys
            .filter(k => k.active)
            .reduce((sum, k) => sum + (k.value || 0), 0);

        const totalExceeds = currentTotal > orderLimit;

        html += `
        <h4 style="margin:16px 0 4px; color:#1A2B4A; font-size:14px; font-weight:700;">
            ${swData.developer} — ${sw}
        </h4>
        <div style="margin-bottom:12px; padding:8px 12px; border-radius:6px;
                    background:${totalExceeds ? '#FEF2F2' : '#ECFDF5'};
                    border:1px solid ${totalExceeds ? '#FECACA' : '#A7F3D0'};
                    font-size:12px; font-weight:600;
                    color:${totalExceeds ? '#DC2626' : '#059669'};">
            Total Active Keys: <strong>${currentTotal}</strong> |
            Order Limit: <strong>${orderLimit}</strong>
            ${totalExceeds
                ? ` | ⚠️ Exceeds by ${currentTotal - orderLimit}`
                : ' | ✅ Within limit'}
        </div>
        <div class="table-wrapper" style="margin-bottom:16px;">
        <table>
            <thead>
                <tr>
                    <th>Label</th>
                    <th>Key ID</th>
                    <th>Active</th>
                    <th>Value</th>
                    <th>Limit</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>`;

        // Group keys by label for per-label validation
        const byLabel = {};
        swData.keys.forEach(k => {
            if (!byLabel[k.label]) byLabel[k.label] = [];
            byLabel[k.label].push(k);
        });

        swData.keys.forEach(k => {
            const limit     = keystoreLimits[sw]?.[k.label];
            const labelKeys = byLabel[k.label] || [];
            const labelSum  = labelKeys
                .filter(lk => lk.active)
                .reduce((sum, lk) => sum + (lk.value || 0), 0);
            const exceeds   = limit !== undefined && labelSum > limit;

            const valueDisplay = k.value !== null
                ? `<span style="font-weight:600;">${k.value}</span>`
                : `<input type="number"
                          placeholder="Enter value"
                          id="kval_${sw}_${k.label}_${k.key_id}"
                          onchange="validateKeystoreInput('${sw}', '${k.label}', this)"
                          style="width:100px; padding:4px 8px;
                                 border:1px solid ${exceeds ? '#DC2626' : '#2563EB'};
                                 border-radius:4px;
                                 background:${exceeds ? '#FEF2F2' : '#EFF6FF'};
                                 font-size:13px;">`;

            const limitDisplay = limit !== undefined
                ? `<span style="font-size:11px; color:#6B7280;">${limit}</span>`
                : `<span style="font-size:11px; color:#9CA3AF;">—</span>`;

            const status = k.value === null
                ? `<span style="color:#DC2626; font-weight:600;
                                background:#FEF2F2; padding:3px 8px;
                                border-radius:4px; font-size:11px;">
                    ⚠️ Needs Input
                   </span>`
                : exceeds
                ? `<span style="color:#DC2626; font-weight:600;
                                background:#FEF2F2; padding:3px 8px;
                                border-radius:4px; font-size:11px;">
                    ⚠️ Exceeds Limit
                   </span>`
                : `<span style="color:#059669; font-weight:600;
                                background:#ECFDF5; padding:3px 8px;
                                border-radius:4px; font-size:11px;">
                    ✅ OK
                   </span>`;

            html += `
            <tr id="krow_${sw}_${k.label}_${k.key_id}"
                style="${exceeds ? 'background:#FFF5F5;' : ''}">
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
                <td>${limitDisplay}</td>
                <td id="kstatus_${sw}_${k.label}_${k.key_id}">${status}</td>
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

function validateKeystoreInput(sw, label, inputEl) {
    const val       = parseFloat(inputEl.value) || 0;
    const limit     = keystoreLimits[sw]?.[label];
    const orderLimit = keystoreLimits[sw]?._order || 0;

    // Get all key values for this label
    const labelInputs = document.querySelectorAll(`[id^="kval_${sw}_${label}_"]`);
    let labelSum = 0;
    labelInputs.forEach(inp => {
        labelSum += parseFloat(inp.value) || 0;
    });

    // Also add fixed values for this label from keystoreData
    const swData = Object.values(keystoreData).find((_, i) =>
        Object.keys(keystoreData)[i] === sw
    );

    // Per label validation
    const labelExceeds = limit !== undefined && labelSum > limit;

    inputEl.style.borderColor = labelExceeds ? '#DC2626' : '#2563EB';
    inputEl.style.background  = labelExceeds ? '#FEF2F2' : '#EFF6FF';

    // Update status cell
    // Find the key_id from input id
    const keyId    = inputEl.id.replace(`kval_${sw}_${label}_`, '');
    const statusEl = document.getElementById(`kstatus_${sw}_${label}_${keyId}`);
    const rowEl    = document.getElementById(`krow_${sw}_${label}_${keyId}`);

    if (statusEl) {
        statusEl.innerHTML = labelExceeds
            ? `<span style="color:#DC2626; font-weight:600;
                            background:#FEF2F2; padding:3px 8px;
                            border-radius:4px; font-size:11px;">
                ⚠️ Exceeds ${label} limit (${limit})
               </span>`
            : `<span style="color:#059669; font-weight:600;
                            background:#ECFDF5; padding:3px 8px;
                            border-radius:4px; font-size:11px;">
                ✅ OK
               </span>`;
    }

    if (rowEl) {
        rowEl.style.background = labelExceeds ? '#FFF5F5' : '';
    }

    // Recalculate global total and update summary
    updateGlobalTotal(sw);
}

function updateGlobalTotal(sw) {
    const orderLimit = keystoreLimits[sw]?._order || 0;
    const swData     = keystoreData[sw];
    if (!swData) return;

    // Sum all active keys (fixed + typed)
    let total = 0;
    swData.keys.forEach(k => {
        if (!k.active) return;
        if (k.value !== null) {
            total += k.value;
        } else {
            const inp = document.getElementById(`kval_${sw}_${k.label}_${k.key_id}`);
            total += parseFloat(inp?.value) || 0;
        }
    });

    // Update summary bar — find it by sw name
    const summaryEl = document.querySelector(`[data-sw-summary="${sw}"]`);
    if (summaryEl) {
        const exceeds = total > orderLimit;
        summaryEl.style.background   = exceeds ? '#FEF2F2' : '#ECFDF5';
        summaryEl.style.borderColor  = exceeds ? '#FECACA' : '#A7F3D0';
        summaryEl.style.color        = exceeds ? '#DC2626' : '#059669';
        summaryEl.innerHTML = `
            Total Active Keys: <strong>${total}</strong> |
            Order Limit: <strong>${orderLimit}</strong>
            ${exceeds
                ? ` | ⚠️ Exceeds by ${total - orderLimit}`
                : ' | ✅ Within limit'}`;
    }
}

// Replace the summary div with:
html += `
<div data-sw-summary="${sw}"
     style="margin-bottom:12px; padding:8px 12px; border-radius:6px;
            background:${totalExceeds ? '#FEF2F2' : '#ECFDF5'};
            border:1px solid ${totalExceeds ? '#FECACA' : '#A7F3D0'};
            font-size:12px; font-weight:600;
            color:${totalExceeds ? '#DC2626' : '#059669'};">
    Total Active Keys: <strong>${currentTotal}</strong> |
    Order Limit: <strong>${orderLimit}</strong>
    ${totalExceeds
        ? ` | ⚠️ Exceeds by ${currentTotal - orderLimit}`
        : ' | ✅ Within limit'}
</div>`;