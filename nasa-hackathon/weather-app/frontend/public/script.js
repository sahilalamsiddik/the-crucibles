document.addEventListener('DOMContentLoaded', () => {
    // --- Expanded Mock Weather Data ---
    const mockWeatherData = {
        'kolkata': { name: 'Kolkata', state: 'West Bengal', tempC: 28, icon: 'cloud-rain', date: 'Saturday, 4 October 2025', conditions: { wind: '15 km/h E', humidity: '88%', rain: '60%', heatIndexC: 32, uv: 'Low', cloudCover: '75%' }, atmosphere: { solar: '450 W/m²', surfaceTempC: 29, pressure: '1008 hPa', oxygen: '20.9%' }, precipitation: [20, 30, 50, 80, 90, 70, 60, 40, 25] },
        'delhi': { name: 'Delhi', state: 'Delhi', tempC: 34, icon: 'sun', date: 'Saturday, 4 October 2025', conditions: { wind: '10 km/h W', humidity: '40%', rain: '5%', heatIndexC: 36, uv: 'Very High', cloudCover: '10%' }, atmosphere: { solar: '950 W/m²', surfaceTempC: 35, pressure: '1015 hPa', oxygen: '20.8%' }, precipitation: [0, 0, 5, 10, 5, 0, 0, 0, 0] },
        'mumbai': { name: 'Mumbai', state: 'Maharashtra', tempC: 30, icon: 'cloud', date: 'Saturday, 4 October 2025', conditions: { wind: '20 km/h SW', humidity: '82%', rain: '40%', heatIndexC: 34, uv: 'Moderate', cloudCover: '60%' }, atmosphere: { solar: '600 W/m²', surfaceTempC: 31, pressure: '1010 hPa', oxygen: '20.9%' }, precipitation: [10, 15, 20, 40, 50, 45, 30, 20, 10] },
        'chennai': { name: 'Chennai', state: 'Tamil Nadu', tempC: 31, icon: 'cloud-lightning', date: 'Saturday, 4 October 2025', conditions: { wind: '18 km/h SE', humidity: '79%', rain: '55%', heatIndexC: 35, uv: 'High', cloudCover: '70%' }, atmosphere: { solar: '700 W/m²', surfaceTempC: 33, pressure: '1009 hPa', oxygen: '20.9%' }, precipitation: [25, 30, 40, 60, 75, 70, 50, 35, 20] },
        'bengaluru': { name: 'Bengaluru', state: 'Karnataka', tempC: 27, icon: 'wind', date: 'Saturday, 4 October 2025', conditions: { wind: '25 km/h W', humidity: '75%', rain: '30%', heatIndexC: 30, uv: 'High', cloudCover: '40%' }, atmosphere: { solar: '800 W/m²', surfaceTempC: 28, pressure: '1012 hPa', oxygen: '21.0%' }, precipitation: [5, 10, 15, 25, 30, 20, 15, 10, 5] },
        'pune': { name: 'Pune', state: 'Maharashtra', tempC: 29, icon: 'cloud-drizzle', date: 'Saturday, 4 October 2025', conditions: { wind: '12 km/h W', humidity: '80%', rain: '45%', heatIndexC: 32, uv: 'Moderate', cloudCover: '55%' }, atmosphere: { solar: '650 W/m²', surfaceTempC: 30, pressure: '1011 hPa', oxygen: '20.9%' }, precipitation: [15, 20, 30, 50, 60, 55, 40, 25, 15] },
        'ahmedabad': { name: 'Ahmedabad', state: 'Gujarat', tempC: 36, icon: 'sun', date: 'Saturday, 4 October 2025', conditions: { wind: '14 km/h NW', humidity: '35%', rain: '2%', heatIndexC: 38, uv: 'Extreme', cloudCover: '5%' }, atmosphere: { solar: '1050 W/m²', surfaceTempC: 37, pressure: '1014 hPa', oxygen: '20.7%' }, precipitation: [0, 0, 0, 2, 5, 2, 0, 0, 0] },
        'kochi': { name: 'Kochi', state: 'Kerala', tempC: 29, icon: 'cloud-rain', date: 'Saturday, 4 October 2025', conditions: { wind: '22 km/h SW', humidity: '85%', rain: '65%', heatIndexC: 33, uv: 'Moderate', cloudCover: '80%' }, atmosphere: { solar: '550 W/m²', surfaceTempC: 30, pressure: '1007 hPa', oxygen: '20.9%' }, precipitation: [30, 40, 55, 70, 85, 80, 60, 45, 30] },
        'jaipur': { name: 'Jaipur', state: 'Rajasthan', tempC: 35, icon: 'sun', date: 'Saturday, 4 October 2025', conditions: { wind: '8 km/h W', humidity: '30%', rain: '0%', heatIndexC: 37, uv: 'Extreme', cloudCover: '2%' }, atmosphere: { solar: '1100 W/m²', surfaceTempC: 36, pressure: '1016 hPa', oxygen: '20.7%' }, precipitation: [0, 0, 0, 0, 0, 0, 0, 0, 0] },
        'gurugram': { name: 'Gurugram', state: 'Haryana', tempC: 33, icon: 'haze', date: 'Saturday, 4 October 2025', conditions: { wind: '9 km/h W', humidity: '45%', rain: '10%', heatIndexC: 35, uv: 'Very High', cloudCover: '15%' }, atmosphere: { solar: '900 W/m²', surfaceTempC: 34, pressure: '1015 hPa', oxygen: '20.8%' }, precipitation: [0, 5, 5, 10, 15, 10, 5, 5, 0] },
        'varanasi': { name: 'Varanasi', state: 'Uttar Pradesh', tempC: 32, icon: 'cloud-sun', date: 'Saturday, 4 October 2025', conditions: { wind: '7 km/h E', humidity: '60%', rain: '15%', heatIndexC: 34, uv: 'High', cloudCover: '30%' }, atmosphere: { solar: '850 W/m²', surfaceTempC: 33, pressure: '1013 hPa', oxygen: '20.8%' }, precipitation: [5, 10, 15, 20, 25, 20, 15, 10, 5] },
        'patna': { name: 'Patna', state: 'Bihar', tempC: 31, icon: 'cloud-drizzle', date: 'Saturday, 4 October 2025', conditions: { wind: '11 km/h E', humidity: '70%', rain: '35%', heatIndexC: 33, uv: 'High', cloudCover: '50%' }, atmosphere: { solar: '750 W/m²', surfaceTempC: 32, pressure: '1010 hPa', oxygen: '20.9%' }, precipitation: [10, 15, 25, 40, 50, 45, 30, 20, 10] },
        'amritsar': { name: 'Amritsar', state: 'Punjab', tempC: 33, icon: 'sun', date: 'Saturday, 4 October 2025', conditions: { wind: '13 km/h NW', humidity: '42%', rain: '5%', heatIndexC: 35, uv: 'Very High', cloudCover: '12%' }, atmosphere: { solar: '980 W/m²', surfaceTempC: 34, pressure: '1014 hPa', oxygen: '20.8%' }, precipitation: [0, 0, 0, 5, 10, 5, 0, 0, 0] },
        'srinagar': { name: 'Srinagar', state: 'Jammu and Kashmir', tempC: 22, icon: 'wind', date: 'Saturday, 4 October 2025', conditions: { wind: '15 km/h N', humidity: '55%', rain: '20%', heatIndexC: 23, uv: 'Moderate', cloudCover: '35%' }, atmosphere: { solar: '700 W/m²', surfaceTempC: 24, pressure: '1018 hPa', oxygen: '21.1%' }, precipitation: [5, 10, 15, 20, 30, 25, 15, 10, 5] }
    };

    // --- Element Selectors ---
    const headerSearchInput = document.querySelector('.header-search-bar input');
    let favouriteItems = document.querySelectorAll('.favourite-item:not(.add-favourite)');
    const cityNameEl = document.querySelector('.location-info h1');
    const dateEl = document.querySelector('.location-info p');
    const mainTempEl = document.querySelector('.temp-display .temp-value');
    const mainIconEl = document.querySelector('.main-weather-icon');
    const tempUnitToggle = document.getElementById('temp-unit-toggle');
    const themeToggle = document.getElementById('theme-toggle');
    const menuIcon = document.querySelector('.menu-icon');
    const closeMenuIcon = document.querySelector('.close-menu-icon');
    const sideMenu = document.querySelector('.side-menu');
    const chartBarContainer = document.querySelector('.chart-bar-container');
    const favouritesBar = document.querySelector('.favourites-bar');
    const addFavouriteBtn = document.getElementById('add-favourite-btn');

    // Detail selectors
    const windSpeedEl = document.getElementById('wind-speed');
    const humidityEl = document.getElementById('humidity');
    const rainPredictionEl = document.getElementById('rain-prediction');
    const heatIndexEl = document.getElementById('heat-index');
    const uvIndexEl = document.getElementById('uv-index');
    const cloudCoverEl = document.getElementById('cloud-cover');
    const solarRadiationEl = document.getElementById('solar-radiation');
    const surfaceTempEl = document.getElementById('surface-temp');
    const surfacePressureEl = document.getElementById('surface-pressure');
    const oxygenLevelsEl = document.getElementById('oxygen-levels');


    if (menuIcon && closeMenuIcon && sideMenu) {
        const toggleMenu = () => {
            sideMenu.classList.toggle('active');
        };
        menuIcon.addEventListener('click', toggleMenu);
        closeMenuIcon.addEventListener('click', toggleMenu);
    }

    // --- Theme Toggle ---
    if (themeToggle) {
        // Function to apply theme
        const applyTheme = (theme) => {
            if (theme === 'dark') {
                document.body.dataset.theme = 'dark';
                themeToggle.checked = true;
            } else {
                document.body.dataset.theme = 'light';
                themeToggle.checked = false;
            }
            feather.replace(); // Re-render icons to pick up new colors
        };

        // Check for saved theme in localStorage
        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);

        themeToggle.addEventListener('change', () => {
            const newTheme = themeToggle.checked ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }

    // --- Temperature Unit Toggle ---
    if (tempUnitToggle) {
        tempUnitToggle.addEventListener('change', () => {
            const isFahrenheit = tempUnitToggle.checked;
            const tempElements = document.querySelectorAll('.temp-value');

            tempElements.forEach(el => {
                const tempC = parseFloat(el.dataset.tempC);
                if (!isNaN(tempC)) {
                    if (isFahrenheit) {
                        // Convert to Fahrenheit
                        const tempF = Math.round((tempC * 9/5) + 32);
                        el.textContent = `${tempF}°F`;
                    } else {
                        // Convert back to Celsius
                        el.textContent = `${tempC}°C`;
                    }
                }
            });
        });
    }

    // --- Weather Update Function ---
    function updateWeatherDisplay(cityData) {
        if (!cityData) return; // Do nothing if no data

        // Update main card
        cityNameEl.textContent = `${cityData.name}, ${cityData.state}`;
        dateEl.textContent = cityData.date;
        mainTempEl.dataset.tempC = cityData.tempC;

        // Check current C/F toggle state and display correctly
        const isFahrenheit = tempUnitToggle.checked;
        if (isFahrenheit) {
            const tempF = Math.round((cityData.tempC * 9/5) + 32);
            mainTempEl.textContent = `${tempF}°F`;
        } else {
            mainTempEl.textContent = `${cityData.tempC}°C`;
        }

        // Update Current Conditions
        windSpeedEl.textContent = cityData.conditions.wind;
        humidityEl.textContent = cityData.conditions.humidity;
        rainPredictionEl.textContent = cityData.conditions.rain;
        heatIndexEl.dataset.tempC = cityData.conditions.heatIndexC;
        uvIndexEl.textContent = cityData.conditions.uv;
        cloudCoverEl.textContent = cityData.conditions.cloudCover;

        // Update Atmospheric Details
        solarRadiationEl.textContent = cityData.atmosphere.solar;
        surfaceTempEl.dataset.tempC = cityData.atmosphere.surfaceTempC;
        surfacePressureEl.textContent = cityData.atmosphere.pressure;
        oxygenLevelsEl.textContent = cityData.atmosphere.oxygen;

        // Update Hourly Precipitation Chart
        if (cityData.precipitation && chartBarContainer) {
            const chartBars = chartBarContainer.querySelectorAll('.chart-bar');
            chartBars.forEach((bar, index) => {
                if (cityData.precipitation[index] !== undefined) {
                    bar.style.height = `${cityData.precipitation[index]}%`;
                }
            });
        }

        // Update main icon after all data is set
        mainIconEl.setAttribute('data-feather', cityData.icon);

        tempUnitToggle.dispatchEvent(new Event('change')); // Trigger temp conversion for all new values
        feather.replace(); // Re-render all icons
    }

    // --- Favourites Click Functionality ---
    function addFavouriteClickListener(item) {
        item.addEventListener('click', () => {
            const cityName = item.querySelector('p').textContent.toLowerCase();
            updateWeatherDisplay(mockWeatherData[cityName]);
        });
    }
    favouriteItems.forEach(addFavouriteClickListener);

    // --- Add Favourite Button Functionality ---
    if (addFavouriteBtn && favouritesBar) {
        const dropdown = document.createElement('div');
        dropdown.className = 'add-favourite-dropdown';
        addFavouriteBtn.appendChild(dropdown);

        const populateDropdown = () => {
            dropdown.innerHTML = ''; // Clear existing options
            const existingFavourites = Array.from(favouritesBar.querySelectorAll('.favourite-item:not(.add-favourite)'))
                                            .map(item => item.querySelector('p').textContent.toLowerCase());
            
            const availableCities = Object.keys(mockWeatherData)
                                          .filter(cityKey => !existingFavourites.includes(cityKey));

            availableCities.forEach(cityKey => {
                const cityData = mockWeatherData[cityKey];
                const option = document.createElement('a');
                option.textContent = cityData.name;
                option.dataset.cityKey = cityKey;
                option.addEventListener('click', (e) => {
                    e.stopPropagation(); // Prevent button click from firing
                    addCityToFavourites(cityKey);
                    dropdown.style.display = 'none';
                });
                dropdown.appendChild(option);
            });
        };

        const addCityToFavourites = (cityKey) => {
            const cityData = mockWeatherData[cityKey];
            const newFavItem = document.createElement('div');
            newFavItem.className = 'favourite-item';
            newFavItem.innerHTML = `
                <p>${cityData.name}</p>
                <i data-feather="${cityData.icon}" class="weather-icon"></i>
                <span class="temp-value" data-temp-c="${cityData.tempC}">${cityData.tempC}°C</span>
            `;
            favouritesBar.insertBefore(newFavItem, addFavouriteBtn);
            feather.replace();
            addFavouriteClickListener(newFavItem); // Add click listener to new item
            tempUnitToggle.dispatchEvent(new Event('change')); // Update temp format if needed
        };

        addFavouriteBtn.addEventListener('click', () => {
            populateDropdown();
            const isVisible = dropdown.style.display === 'block';
            dropdown.style.display = isVisible ? 'none' : 'block';
        });

        // Hide dropdown if clicking outside
        document.addEventListener('click', (e) => {
            if (!addFavouriteBtn.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    // --- Header Search Bar Functionality ---
    if (headerSearchInput) {
        headerSearchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && headerSearchInput.value) {
                const query = headerSearchInput.value.toLowerCase().trim();
                if (mockWeatherData[query]) {
                    const cityData = mockWeatherData[query];
                    updateWeatherDisplay(cityData);
                } else {
                    alert("I can currently fetch weather for the listed cities. Please try one of those (e.g., 'pune', 'jaipur').");
                }
                headerSearchInput.value = ''; // Clear search bar after handling the query
            }
        });
    }
});