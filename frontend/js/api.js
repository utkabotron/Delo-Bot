// API Client for Deloculator

const API_BASE = '/api';

const api = {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        // Add auth password if available
        const password = localStorage.getItem('app_password');
        if (password) {
            headers['X-Auth-Password'] = password;
        }

        // Add Telegram initData if available
        if (window.Telegram?.WebApp?.initData) {
            headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        if (response.status === 204) {
            return null;
        }

        return response.json();
    },

    // Projects
    projects: {
        list() {
            return api.request('/projects');
        },

        get(id) {
            return api.request(`/projects/${id}`);
        },

        create(data) {
            return api.request('/projects', {
                method: 'POST',
                body: JSON.stringify(data),
            });
        },

        update(id, data) {
            return api.request(`/projects/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data),
            });
        },

        delete(id) {
            return api.request(`/projects/${id}`, {
                method: 'DELETE',
            });
        },

        addItem(projectId, item) {
            return api.request(`/projects/${projectId}/items`, {
                method: 'POST',
                body: JSON.stringify(item),
            });
        },

        removeItem(projectId, itemId) {
            return api.request(`/projects/${projectId}/items/${itemId}`, {
                method: 'DELETE',
            });
        },

        updateItemQuantity(projectId, itemId, quantity) {
            return api.request(`/projects/${projectId}/items/${itemId}`, {
                method: 'PATCH',
                body: JSON.stringify({ quantity }),
            });
        },
    },

    // Catalog
    catalog: {
        search(query, limit = 20) {
            const params = new URLSearchParams({ q: query, limit });
            return api.request(`/catalog/search?${params}`);
        },

        grouped() {
            return api.request('/catalog/grouped');
        },

        sync() {
            return api.request('/catalog/sync', { method: 'POST' });
        },
    },
};
