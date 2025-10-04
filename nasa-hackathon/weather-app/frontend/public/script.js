document.addEventListener('DOMContentLoaded', () => {
    // Side Menu Toggle
    const menuIcon = document.querySelector('.menu-icon');
    const closeMenuIcon = document.querySelector('.close-menu-icon');
    const sideMenu = document.querySelector('.side-menu');

    if (menuIcon && closeMenuIcon && sideMenu) {
        const toggleMenu = () => {
            sideMenu.classList.toggle('active');
        };
        menuIcon.addEventListener('click', toggleMenu);
        closeMenuIcon.addEventListener('click', toggleMenu);
    }

    // Region Selector Dropdown
    const regionSelector = document.querySelector('.region-selector');
    const regionDropdown = document.querySelector('.region-dropdown');
    const selectedRegion = document.querySelector('.selected-region');
    const regionOptions = document.querySelectorAll('.region-dropdown a');

    if (regionSelector && regionDropdown && selectedRegion) {
        regionSelector.addEventListener('click', (event) => {
            event.stopPropagation();
            regionDropdown.style.display = regionDropdown.style.display === 'block' ? 'none' : 'block';
        });

        regionOptions.forEach(option => {
            option.addEventListener('click', () => {
                selectedRegion.textContent = option.dataset.value;
            });
        });
    }
});