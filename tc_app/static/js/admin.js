document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeSwitch = document.getElementById('theme-switch');
    const body = document.body;
    const darkIcon = themeSwitch.querySelector('.dark-icon');
    const lightIcon = themeSwitch.querySelector('.light-icon');
    
    // Get saved theme from localStorage
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    setTheme(isDarkMode);
    
    themeSwitch.addEventListener('click', function() {
        const isDark = body.classList.contains('dark-mode');
        setTheme(!isDark);
    });
    
    function setTheme(isDark) {
        body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('darkMode', isDark);
        
        // Toggle icons
        darkIcon.style.display = isDark ? 'none' : 'block';
        lightIcon.style.display = isDark ? 'block' : 'none';
    }
}); 