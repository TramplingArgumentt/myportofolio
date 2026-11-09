function initializePortfolioApi(config) {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const empty = document.getElementById('empty');
    const grid = document.getElementById('grid');
    const searchForm = document.getElementById(config.searchFormId);
    const searchInput = document.getElementById('search-input');
    const form = document.getElementById(config.formId);
    let activeRequest;
    let searchTimer;
    const itemsById = new Map();
    let editModal;
    let editForm;
    let editingItemId;

    function showState({ loading: isLoading = false, error: hasError = false,
        empty: isEmpty = false, grid: hasItems = false }) {
        loading.classList.toggle('hide', !isLoading);
        error.classList.toggle('hide', !hasError);
        empty.classList.toggle('hide', !isEmpty);
        grid.classList.toggle('hide', !hasItems);
    }

    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(';').map(value => value.trim())
            .find(value => value.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
    }

    function detailUrl(pattern, id) {
        return pattern.replace('00000000-0000-0000-0000-000000000000', id);
    }

    function errorMessage(data, status) {
        const messages = Object.values(data).flatMap(value =>
            Array.isArray(value) ? value : [value]
        ).filter(value => typeof value === 'string');
        return messages.join(' ') || `Request failed (HTTP ${status}).`;
    }

    async function request(url, method, payload) {
        const headers = { Accept: 'application/json' };
        const options = { method, headers };
        if (method !== 'GET' && method !== 'HEAD') {
            headers['Content-Type'] = 'application/json';
            headers['X-CSRFToken'] = getCookie('csrftoken');
            if (payload !== undefined) options.body = JSON.stringify(payload);
        }
        const response = await fetch(url, options);
        const data = response.status === 204 ? null : await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(errorMessage(data || {}, response.status));
        return data;
    }

    function createEditModal() {
        if (!config.canEdit || !config.editFields?.length) return;

        editModal = document.createElement('div');
        editModal.className = 'project-form-modal';
        editModal.id = `${config.modalId}-edit`;
        editModal.setAttribute('popover', 'auto');
        editModal.setAttribute('role', 'dialog');
        editModal.setAttribute('aria-modal', 'true');
        editModal.setAttribute('aria-labelledby', `${editModal.id}-title`);

        const backdrop = document.createElement('button');
        backdrop.type = 'button';
        backdrop.className = 'project-form-modal__backdrop';
        backdrop.setAttribute('aria-label', 'Close edit dialog');
        backdrop.addEventListener('click', () => editModal.hidePopover());

        const content = document.createElement('div');
        content.className = 'project-form-modal__content';
        const heading = document.createElement('h2');
        heading.id = `${editModal.id}-title`;
        heading.textContent = `Edit ${config.label}`;
        const close = document.createElement('button');
        close.type = 'button';
        close.className = 'project-form-modal__close';
        close.setAttribute('aria-label', 'Close edit dialog');
        close.textContent = '×';
        close.addEventListener('click', () => editModal.hidePopover());

        editForm = document.createElement('form');
        editForm.className = 'project-form';
        for (const field of config.editFields) {
            const group = document.createElement('div');
            group.className = 'form-group';
            const label = document.createElement('label');
            label.textContent = field.label;
            if (field.type === 'tags') {
                const choices = document.createElement('div');
                choices.className = 'edit-tag-choices';
                for (const tag of config.tagOptions || []) {
                    const choice = document.createElement('label');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.name = field.name;
                    checkbox.value = tag.id;
                    choice.append(checkbox, document.createTextNode(tag.name));
                    choices.appendChild(choice);
                }
                group.append(label, choices);
            } else {
                const control = document.createElement(
                    field.type === 'textarea' ? 'textarea'
                        : field.type === 'select' ? 'select' : 'input',
                );
                control.name = field.name;
                if (field.type === 'select') {
                    const select = control;
                    for (const [value, text] of field.choices) {
                        const option = document.createElement('option');
                        option.value = value;
                        option.textContent = text;
                        select.appendChild(option);
                    }
                } else if (field.type !== 'select') {
                    control.type = field.type;
                }
                label.htmlFor = `${editModal.id}-${field.name}`;
                control.id = label.htmlFor;
                group.append(label, control);
            }
            editForm.appendChild(group);
        }

        const actions = document.createElement('div');
        actions.className = 'project-form-modal__actions';
        const cancel = document.createElement('button');
        cancel.type = 'button';
        cancel.className = 'button button-secondary';
        cancel.textContent = 'Cancel';
        cancel.addEventListener('click', () => editModal.hidePopover());
        const save = document.createElement('button');
        save.type = 'submit';
        save.className = 'button';
        save.textContent = 'Save changes';
        actions.append(cancel, save);
        editForm.appendChild(actions);

        content.append(close, heading, editForm);
        editModal.append(backdrop, content);
        document.body.appendChild(editModal);

        editForm.addEventListener('submit', async event => {
            event.preventDefault();
            const submit = editForm.querySelector('button[type="submit"]');
            submit.disabled = true;
            const values = new FormData(editForm);
            const payload = {};
            for (const field of config.editFields) {
                if (field.type === 'tags') {
                    payload[field.name] = values.getAll(field.name);
                    continue;
                }
                const value = values.get(field.name);
                payload[field.name] = config.nullFields.includes(field.name) && value === ''
                    ? null
                    : value;
            }
            try {
                await request(detailUrl(config.detailUrl, editingItemId), 'PATCH', payload);
                editModal.hidePopover();
                showToast('Success', `${config.label} updated.`, 'success');
                await load(searchInput.value.trim());
            } catch (exception) {
                showToast(`Could not update ${config.label.toLowerCase()}`,
                    exception.message, 'error');
            } finally {
                submit.disabled = false;
            }
        });
    }

    function editValue(value, type) {
        if (value === null || value === undefined) return '';
        if (type === 'date') return String(value).slice(0, 10);
        if (type === 'datetime-local') {
            const date = new Date(value);
            if (Number.isNaN(date.getTime())) return '';
            return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
                .toISOString().slice(0, 16);
        }
        return value;
    }

    function openEdit(item) {
        if (!editModal) return;
        editingItemId = item.id;
        for (const field of config.editFields) {
            if (field.type === 'tags') {
                const selected = new Set(item[field.name]);
                editForm.querySelectorAll(`input[name="${field.name}"]`).forEach(input => {
                    const tag = (config.tagOptions || []).find(option => option.id === input.value);
                    input.checked = tag && selected.has(tag.name);
                });
            } else {
                const control = editForm.elements.namedItem(field.name);
                control.value = editValue(item[field.name], field.type);
            }
        }
        editModal.showPopover();
    }

    function renderActions(item) {
        const actions = document.createElement('div');
        actions.className = 'project-card-actions';
        const buttons = document.createElement('div');
        buttons.className = 'project-actions';
        if (config.authenticated) {
            const star = document.createElement('button');
            star.type = 'button';
            star.className = `button button-star${item.is_starred ? ' is-starred' : ''}`;
            star.dataset.action = 'star';
            star.dataset.id = item.id;
            star.title = item.starred_by_names || 'Be the first to star';
            star.textContent = `${item.is_starred ? 'Unstar' : 'Star'} (${item.star_count})`;
            buttons.appendChild(star);
        } else {
            const login = document.createElement('a');
            login.href = config.loginUrl;
            login.className = 'button';
            login.textContent = `Login to star (${item.star_count})`;
            buttons.appendChild(login);
        }
        if (config.canEdit) {
            const edit = document.createElement('button');
            edit.type = 'button';
            edit.className = 'button';
            edit.dataset.action = 'edit';
            edit.dataset.id = item.id;
            edit.textContent = `Edit ${config.label}`;
            buttons.appendChild(edit);
        }
        if (config.isOwner) {
            const remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'button button-danger';
            remove.dataset.action = 'delete';
            remove.dataset.id = item.id;
            remove.textContent = 'Delete';
            buttons.appendChild(remove);
        }
        actions.appendChild(buttons);
        return actions;
    }

    async function load(query = '') {
        if (activeRequest) activeRequest.abort();
        activeRequest = new AbortController();
        showState({ loading: true });
        const url = new URL(config.listUrl, window.location.origin);
        if (query) url.searchParams.set('name', query);
        try {
            const response = await fetch(url, {
                headers: { Accept: 'application/json' },
                signal: activeRequest.signal,
            });
            if (!response.ok) throw new Error(`Request failed (HTTP ${response.status}).`);
            const items = await response.json();
            itemsById.clear();
            items.forEach(item => itemsById.set(item.id, item));
            const cards = items.map(item => {
                const card = config.renderCard(item);
                const actions = renderActions(item);
                const actionsParent = config.actionsParentSelector
                    ? card.querySelector(config.actionsParentSelector)
                    : card;
                actionsParent.appendChild(actions);
                return card;
            });
            grid.replaceChildren(...cards);
            showState({ grid: cards.length > 0, empty: cards.length === 0 });
        } catch (exception) {
            if (exception.name === 'AbortError') return;
            console.error(`Could not load ${config.label.toLowerCase()} data:`, exception);
            showState({ error: true });
        }
    }

    if (form) {
        form.addEventListener('submit', async event => {
            event.preventDefault();
            const submit = form.querySelector('button[type="submit"]');
            submit.disabled = true;
            const fields = new FormData(form);
            const payload = {};
            for (const [key, value] of fields.entries()) {
                if (key === 'csrfmiddlewaretoken') continue;
                if (key === 'tags') {
                    payload.tags = fields.getAll('tags');
                } else {
                    payload[key] = value;
                }
            }
            for (const field of config.nullFields) {
                if (payload[field] === '') payload[field] = null;
            }
            try {
                await request(config.listUrl, 'POST', payload);
                form.reset();
                document.getElementById(config.modalId).hidePopover();
                showToast('Success', `${config.label} created.`, 'success');
                await load(searchInput.value.trim());
            } catch (exception) {
                showToast(`Could not create ${config.label.toLowerCase()}`,
                    exception.message, 'error');
            } finally {
                submit.disabled = false;
            }
        });
    }

    createEditModal();

    grid.addEventListener('click', async event => {
        const button = event.target.closest('button[data-action]');
        if (!button || button.disabled) return;
        const { action, id } = button.dataset;
        if (action === 'delete' && !window.confirm(`Delete this ${config.label.toLowerCase()}?`)) return;
        if (action === 'edit') {
            const item = itemsById.get(id);
            if (item) openEdit(item);
            return;
        }
        const pattern = action === 'star' ? config.starUrl : config.detailUrl;
        button.disabled = true;
        try {
            await request(detailUrl(pattern, id),
                action === 'star' ? 'POST' : 'DELETE');
            showToast('Success', action === 'star' ? 'Star updated.'
                : action === 'delete' ? `${config.label} deleted.` : `${config.label} updated.`,
            'success');
            await load(searchInput.value.trim());
        } catch (exception) {
            showToast('Request failed', exception.message, 'error');
        } finally {
            button.disabled = false;
        }
    });

    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => load(searchInput.value.trim()), 300);
    });
    searchForm.addEventListener('submit', event => {
        event.preventDefault();
        clearTimeout(searchTimer);
        load(searchInput.value.trim());
    });
    load(searchInput.value.trim());
}
