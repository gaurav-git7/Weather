document.addEventListener('DOMContentLoaded', function () {
    const switcher = document.getElementById('theme-switcher');
    
    switcher.addEventListener('click', function () {
        if (document.body.classList.contains('dark-mode')) {
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
        } else {
            document.body.classList.remove('light-mode');
            document.body.classList.add('dark-mode');
        }
    });
});
