```markdown
# 🏗️ Construction Quick Estimator

<div dir="rtl">

یک ابزار تخمین سریع مصالح، هزینه و زمان ساخت ساختمان با دو نسخه **وب (Streamlit)** و **دسکتاپ (Tkinter)**.

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📐 **Area Calculation** | Calculate total built area from land area and floors |
| 🧱 **Materials Estimation** | Estimate concrete, steel, and formwork quantities |
| 💰 **Cost Estimation** | Calculate total cost based on current material prices |
| ⏱️ **Duration Estimation** | Estimate project duration based on size and structure type |
| 📊 **Excel Export** | Export full report to Excel file |
| 📄 **PDF Export** | Export summary report to PDF |
| 🖥️ **Desktop Version** | Native Windows application with Tkinter |
| 🌐 **Web Version** | Online version with Streamlit |

---

## 🛠️ Tech Stack

```text
🐍 Python 3.10+
🖥️ Tkinter (Desktop)
🌐 Streamlit (Web)
📊 Pandas, OpenPyXL
📄 ReportLab (PDF)
```

---

## 📋 Supported Structure Types

| Structure | Description |
|-----------|-------------|
| **Concrete** | Reinforced concrete - suitable for medium and high-rise buildings |
| **Steel** | Steel frame - suitable for warehouses and high-rise buildings |
| **Composite** | Combined concrete-steel - optimized for large spans |

---

## 📋 Supported Roof Types

| Roof Type | Description |
|-----------|-------------|
| **Tircheh Block** | Most common roof in Iran |
| **Waffle** | Lightweight and integrated - suitable for large spans |
| **Concrete Slab** | Heavy and resistant - suitable for earthquake zones |
| **Composite** | Steel deck roof - high execution speed |

---

## 📋 Supported Building Types

| Building Type | Description |
|---------------|-------------|
| **Residential** | Apartment buildings and houses |
| **Commercial** | Shopping centers and stores |
| **Office** | Administrative buildings |
| **Industrial** | Factories and warehouses |

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/construction-estimator.git
cd construction-estimator
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📱 Usage

### Desktop Version (Tkinter)

```bash
python estimator_TKinter.py
```

### Web Version (Streamlit)

```bash
streamlit run estimator_streamlit.py
```

### Build Executable (exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "ConstructionEstimator" estimator_TKinter.py
```

---

## 📊 Sample Output

```text
============================================================
🏗️ CONSTRUCTION ESTIMATOR REPORT
============================================================

📐 PROJECT INFORMATION
--------------------------------------------------
Area: 180 m²
Floors: 5
Total Area: 900 m²
Structure: Concrete
Roof: Tircheh Block
Building Type: Residential

🧱 MATERIALS
--------------------------------------------------
Concrete: 405.00 m³
Steel: 40,500 kg (40.50 ton)
Formwork: 1,080 m²

💰 COST ESTIMATION
--------------------------------------------------
Concrete: 1,012,500,000 Toman
Steel: 1,701,000,000 Toman
Formwork: 378,000,000 Toman
Labor: 375,000,000 Toman
--------------------------------------------------
TOTAL: 3,466,500,000 Toman

⏱️ DURATION
--------------------------------------------------
Total Days: 175 days (~5.8 months)
```

---

## 📁 Project Structure

```text
construction-estimator/
│
├── estimator_TKinter.py          # Desktop version (Tkinter)
├── estimator_streamlit.py        # Web version (Streamlit)
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation
├── .gitignore                    # Git ignore file
│
├── data/
│   ├── structures.json           # Structure coefficients
│   └── roofs.json                # Roof coefficients
│
└── dist/
    └── ConstructionEstimator.exe # Standalone executable
```

---

## 🔧 Customization

You can modify the coefficients in the code or JSON files:

```python
COEFFICIENTS = {
    "Concrete": {
        "concrete_avg": 0.42,
        "concrete_min": 0.35,
        "concrete_max": 0.50,
        "steel_avg": 45,
        "steel_min": 38,
        "steel_max": 55,
        "formwork": 1.2,
        "structure_days": 75,
        "cost_factor": 1.0
    }
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@your_username](https://github.com/your_username)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- [Python](https://www.python.org/) - Programming language
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
- [Streamlit](https://streamlit.io/) - Web app framework
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel file handling

---

## ⭐ Show your support

If this project helped you, please give it a ⭐ on GitHub!

---

**Made with ❤️ for civil engineers and contractors**
```
