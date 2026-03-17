# FullStack Web Development on Python hw3 :?/)

## Start
```bash
pip install -r requirements.txt
python main.py
```

### via Docker

linux
```bash
docker build -t umt-hw3 .
docker run -p 3000:3000 -v ${PWD}/storage:/app/storage umt-hw3
```

Windows
```PowerShell
docker run -p 3000:3000 -v ${PWD}\storage:/app/storage umt-hw3
```
