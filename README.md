# 🔍 Domain Availability Checker — Bulk RDAP Domain Check Tool

> **Kiểm tra hàng loạt domain còn trống bằng giao thức RDAP — nhanh, chính xác, miễn phí.**
>
> Bulk check domain availability using RDAP protocol — fast, accurate, and free.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## ✨ Features / Tính năng

| Feature | Description |
|---------|-------------|
| 🔎 **Bulk Domain Check** | Check hundreds of domains in seconds using multi-threading |
| 🌐 **RDAP Protocol** | Uses official RDAP endpoints — more reliable than WHOIS |
| 🎯 **Domain Generator** | Generate domain names by country, tech topic, or custom input |
| 📊 **Real-time Stats** | Live progress, speed counter, and availability summary |
| 🎨 **Modern GUI** | Clean Tkinter interface with color-coded results |
| 📋 **Export Results** | Save results to file or copy to clipboard |
| ⚡ **Multi-threaded** | Configurable thread count (default: 20 threads) |
| 🔄 **Sort & Filter** | Sort by name/status/year, filter by TLD |
| 🌍 **Multi-language** | 7 languages: Tiếng Việt, English, 日本語, 한국어, 中文, Deutsch, Français |
| 📦 **Standalone EXE** | Build as single-file Windows EXE — no Python needed |
| ✂️ **Multi-select Copy** | Drag-select + right-click copy in Available domains list |

## 🖥️ Screenshots

<!-- Add your screenshots here after taking them -->
<!-- ![Main Screen](screenshots/main.png) -->
<!-- ![Generator](screenshots/generator.png) -->

## 🌍 Supported TLDs

| TLD | RDAP Provider |
|-----|---------------|
| `.com` | Verisign |
| `.net` | Verisign |
| `.org` | Public Interest Registry |
| `.io` | NIC.IO |
| `.ai` | NIC.AI |
| `.co` | NIC.CO |
| `.us` | Neustar |
| `.vn` | VNNIC |
| `.de` | DENIC |
| `.fr` | NIC.FR |
| `.jp` | JPRS |
| `.sg` | SGNIC |
| `.in` | Registry.IN |

## 📦 Download EXE (Windows)

For regular users who don't have Python installed:

1. Go to the [Releases](../../releases) page
2. Download `DomainTool.exe`
3. Double-click to run — no installation needed!

## 🚀 Installation / Cài đặt (for developers)

### Prerequisites / Yêu cầu
- Python 3.8 or higher
- `tkinter` (included with Python on most platforms)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/domain-checker-tool.git
cd domain-checker-tool

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Build EXE from source

```bash
# Install build dependencies
pip install pyinstaller pillow

# Build single-file EXE
python build.py
# → Output: dist/DomainTool.exe
```

## 📖 Usage / Hướng dẫn sử dụng

### Tab 1: Check Domain

1. Prepare a `domains.txt` file with one domain per line (see example below)
2. Click **"Load domains.txt"** to load your domain list
3. Select/deselect domains using checkboxes or TLD filters
4. Set thread count (default: 20)
5. Click **"Check Domain"** to start checking
6. Results are color-coded:
   - 🟢 **AVAILABLE** — Domain is free to register
   - 🔴 **REGISTERED** — Domain is taken
   - 🟡 **EXPIRING** — Domain is in pending delete / redemption period
   - 🟠 **ERROR** — Could not check (timeout, connection error)

### Tab 2: Domain Generator

1. **Manual input**: Type domain names (one per line)
2. **Random by country**: Select countries to generate culturally relevant names
3. **Random by topic**: Select tech topics (AI, Fintech, SaaS, etc.)
4. **Combine**: Select both country + topic for hybrid names
5. Choose TLDs and click **"Tạo Domain"** (Generate)
6. Click **"Lưu & Chuyển sang Check"** to save and switch to checker tab

### Example `domains.txt`

```
example.com
mysite.net
techblog.io
startup.ai
webapp.co
```

## 🏗️ Project Structure

```
domain-checker-tool/
├── main.py              # Main application (GUI + logic)
├── lang.py              # Multi-language translations (7 languages)
├── icon.py              # V-letter icon generator
├── build.py             # PyInstaller build script → DomainTool.exe
├── domains.txt          # Input: list of domains to check
├── result.txt           # Output: check results (auto-generated)
├── requirements.txt     # Python dependencies
├── LICENSE              # MIT License
├── CONTRIBUTING.md      # Contribution guidelines
└── README.md            # This file
```

## ⚙️ How It Works

This tool uses the **RDAP (Registration Data Access Protocol)** to check domain availability. RDAP is the modern replacement for WHOIS, providing:

- ✅ Structured JSON responses
- ✅ Official registry data
- ✅ No rate-limiting issues (unlike WHOIS)
- ✅ More accurate status information

The checker sends HTTP requests to official RDAP endpoints for each TLD and interprets the response:
- `HTTP 200` → Domain is registered
- `HTTP 404` → Domain is available
- Status flags like `pendingDelete` → Domain is expiring

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🔗 Related / Liên quan

- [IANA RDAP Bootstrap](https://data.iana.org/rdap/dns.json) — Official RDAP endpoint registry
- [RDAP Specification (RFC 7482)](https://tools.ietf.org/html/rfc7482) — RDAP protocol specification

---

**⭐ If this tool helped you, give it a star!**

*Made with ❤️ using Python & Tkinter*
