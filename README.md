## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/medmdg3/VPS_Scan.git
cd VPS_Scan
```
### 2. Dependancies:
python 3.x 
easyocr
Flask
### 3.Run the tool:
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
