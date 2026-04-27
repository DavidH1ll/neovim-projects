/**
 * MSP Password Generator - Frontend Application
 */

let companies = [];
let currentCompanyId = null;

// DOM Elements
const companySelect = document.getElementById('company-select');
const schemeInfo = document.getElementById('scheme-info');
const generateBtn = document.getElementById('generate-btn');
const passwordResult = document.getElementById('password-result');
const passwordOutput = document.getElementById('password-output');
const copyBtn = document.getElementById('copy-btn');
const regenerateBtn = document.getElementById('regenerate-btn');
const strengthBadge = document.getElementById('strength-badge');
const companiesList = document.getElementById('companies-list');
const addCompanyToggle = document.getElementById('add-company-toggle');
const addCompanyForm = document.getElementById('add-company-form');
const saveCompanyBtn = document.getElementById('save-company-btn');
const cancelAddBtn = document.getElementById('cancel-add-btn');
const toast = document.getElementById('toast');

// Initialize
async function init() {
    await loadCompanies();
    setupEventListeners();
}

// Load companies from API
async function loadCompanies() {
    try {
        const response = await fetch('/api/companies');
        companies = await response.json();
        populateCompanySelect();
        renderCompaniesList();
    } catch (error) {
        showToast('Failed to load companies', 'error');
    }
}

// Populate dropdown
function populateCompanySelect() {
    companySelect.innerHTML = '<option value="">-- Choose a company --</option>';
    companies.forEach(company => {
        const option = document.createElement('option');
        option.value = company.id;
        option.textContent = company.name;
        companySelect.appendChild(option);
    });
}

// Render companies list
function renderCompaniesList() {
    if (companies.length === 0) {
        companiesList.innerHTML = '<div class="empty-state">No companies yet. Add one above.</div>';
        return;
    }

    companiesList.innerHTML = companies.map(company => {
        const s = company.scheme;
        const rules = [];
        if (s.require_uppercase) rules.push('A-Z');
        if (s.require_lowercase) rules.push('a-z');
        if (s.require_digits) rules.push('0-9');
        if (s.require_symbols) rules.push('!@#');
        if (s.exclude_ambiguous) rules.push('no ambiguous');

        const schemeText = `${s.min_length}-${s.max_length} chars · ${rules.join(', ')}`;
        const prefixSuffix = (s.custom_prefix || s.custom_suffix)
            ? ` · Format: ${s.custom_prefix || ''}[pass]${s.custom_suffix || ''}`
            : '';

        return `
            <div class="company-item">
                <div>
                    <div class="company-name">${escapeHtml(company.name)}</div>
                    <div class="company-scheme">${schemeText}${prefixSuffix}</div>
                </div>
                <div class="company-actions">
                    <button class="btn-delete" data-id="${company.id}" title="Delete company">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    // Attach delete handlers
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', () => deleteCompany(btn.dataset.id));
    });
}

// Update scheme display
function updateSchemeDisplay(companyId) {
    const company = companies.find(c => c.id === companyId);
    if (!company) {
        schemeInfo.classList.add('hidden');
        generateBtn.disabled = true;
        return;
    }

    const s = company.scheme;
    document.getElementById('scheme-length').textContent = `${s.min_length}-${s.max_length}`;
    document.getElementById('scheme-upper').textContent = s.require_uppercase ? 'Yes' : 'No';
    document.getElementById('scheme-lower').textContent = s.require_lowercase ? 'Yes' : 'No';
    document.getElementById('scheme-digits').textContent = s.require_digits ? 'Yes' : 'No';
    document.getElementById('scheme-symbols').textContent = s.require_symbols ? 'Yes' : 'No';
    document.getElementById('scheme-ambiguous').textContent = s.exclude_ambiguous ? 'Yes' : 'No';

    const customEl = document.getElementById('scheme-custom');
    if (s.custom_prefix || s.custom_suffix) {
        document.getElementById('scheme-format').textContent =
            `${s.custom_prefix || ''}[password]${s.custom_suffix || ''}`;
        customEl.classList.remove('hidden');
    } else {
        customEl.classList.add('hidden');
    }

    schemeInfo.classList.remove('hidden');
    generateBtn.disabled = false;
    currentCompanyId = companyId;
}

// Generate password
async function generatePassword() {
    if (!currentCompanyId) return;

    generateBtn.disabled = true;
    generateBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg>
        Generating...
    `;

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_id: currentCompanyId }),
        });

        const data = await response.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        passwordOutput.value = data.password;
        passwordResult.classList.remove('hidden');

        // Update strength badge
        strengthBadge.className = 'strength-badge';
        strengthBadge.classList.add(`strength-${data.strength.toLowerCase()}`);
        strengthBadge.textContent = data.strength;

    } catch (error) {
        showToast('Failed to generate password', 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"></polyline>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Generate Password
        `;
    }
}

// Copy to clipboard
async function copyToClipboard() {
    const password = passwordOutput.value;
    if (!password) return;

    try {
        await navigator.clipboard.writeText(password);
        showToast('Password copied to clipboard!');
    } catch {
        // Fallback
        passwordOutput.select();
        document.execCommand('copy');
        showToast('Password copied to clipboard!');
    }
}

// Add company
async function saveCompany() {
    const name = document.getElementById('new-name').value.trim();
    if (!name) {
        showToast('Company name is required', 'error');
        return;
    }

    const minLength = parseInt(document.getElementById('new-min').value);
    const maxLength = parseInt(document.getElementById('new-max').value);

    if (minLength > maxLength) {
        showToast('Min length cannot be greater than max length', 'error');
        return;
    }

    const body = {
        name: name,
        min_length: minLength,
        max_length: maxLength,
        require_uppercase: document.getElementById('new-upper').checked,
        require_lowercase: document.getElementById('new-lower').checked,
        require_digits: document.getElementById('new-digits').checked,
        require_symbols: document.getElementById('new-symbols').checked,
        exclude_ambiguous: document.getElementById('new-ambiguous').checked,
        custom_prefix: document.getElementById('new-prefix').value.trim(),
        custom_suffix: document.getElementById('new-suffix').value.trim(),
    };

    try {
        const response = await fetch('/api/companies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        showToast(`Company "${name}" added!`);
        resetAddForm();
        addCompanyForm.classList.add('hidden');
        await loadCompanies();

        // Auto-select the new company
        companySelect.value = data.id;
        updateSchemeDisplay(data.id);

    } catch (error) {
        showToast('Failed to add company', 'error');
    }
}

// Delete company
async function deleteCompany(companyId) {
    const company = companies.find(c => c.id === companyId);
    if (!company) return;

    if (!confirm(`Delete "${company.name}"?`)) return;

    try {
        const response = await fetch(`/api/companies/${companyId}`, {
            method: 'DELETE',
        });

        const data = await response.json();

        if (data.error) {
            showToast(data.error, 'error');
            return;
        }

        showToast('Company deleted');

        // Clear selection if deleted company was selected
        if (currentCompanyId === companyId) {
            companySelect.value = '';
            updateSchemeDisplay('');
            passwordResult.classList.add('hidden');
        }

        await loadCompanies();

    } catch (error) {
        showToast('Failed to delete company', 'error');
    }
}

// Reset add form
function resetAddForm() {
    document.getElementById('new-name').value = '';
    document.getElementById('new-min').value = '12';
    document.getElementById('new-max').value = '16';
    document.getElementById('new-upper').checked = true;
    document.getElementById('new-lower').checked = true;
    document.getElementById('new-digits').checked = true;
    document.getElementById('new-symbols').checked = true;
    document.getElementById('new-ambiguous').checked = false;
    document.getElementById('new-prefix').value = '';
    document.getElementById('new-suffix').value = '';
}

// Show toast notification
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.classList.remove('hidden');
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.classList.add('hidden'), 300);
    }, 2500);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
function setupEventListeners() {
    companySelect.addEventListener('change', (e) => {
        updateSchemeDisplay(e.target.value);
        passwordResult.classList.add('hidden');
    });

    generateBtn.addEventListener('click', generatePassword);
    regenerateBtn.addEventListener('click', generatePassword);
    copyBtn.addEventListener('click', copyToClipboard);

    addCompanyToggle.addEventListener('click', () => {
        addCompanyForm.classList.toggle('hidden');
    });

    cancelAddBtn.addEventListener('click', () => {
        addCompanyForm.classList.add('hidden');
        resetAddForm();
    });

    saveCompanyBtn.addEventListener('click', saveCompany);
}

// Start
init();
