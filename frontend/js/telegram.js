// Telegram WebApp Integration

const tg = {
    app: window.Telegram?.WebApp,

    init() {
        if (!this.app) {
            console.log('Not running in Telegram WebApp');
            return;
        }

        // Expand to full height
        this.app.expand();

        // Disable vertical swipes to prevent viewport resize on keyboard
        if (this.app.isVersionAtLeast && this.app.isVersionAtLeast('6.1')) {
            this.app.disableVerticalSwipes();
        }

        // Apply theme - DISABLED (always use light theme)
        // this.applyTheme();

        // Force light theme by overriding CSS variables
        this.forceLightTheme();

        // Apply safe area insets
        this.applySafeArea();

        // Ready signal
        this.app.ready();
    },

    forceLightTheme() {
        // Force light theme colors regardless of Telegram theme
        const root = document.documentElement;
        root.style.setProperty('--tg-bg-color', '#ffffff');
        root.style.setProperty('--tg-text-color', '#000000');
        root.style.setProperty('--tg-hint-color', '#6c757d');
        root.style.setProperty('--tg-link-color', '#2481cc');
        root.style.setProperty('--tg-button-color', '#2481cc');
        root.style.setProperty('--tg-button-text-color', '#ffffff');
        root.style.setProperty('--tg-secondary-bg-color', '#f7f7f7');
        root.style.setProperty('--tg-section-bg-color', '#ffffff');
        root.style.setProperty('--tg-subtitle-text-color', '#707070');
        root.style.setProperty('--tg-border-color', 'rgba(108, 117, 125, 0.35)');

        console.log('Light theme forced');
    },

    applySafeArea() {
        if (!this.app) return;

        const root = document.documentElement;

        // Content safe area (area below Telegram header)
        const contentInset = this.app.contentSafeAreaInset || {};
        const safeInset = this.app.safeAreaInset || {};

        // Use content safe area top (space below Telegram's header)
        const topInset = (contentInset.top || 0) + (safeInset.top || 0);
        root.style.setProperty('--tg-content-safe-area-top', `${topInset}px`);
        root.style.setProperty('--tg-safe-area-bottom', `${safeInset.bottom || 0}px`);

        // Add padding to header elements
        const headers = document.querySelectorAll('header');
        headers.forEach(header => {
            header.style.paddingTop = `${topInset}px`;
        });
    },

    applyTheme() {
        if (!this.app) return;

        const root = document.documentElement;
        const theme = this.app.themeParams;

        if (theme.bg_color) {
            root.style.setProperty('--tg-bg-color', theme.bg_color);
        }
        if (theme.secondary_bg_color) {
            root.style.setProperty('--tg-secondary-bg-color', theme.secondary_bg_color);
        }
        if (theme.section_bg_color) {
            root.style.setProperty('--tg-section-bg-color', theme.section_bg_color);
        }
        if (theme.text_color) {
            root.style.setProperty('--tg-text-color', theme.text_color);
        }
        if (theme.subtitle_text_color) {
            root.style.setProperty('--tg-subtitle-text-color', theme.subtitle_text_color);
        }
        if (theme.hint_color) {
            root.style.setProperty('--tg-hint-color', theme.hint_color);
        }
        if (theme.link_color) {
            root.style.setProperty('--tg-link-color', theme.link_color);
        }
        if (theme.button_color) {
            root.style.setProperty('--tg-button-color', theme.button_color);
        }
        if (theme.button_text_color) {
            root.style.setProperty('--tg-button-text-color', theme.button_text_color);
        }

        console.log('Telegram theme applied:', theme);
    },

    showMainButton(text, callback) {
        if (!this.app) return;

        this.app.MainButton.setText(text);
        this.app.MainButton.onClick(callback);
        this.app.MainButton.show();
    },

    hideMainButton() {
        if (!this.app) return;
        this.app.MainButton.hide();
    },

    showBackButton(callback) {
        if (!this.app) return;

        this.app.BackButton.onClick(callback);
        this.app.BackButton.show();
    },

    hideBackButton() {
        if (!this.app) return;
        this.app.BackButton.hide();
    },

    hapticFeedback(type = 'light') {
        if (!this.app?.HapticFeedback) return;

        switch (type) {
            case 'light':
                this.app.HapticFeedback.impactOccurred('light');
                break;
            case 'medium':
                this.app.HapticFeedback.impactOccurred('medium');
                break;
            case 'heavy':
                this.app.HapticFeedback.impactOccurred('heavy');
                break;
            case 'success':
                this.app.HapticFeedback.notificationOccurred('success');
                break;
            case 'error':
                this.app.HapticFeedback.notificationOccurred('error');
                break;
        }
    },

    close() {
        if (this.app) {
            this.app.close();
        }
    },
};
