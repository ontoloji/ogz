const { ipcRenderer } = require('electron');
const fs = require('fs');
const path = require('path');

// State Management
let channels = [];
let favorites = [];
let currentChannel = null;
let currentFilter = 'all';
let hls = null;

// DOM Elements
const videoPlayer = document.getElementById('videoPlayer');
const videoSource = document.getElementById('videoSource');
const channelList = document.getElementById('channelList');
const searchInput = document.getElementById('searchInput');
const countryFilter = document.getElementById('countryFilter');
const categoryFilter = document.getElementById('categoryFilter');
const loadingSpinner = document.getElementById('loadingSpinner');
const noChannel = document.getElementById('noChannel');
const videoControls = document.getElementById('videoControls');
const playPauseBtn = document.getElementById('playPauseBtn');
const volumeSlider = document.getElementById('volumeSlider');
const volumeLabel = document.getElementById('volumeLabel');
const fullscreenBtn = document.getElementById('fullscreenBtn');
const favoriteBtn = document.getElementById('favoriteBtn');
const currentChannelName = document.getElementById('currentChannelName');
const infoChannelName = document.getElementById('infoChannelName');
const infoCountry = document.getElementById('infoCountry');
const infoCategory = document.getElementById('infoCategory');
const infoDescription = document.getElementById('infoDescription');
const toggleSidebarBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');

// Initialize the app
function init() {
    loadChannels();
    loadFavorites();
    setupEventListeners();
    renderChannels();

    // Set initial volume
    videoPlayer.volume = 0.7;
}

// Load channels from JSON file
function loadChannels() {
    const channelsPath = path.join(__dirname, 'channels.json');

    try {
        const data = fs.readFileSync(channelsPath, 'utf8');
        channels = JSON.parse(data);
    } catch (error) {
        console.log('Creating default channels database...');
        channels = getDefaultChannels();
        saveChannels();
    }
}

// Save channels to file
function saveChannels() {
    const channelsPath = path.join(__dirname, 'channels.json');
    fs.writeFileSync(channelsPath, JSON.stringify(channels, null, 2));
}

// Load favorites from localStorage
function loadFavorites() {
    const stored = localStorage.getItem('favorites');
    favorites = stored ? JSON.parse(stored) : [];
}

// Save favorites to localStorage
function saveFavorites() {
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

// Setup event listeners
function setupEventListeners() {
    // Search
    searchInput.addEventListener('input', (e) => {
        renderChannels(e.target.value);
    });

    // Filters
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            renderChannels();
        });
    });

    countryFilter.addEventListener('change', () => renderChannels());
    categoryFilter.addEventListener('change', () => renderChannels());

    // Video controls
    playPauseBtn.addEventListener('click', togglePlayPause);

    volumeSlider.addEventListener('input', (e) => {
        const volume = e.target.value / 100;
        videoPlayer.volume = volume;
        volumeLabel.textContent = `${e.target.value}%`;
    });

    fullscreenBtn.addEventListener('click', toggleFullscreen);
    favoriteBtn.addEventListener('click', toggleFavorite);

    // Video events
    videoPlayer.addEventListener('play', () => {
        playPauseBtn.textContent = '⏸️';
        hideNoChannel();
    });

    videoPlayer.addEventListener('pause', () => {
        playPauseBtn.textContent = '▶️';
    });

    videoPlayer.addEventListener('loadstart', () => {
        showLoading();
    });

    videoPlayer.addEventListener('canplay', () => {
        hideLoading();
    });

    videoPlayer.addEventListener('error', (e) => {
        hideLoading();
        console.error('Video error:', e);
        alert('Bu kanal şu anda oynatılamıyor. Lütfen başka bir kanal deneyin.');
    });

    // Sidebar toggle
    toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.toggle('hidden');
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'f' || e.key === 'F') {
            toggleFullscreen();
        } else if (e.key === ' ') {
            e.preventDefault();
            togglePlayPause();
        } else if (e.key === 'Escape') {
            ipcRenderer.send('exit-fullscreen');
        }
    });
}

// Render channels list
function renderChannels(searchTerm = '') {
    const country = countryFilter.value;
    const category = categoryFilter.value;

    let filteredChannels = channels.filter(channel => {
        // Filter by search term
        if (searchTerm && !channel.name.toLowerCase().includes(searchTerm.toLowerCase())) {
            return false;
        }

        // Filter by favorites
        if (currentFilter === 'favorites' && !favorites.includes(channel.id)) {
            return false;
        }

        // Filter by country
        if (country !== 'all' && channel.country !== country) {
            return false;
        }

        // Filter by category
        if (category !== 'all' && channel.category !== category) {
            return false;
        }

        return true;
    });

    channelList.innerHTML = '';

    if (filteredChannels.length === 0) {
        channelList.innerHTML = '<div style="padding: 20px; text-align: center; color: #888;">Kanal bulunamadı</div>';
        return;
    }

    filteredChannels.forEach(channel => {
        const channelItem = document.createElement('div');
        channelItem.className = 'channel-item';
        if (favorites.includes(channel.id)) {
            channelItem.classList.add('favorite');
        }
        if (currentChannel && currentChannel.id === channel.id) {
            channelItem.classList.add('active');
        }

        channelItem.innerHTML = `
            <div>
                <div class="channel-name">${channel.name}</div>
                <div class="channel-meta">${getCountryFlag(channel.country)} ${channel.country} • ${channel.category}</div>
            </div>
        `;

        channelItem.addEventListener('click', () => playChannel(channel));
        channelList.appendChild(channelItem);
    });
}

// Play channel
function playChannel(channel) {
    currentChannel = channel;

    // Destroy existing HLS instance
    if (hls) {
        hls.destroy();
        hls = null;
    }

    // Update UI
    currentChannelName.textContent = channel.name;
    infoChannelName.textContent = channel.name;
    infoCountry.textContent = `${getCountryFlag(channel.country)} ${channel.country}`;
    infoCategory.textContent = channel.category;
    infoDescription.textContent = channel.description || 'Kanal açıklaması bulunmuyor.';

    updateFavoriteButton();
    renderChannels();

    showLoading();

    // Check if HLS is supported
    if (Hls.isSupported() && channel.url.includes('.m3u8')) {
        hls = new Hls({
            enableWorker: true,
            lowLatencyMode: true,
            backBufferLength: 90
        });

        hls.loadSource(channel.url);
        hls.attachMedia(videoPlayer);

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
            videoPlayer.play().catch(e => {
                console.error('Autoplay prevented:', e);
                hideLoading();
            });
        });

        hls.on(Hls.Events.ERROR, (event, data) => {
            console.error('HLS error:', data);
            if (data.fatal) {
                hideLoading();
                alert('Bu kanal yüklenemedi. Lütfen başka bir kanal deneyin.');
            }
        });
    } else if (videoPlayer.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        videoSource.src = channel.url;
        videoPlayer.load();
        videoPlayer.play().catch(e => {
            console.error('Autoplay prevented:', e);
            hideLoading();
        });
    } else {
        // Direct streaming
        videoSource.src = channel.url;
        videoPlayer.load();
        videoPlayer.play().catch(e => {
            console.error('Autoplay prevented:', e);
            hideLoading();
        });
    }
}

// Toggle play/pause
function togglePlayPause() {
    if (videoPlayer.paused) {
        videoPlayer.play();
    } else {
        videoPlayer.pause();
    }
}

// Toggle fullscreen
function toggleFullscreen() {
    ipcRenderer.send('toggle-fullscreen');
}

// Toggle favorite
function toggleFavorite() {
    if (!currentChannel) return;

    const index = favorites.indexOf(currentChannel.id);
    if (index > -1) {
        favorites.splice(index, 1);
    } else {
        favorites.push(currentChannel.id);
    }

    saveFavorites();
    updateFavoriteButton();
    renderChannels();
}

// Update favorite button
function updateFavoriteButton() {
    if (!currentChannel) return;

    if (favorites.includes(currentChannel.id)) {
        favoriteBtn.classList.add('active');
        favoriteBtn.title = 'Favorilerden Çıkar';
    } else {
        favoriteBtn.classList.remove('active');
        favoriteBtn.title = 'Favorilere Ekle';
    }
}

// Show/hide loading
function showLoading() {
    loadingSpinner.classList.add('active');
}

function hideLoading() {
    loadingSpinner.classList.remove('active');
}

function hideNoChannel() {
    noChannel.style.display = 'none';
}

// Get country flag emoji
function getCountryFlag(countryCode) {
    const flags = {
        'TR': '🇹🇷', 'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷',
        'IT': '🇮🇹', 'ES': '🇪🇸', 'RU': '🇷🇺', 'CN': '🇨🇳', 'JP': '🇯🇵',
        'KR': '🇰🇷', 'SA': '🇸🇦', 'AE': '🇦🇪', 'BR': '🇧🇷', 'IN': '🇮🇳',
        'MX': '🇲🇽', 'CA': '🇨🇦', 'AU': '🇦🇺', 'NL': '🇳🇱', 'SE': '🇸🇪'
    };
    return flags[countryCode] || '🌐';
}

// Get default channels (sample data)
function getDefaultChannels() {
    return [
        // Turkish Channels
        {
            id: 'trt1',
            name: 'TRT 1',
            country: 'TR',
            category: 'general',
            url: 'https://tv-trt1.medya.trt.com.tr/master.m3u8',
            description: 'TRT 1 - Türkiye Radyo Televizyon Kurumu ana kanalı'
        },
        {
            id: 'trt-haber',
            name: 'TRT Haber',
            country: 'TR',
            category: 'news',
            url: 'https://tv-trthaber.medya.trt.com.tr/master.m3u8',
            description: 'TRT Haber - 7/24 haber yayını'
        },
        {
            id: 'trt-spor',
            name: 'TRT Spor',
            country: 'TR',
            category: 'sports',
            url: 'https://tv-trtspor1.medya.trt.com.tr/master.m3u8',
            description: 'TRT Spor - Spor yayınları'
        },
        {
            id: 'trt-cocuk',
            name: 'TRT Çocuk',
            country: 'TR',
            category: 'kids',
            url: 'https://tv-trtcocuk.medya.trt.com.tr/master.m3u8',
            description: 'TRT Çocuk - Çocuk programları'
        },
        {
            id: 'trt-belgesel',
            name: 'TRT Belgesel',
            country: 'TR',
            category: 'documentary',
            url: 'https://tv-trtbelgesel.medya.trt.com.tr/master.m3u8',
            description: 'TRT Belgesel - Belgesel yayınları'
        },
        {
            id: 'trt-muzik',
            name: 'TRT Müzik',
            country: 'TR',
            category: 'music',
            url: 'https://tv-trtmuzik.medya.trt.com.tr/master.m3u8',
            description: 'TRT Müzik - Müzik yayınları'
        },
        {
            id: 'trt-world',
            name: 'TRT World',
            country: 'TR',
            category: 'news',
            url: 'https://tv-trtworld.medya.trt.com.tr/master.m3u8',
            description: 'TRT World - İngilizce haber kanalı'
        },
        {
            id: 'tbmm-tv',
            name: 'TBMM TV',
            country: 'TR',
            category: 'general',
            url: 'https://meclistv-live.ercdn.net/meclistv/meclistv.m3u8',
            description: 'TBMM TV - Türkiye Büyük Millet Meclisi TV'
        },

        // International News Channels
        {
            id: 'bbc-news',
            name: 'BBC News',
            country: 'GB',
            category: 'news',
            url: 'https://vs-cmaf-pushb-uk-live.akamaized.net/x=4/i=urn:bbc:pips:service:bbc_news_channel_hd/pc_hd_abr_v2.mpd',
            description: 'BBC News - Dünya haberleri'
        },
        {
            id: 'al-jazeera',
            name: 'Al Jazeera English',
            country: 'AE',
            category: 'news',
            url: 'https://live-hls-web-aje.getaj.net/AJE/index.m3u8',
            description: 'Al Jazeera English - Uluslararası haber kanalı'
        },
        {
            id: 'france24-en',
            name: 'France 24 English',
            country: 'FR',
            category: 'news',
            url: 'https://cdn.klowdtv.net/803B48A/n1.klowdtv.net/live1/france24_720p/playlist.m3u8',
            description: 'France 24 - Fransız haber kanalı'
        },
        {
            id: 'euronews',
            name: 'Euronews',
            country: 'FR',
            category: 'news',
            url: 'https://euronews-euronews-world-1-eu.rakuten.wstar.live/linear/1011000/playlist.m3u8',
            description: 'Euronews - Avrupa haberleri'
        },

        // Entertainment
        {
            id: 'nasa-tv',
            name: 'NASA TV',
            country: 'US',
            category: 'documentary',
            url: 'https://ntv1.akamaized.net/hls/live/2014075/NASA-NTV1-HLS/master.m3u8',
            description: 'NASA TV - Uzay ve bilim yayınları'
        },
        {
            id: 'red-bull-tv',
            name: 'Red Bull TV',
            country: 'US',
            category: 'sports',
            url: 'https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8',
            description: 'Red Bull TV - Ekstrem sporlar'
        },

        // Music Channels
        {
            id: 'powertv',
            name: 'PowerTV',
            country: 'TR',
            category: 'music',
            url: 'https://livetv.powerapp.com.tr/powerTV/powerhd.smil/playlist.m3u8',
            description: 'PowerTV - Türkçe müzik kanalı'
        }
    ];
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
