// Alpine.js Components

function formatMoney(value) {
    const num = parseFloat(value) || 0;
    return num.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}

function pluralize(n, one, few, many) {
    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod100 >= 11 && mod100 <= 19) return many;
    if (mod10 === 1) return one;
    if (mod10 >= 2 && mod10 <= 4) return few;
    return many;
}

function formatItems(count) {
    return `${count} ${pluralize(count, 'позиция', 'позиции', 'позиций')}`;
}

function getBaseName(name, itemType) {
    if (itemType && name.endsWith(itemType)) {
        return name.slice(0, -itemType.length).trim();
    }
    return name;
}

// Dashboard Component
function dashboard() {
    return {
        projects: [],
        loading: true,
        showNewProjectModal: false,
        newProject: {
            name: '',
            client: '',
        },

        async init() {
            tg.init();
            await this.loadProjects();
        },

        async loadProjects() {
            this.loading = true;
            try {
                this.projects = await api.projects.list();
            } catch (error) {
                console.error('Failed to load projects:', error);
            } finally {
                this.loading = false;
            }
        },

        async createProject() {
            if (!this.newProject.name.trim()) return;

            try {
                const project = await api.projects.create(this.newProject);
                this.projects.unshift(project);
                this.showNewProjectModal = false;
                this.newProject = { name: '', client: '' };
                tg.hapticFeedback('success');
            } catch (error) {
                console.error('Failed to create project:', error);
                tg.hapticFeedback('error');
            }
        },

        async deleteProject(id) {
            if (!confirm('Удалить проект?')) return;

            try {
                await api.projects.delete(id);
                this.projects = this.projects.filter(p => p.id !== id);
                tg.hapticFeedback('medium');
            } catch (error) {
                console.error('Failed to delete project:', error);
                tg.hapticFeedback('error');
            }
        },

        openProject(id) {
            window.location.href = `/project/${id}`;
        },

        formatMoney,
        formatItems,
    };
}

// Project Editor Component
function projectEditor() {
    return {
        project: null,
        loading: true,
        showSettingsModal: false,
        showAddItemModal: false,
        showSearchResults: false,
        searchQuery: '',
        searchResults: [],
        editProject: {},
        // Каталог для dropdown
        catalogProducts: [],
        catalogLoading: false,
        selectedBaseName: '',
        selectedType: '',
        newItem: {
            name: '',
            item_type: '',
            base_price: 0,
            cost_price: 0,
            quantity: 1,
        },
        // Отслеживание редактирования количества
        editingItemId: null,

        async init() {
            tg.init();

            // Get project ID from URL
            const pathParts = window.location.pathname.split('/');
            const projectId = parseInt(pathParts[pathParts.length - 1]);

            if (projectId) {
                await this.loadProject(projectId);
            }

            // Setup Telegram back button
            tg.showBackButton(() => this.goBack());
        },

        async loadProject(id) {
            this.loading = true;
            try {
                this.project = await api.projects.get(id);
                this.editProject = {
                    name: this.project.name,
                    client: this.project.client,
                    global_discount: this.project.global_discount,
                    global_tax: this.project.global_tax,
                };
            } catch (error) {
                console.error('Failed to load project:', error);
            } finally {
                this.loading = false;
            }
        },

        async searchCatalog() {
            if (this.searchQuery.length < 1) {
                this.searchResults = [];
                return;
            }

            try {
                this.searchResults = await api.catalog.search(this.searchQuery);
                this.showSearchResults = true;
            } catch (error) {
                console.error('Failed to search catalog:', error);
            }
        },

        async addFromCatalog(product) {
            const item = {
                name: product.name,
                item_type: product.product_type,
                base_price: product.base_price,
                cost_price: product.cost_price,
                quantity: 1,
            };

            await this.addItem(item);
            this.searchQuery = '';
            this.searchResults = [];
            this.showSearchResults = false;
        },

        // Загрузка каталога для dropdown
        async loadCatalogForDropdown() {
            if (this.catalogProducts.length > 0) return;
            this.catalogLoading = true;
            try {
                this.catalogProducts = await api.catalog.grouped();
            } catch (error) {
                console.error('Failed to load catalog:', error);
            } finally {
                this.catalogLoading = false;
            }
        },

        // Уникальные базовые названия
        get availableNames() {
            const names = [...new Set(this.catalogProducts.map(p => p.base_name))];
            return names.sort();
        },

        // Типы для выбранного названия
        get availableTypes() {
            if (!this.selectedBaseName) return [];
            return this.catalogProducts
                .filter(p => p.base_name === this.selectedBaseName)
                .map(p => ({ type: p.product_type, product: p }));
        },

        // При выборе названия
        onBaseNameChange() {
            this.selectedType = '';
            this.newItem.name = '';
            this.newItem.item_type = '';
            this.newItem.base_price = 0;
            this.newItem.cost_price = 0;
        },

        // При выборе типа
        onTypeChange() {
            const found = this.catalogProducts.find(
                p => p.base_name === this.selectedBaseName && p.product_type === this.selectedType
            );
            if (found) {
                this.newItem.name = found.name;
                this.newItem.item_type = found.product_type;
                this.newItem.base_price = found.base_price;
                this.newItem.cost_price = found.cost_price;
            }
        },

        // Открытие модального окна добавления
        async openAddItemModal() {
            this.showAddItemModal = true;
            this.selectedBaseName = '';
            this.selectedType = '';
            this.newItem = {
                name: '',
                item_type: '',
                base_price: 0,
                cost_price: 0,
                quantity: 1,
            };
            await this.loadCatalogForDropdown();
        },

        async addManualItem() {
            if (!this.newItem.name.trim()) return;
            await this.addItem(this.newItem);
            this.showAddItemModal = false;
            this.selectedBaseName = '';
            this.selectedType = '';
            this.newItem = {
                name: '',
                item_type: '',
                base_price: 0,
                cost_price: 0,
                quantity: 1,
            };
        },

        async addItem(item) {
            try {
                await api.projects.addItem(this.project.id, item);
                await this.loadProject(this.project.id);
                tg.hapticFeedback('light');
            } catch (error) {
                console.error('Failed to add item:', error);
                tg.hapticFeedback('error');
            }
        },

        async removeItem(itemId) {
            try {
                await api.projects.removeItem(this.project.id, itemId);
                this.project.items = this.project.items.filter(i => i.id !== itemId);
                await this.loadProject(this.project.id);
                tg.hapticFeedback('medium');
            } catch (error) {
                console.error('Failed to remove item:', error);
                tg.hapticFeedback('error');
            }
        },

        async updateQuantity(item, delta) {
            const newQuantity = item.quantity + delta;
            if (newQuantity < 1) {
                await this.removeItem(item.id);
                return;
            }

            try {
                await api.projects.updateItemQuantity(this.project.id, item.id, newQuantity);
                await this.loadProject(this.project.id);
                tg.hapticFeedback('light');
            } catch (error) {
                console.error('Failed to update quantity:', error);
                tg.hapticFeedback('error');
            }
        },

        async saveQuantityDirect(item, newValue) {
            const newQuantity = parseInt(newValue);

            // Validation
            if (isNaN(newQuantity) || newQuantity < 1) {
                // Restore original value
                await this.loadProject(this.project.id);
                tg.hapticFeedback('error');
                return;
            }

            // If quantity unchanged, do nothing
            if (newQuantity === item.quantity) {
                return;
            }

            // Save via API
            try {
                await api.projects.updateItemQuantity(this.project.id, item.id, newQuantity);
                await this.loadProject(this.project.id);
                tg.hapticFeedback('success');
            } catch (error) {
                console.error('Failed to save quantity:', error);
                await this.loadProject(this.project.id);
                tg.hapticFeedback('error');
            }
        },

        async saveQuantityFromButton(item) {
            // Получаем значение из input
            const input = document.getElementById(`qty-input-${item.id}`);
            if (!input) return;

            const newValue = input.value;
            const newQuantity = parseInt(newValue);

            // Validation
            if (isNaN(newQuantity) || newQuantity < 1) {
                await this.loadProject(this.project.id);
                this.editingItemId = null;
                tg.hapticFeedback('error');
                return;
            }

            // If quantity unchanged, just close editor
            if (newQuantity === item.quantity) {
                this.editingItemId = null;
                input.blur();
                return;
            }

            // Save via API
            try {
                await api.projects.updateItemQuantity(this.project.id, item.id, newQuantity);
                await this.loadProject(this.project.id);
                this.editingItemId = null;
                input.blur();
                tg.hapticFeedback('success');
            } catch (error) {
                console.error('Failed to save quantity:', error);
                await this.loadProject(this.project.id);
                this.editingItemId = null;
                tg.hapticFeedback('error');
            }
        },

        async updateProject() {
            try {
                await api.projects.update(this.project.id, this.editProject);
                await this.loadProject(this.project.id);
                this.showSettingsModal = false;
                tg.hapticFeedback('success');
            } catch (error) {
                console.error('Failed to update project:', error);
                tg.hapticFeedback('error');
            }
        },

        goBack() {
            tg.hideBackButton();
            window.location.href = '/';
        },

        formatMoney,
    };
}
