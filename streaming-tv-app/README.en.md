# 📺 World TV Streaming

A modern, user-friendly online TV streaming application developed for Windows and macOS.

## ✨ Features

- 🌍 **Worldwide TV Channels** - Turkey, USA, Europe, Asia, and more
- 📱 **Modern Interface** - Easy to use, elegant design
- ⛶ **Full-Screen Mode** - Cinema-quality viewing experience
- ⭐ **Favorite Channels** - Save your favorite channels
- 🔍 **Smart Search** - Find channels quickly
- 🌐 **Country and Category Filters** - Easily find the content you want
- 🎵 **Multiple Categories** - News, Sports, Entertainment, Music, Documentary, and more
- 💾 **Local Storage** - Your favorites list is saved on your device

## 🖥️ Supported Platforms

- ✅ Windows 10/11
- ✅ macOS 10.13 (High Sierra) and later

## 📋 Requirements

- Node.js 18.x or later
- npm or yarn package manager

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd streaming-tv-app
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start the Application

```bash
npm start
```

## 📦 Building

### For Windows:

```bash
npm run build:win
```

The installer will be created in the `dist/` folder.

### For macOS:

```bash
npm run build:mac
```

The DMG file will be created in the `dist/` folder.

### For Both Platforms:

```bash
npm run build
```

## 🎮 Usage

### Basic Usage

1. **Channel Selection**: Click on the channel you want to watch from the list on the left
2. **Search**: Search for channels by typing the channel name in the search box at the top
3. **Filtering**:
   - Select your desired country from the country filter
   - Select content type from the category filter
4. **Favorites**: Click the star button at the top right while watching a channel to add it to favorites

### Keyboard Shortcuts

- **F or f**: Toggle full-screen mode
- **Space**: Play/Pause
- **ESC**: Exit full-screen

### Video Controls

- ▶️ Play/Pause button
- 🔊 Volume control
- ⛶ Full-screen mode
- ⭐ Add/remove favorites

## 📺 Channel Categories

- 📰 **News**: National and international news channels
- ⚽ **Sports**: Sports broadcasts and events
- 🎬 **Movies**: Movie channels
- 📺 **Series**: TV series channels
- 🎭 **Entertainment**: General entertainment channels
- 🎵 **Music**: Music videos and concerts
- 👶 **Kids**: Children's programs
- 📚 **Documentary**: Documentary and educational programs
- 📡 **General**: General content channels

## 🌍 Supported Countries

- 🇹🇷 Turkey
- 🇺🇸 United States
- 🇬🇧 United Kingdom
- 🇩🇪 Germany
- 🇫🇷 France
- 🇮🇹 Italy
- 🇪🇸 Spain
- 🇷🇺 Russia
- 🇨🇳 China
- 🇯🇵 Japan
- 🇰🇷 South Korea
- 🇸🇦 Saudi Arabia
- 🇦🇪 United Arab Emirates
- And more...

## 🔧 Adding Channels

To add your own channels, edit the `src/channels.json` file:

```json
{
  "id": "unique-channel-id",
  "name": "Channel Name",
  "country": "US",
  "category": "news",
  "url": "https://stream-url.com/playlist.m3u8",
  "description": "Channel description"
}
```

### Supported Stream Formats

- HLS (HTTP Live Streaming) - `.m3u8`
- MPEG-DASH
- Direct video streams

## 🛠️ Technologies

- **Electron**: Cross-platform desktop application
- **HLS.js**: HTTP Live Streaming support
- **HTML5 Video**: Modern video player
- **Node.js**: Backend runtime
- **JavaScript/ES6**: Application logic

## 📂 Project Structure

```
streaming-tv-app/
├── src/
│   ├── main.js          # Electron main process
│   ├── renderer.js      # Renderer process (application logic)
│   ├── index.html       # Main HTML file
│   ├── styles.css       # CSS styles
│   └── channels.json    # Channel database
├── assets/              # Application icons and images
├── package.json         # Project dependencies
└── README.md           # Documentation
```

## 🐛 Troubleshooting

### Video Not Playing

1. Check your internet connection
2. Try another channel
3. Restart the application

### Channel Not Found

1. Clear search filters
2. Switch to "All Channels" tab
3. Set country and category filters to "All"

### Application Won't Open

1. Make sure Node.js and npm are installed correctly
2. Reinstall dependencies: `npm install`
3. Check for error messages in the terminal

## 🤝 Contributing

We welcome your contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## ⚠️ Legal Notice

This application only supports publicly available and legally broadcast TV streams. Users must respect copyright and broadcasting rights when watching streams. Developers are not responsible for users watching illegal content.

## 📞 Support

For questions or issues:
- Use GitHub Issues
- Check the documentation
- Join community forums

## 🎉 Thanks

Thank you for using this project! Enjoy watching! 📺✨

---

**Note**: The channel list is regularly updated. Some streams may not be accessible depending on your region.
