// static/app.js

const API = '';  // same origin

// ── Session Storage Helpers ───────────────

const Session = {
    get: (key) => {
        try { return JSON.parse(sessionStorage.getItem(key)); }
        catch { return null; }
    },
    set: (key, val) => sessionStorage.setItem(key, JSON.stringify(val)),
    clear: () => sessionStorage.clear(),
};

function getSessionId()  { return Session.get('session_id'); }
function getSoftware()   { return Session.get('software') || []; }
// Replace old getInputs() with:
function getInputs(software = null) {
    const allInputs = Session.get('inputs') || {};
    if (software) {
        return allInputs[software] || {annual: 0, advent: 0, onshore: 0};
    }
    return allInputs;
}
function getUploadData() { return Session.get('upload_data') || {}; }


// ── Toast ─────────────────────────────────

function toast(msg, type='info') {
    const el = document.getElementById('toast');
    if (!el) return;
    el.className  = `alert alert-${type}`;
    el.innerHTML  = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3500);
}


// ── Loading ───────────────────────────────

function showLoading(msg='Loading...') {
    const el = document.getElementById('loading');
    if (!el) return;
    el.querySelector('span').textContent = msg;
    el.classList.add('show');
}

function hideLoading() {
    const el = document.getElementById('loading');
    if (el) el.classList.remove('show');
}


// ── API Calls ─────────────────────────────

async function apiFetch(url, options={}) {
    try {
        const res  = await fetch(API + url, options);
        const data = await res.json();
        return data;
    } catch(e) {
        toast('Network error: ' + e.message, 'error');
        return null;
    }
}


// ── Sidebar Nav Unlock ────────────────────

function updateNav() {
    const sid      = getSessionId();
    const software = getSoftware();
    const hasSid   = !!sid;
    const hasSw    = software.length > 0;

    document.querySelectorAll('.nav-item[data-require]').forEach(item => {
        const req = item.dataset.require;
        let unlock = false;

        if (req === 'session')   unlock = hasSid;
        if (req === 'software')  unlock = hasSid && hasSw;

        item.classList.toggle('locked', !unlock);
    });

    // Update done badges
    const doneBadges = Session.get('done_tables') || [];
    doneBadges.forEach(t => {
        const badge = document.querySelector(`.nav-badge[data-table="${t}"]`);
        if (badge) badge.classList.add('done');
    });
}


// ── Mark Table Done ───────────────────────

function markDone(table) {
    const done = Session.get('done_tables') || [];
    if (!done.includes(table)) {
        done.push(table);
        Session.set('done_tables', done);
    }
    updateNav();
}


// ── Render Table from Data ────────────────

function renderTable(containerId, headers, rows, editable=false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = `<div class="table-wrapper"><table>
        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
        <tbody>`;

    rows.forEach((row, ri) => {
        const isTotal = Object.values(row).some(v =>
            typeof v === 'string' && v.toUpperCase() === 'TOTAL'
        );
        html += `<tr>`;
        Object.entries(row).forEach(([key, val]) => {
            let cls = isTotal ? 'total-row' : '';
            if (key === 'required' || key === 'value') {
                if (typeof val === 'number' && val < 0) cls += ' deficit';
                if (typeof val === 'number' && val > 0 && key !== 'required') cls += '';
            }
            const display = val === null ? '<em style="color:#999">User Input</em>' : val;
            if (editable && !isTotal && typeof val === 'number') {
                html += `<td class="${cls}">
                    <input class="edit-cell" data-row="${ri}" data-key="${key}"
                           value="${val}" style="display:none">
                    <span class="display-val">${display}</span>
                </td>`;
            } else {
                html += `<td class="${cls}">${display}</td>`;
            }
        });
        html += `</tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}


// ── Toggle Edit Mode ──────────────────────

function toggleEdit(btn) {
    const editing = btn.dataset.editing === 'true';
    const inputs  = document.querySelectorAll('.edit-cell');
    const spans   = document.querySelectorAll('.display-val');

    if (editing) {
        // Save mode — hide inputs, show updated spans
        inputs.forEach(inp => {
            inp.nextElementSibling.textContent = inp.value;
            inp.style.display = 'none';
            inp.nextElementSibling.style.display = '';
        });
        btn.textContent    = '✏️ Edit';
        btn.dataset.editing = 'false';
        toast('Changes saved locally', 'success');
    } else {
        // Edit mode — show inputs
        inputs.forEach(inp => {
            inp.style.display = '';
            inp.nextElementSibling.style.display = 'none';
        });
        btn.textContent    = '💾 Save';
        btn.dataset.editing = 'true';
    }
}


// ── Get Edited Table Data ─────────────────

function getEditedData(originalData) {
    const inputs = document.querySelectorAll('.edit-cell');
    const edited = JSON.parse(JSON.stringify(originalData));

    inputs.forEach(inp => {
        const ri  = parseInt(inp.dataset.row);
        const key = inp.dataset.key;
        if (edited[ri] !== undefined) {
            const val = parseFloat(inp.value);
            edited[ri][key] = isNaN(val) ? inp.value : val;
        }
    });
    return edited;
}


// ── Init page ─────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    updateNav();

    // Set active nav item
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.getAttribute('href') === path);
    });
});