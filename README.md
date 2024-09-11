## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/medmdg3/VPS_Scan.git
cd VPS_Scan
```
### 2. Requirements:
Python 3.x
### 3. Dependancies:
easyocr

Flask

### 4. Install dependancies:
```bash
pip install easyocr
pip install Flask
```
### 5.Run the tool:
```bash
python web.py
```

## Send request:
```bash
url = "https://example.com/api"
files = {'image': image_file}  # Standard image
data = {'Type': item_type} #"CIN" or "MERCHANT"
response = requests.post(url, files=files, data=data)
```
