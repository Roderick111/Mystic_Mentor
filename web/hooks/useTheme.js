/**
 * useTheme.js - Theme Management Hook
 * Purpose: Provides theme switching functionality similar to next-themes
 */
const { createContext, useContext, useState, useEffect } = React;

// Create theme context
const ThemeContext = createContext();

// Theme Provider Component
const ThemeProvider = ({ children }) => {
    const [theme, setThemeState] = useState('dark'); // Default to dark
    const [mounted, setMounted] = useState(false);

    // Load theme from localStorage on mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        setThemeState(savedTheme);
        setMounted(true);
        
        // Apply theme to document
        applyTheme(savedTheme);
    }, []);

    // Apply theme to document
    const applyTheme = (newTheme) => {
        document.documentElement.setAttribute('data-theme', newTheme);
        document.documentElement.className = newTheme;
    };

    // Set theme function
    const setTheme = (newTheme) => {
        setThemeState(newTheme);
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    };

    const value = {
        theme,
        setTheme,
        mounted
    };

    return React.createElement(ThemeContext.Provider, { value }, children);
};

// Custom hook to use theme
const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

// Export for global use
window.ThemeProvider = ThemeProvider;
window.useTheme = useTheme; 