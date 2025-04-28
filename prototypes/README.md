# 🎛️ wdf-sallenkey

This project implements a VST plugin that virtualizes active Sallen-Key filters using Wave Digital Filters (WDF) techniques.

---

## 🚀 Setup Instructions on Windows

This guide summarizes the steps and commands used to set up the project environment on Windows.

### 1. Clone the repository (with submodules)

```powershell
git clone --recurse-submodules https://github.com/fergarciadlc/wdf-sallenkey.git
cd wdf-sallenkey
```

---

### 2. Set Execution Policy (only once)

If activating the virtual environment fails with a security error, allow script execution for your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 3. Create and activate a Python virtual environment

Create a virtual environment:

```powershell
python -m venv venv
```

Before activating, set the environment variable to ensure UTF-8 encoding:

```powershell
$env:PYTHONUTF8=1
```

Then activate the virtual environment:

```powershell
.\venv\Scripts\Activate
```

---

### 4. Install Python dependencies

Install required Python packages from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

If you need to work directly with `pywdf`, clone and install it manually:

```powershell
git clone https://github.com/gusanthon/pywdf.git
cd pywdf
pip install -e .
```

