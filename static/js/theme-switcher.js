document.addEventListener("DOMContentLoaded", function() {
    const themeSwitcher = document.getElementById('theme-switcher');
    const htmlElement = document.documentElement;
    const themeIcon = document.getElementById('theme-icon'); // Иконка для темы

    // Load stored theme from localStorage or set default theme
    const storedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', storedTheme);

    // Функция для установки цветов кнопки и иконок
    function setButtonColors(theme) {
        if (theme === 'light') {
            htmlElement.style.setProperty('--button-bg-color', '#28a745');
            htmlElement.style.setProperty('--button-text-color', '#ffffff');
            htmlElement.style.setProperty('--button-border-color', '#28a745');
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        } else {
            htmlElement.style.setProperty('--button-bg-color', '#17a2b8');
            htmlElement.style.setProperty('--button-text-color', '#000000');
            htmlElement.style.setProperty('--button-border-color', '#17a2b8');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }

    // Установка начальных цветов кнопки и иконки
    setButtonColors(storedTheme);

    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', function() {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Установка новых цветов кнопки и иконки
            setButtonColors(newTheme);
        });
    } else {
        console.error('Theme switcher button not found.');
    }
});
