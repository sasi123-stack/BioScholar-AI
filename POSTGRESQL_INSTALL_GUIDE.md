# PostgreSQL Manual Installation Guide

## Quick Summary

The PostgreSQL installer was downloaded but the installation needs to be completed manually.

## Installation Steps

### 1. Download PostgreSQL (if not already downloaded)

The installer should be at: `C:\Users\sasid\AppData\Local\Temp\postgresql-15-installer.exe`

If not, download from: https://www.postgresql.org/download/windows/

### 2. Run the Installer

Double-click the installer and follow these steps:

**Installation Wizard Settings:**

1. **Welcome Screen** → Click "Next"

2. **Installation Directory**
   - Use: `C:\Program Files\PostgreSQL\15`
   - Click "Next"

3. **Select Components**
   - Check all components (PostgreSQL Server, pgAdmin 4, Stack Builder, Command Line Tools)
   - Click "Next"

4. **Data Directory**
   - Use default: `C:\Program Files\PostgreSQL\15\data`
   - Click "Next"

5. **Password** ⚠️ **IMPORTANT**
   - Enter password: `password`
   - Confirm password: `password`
   - Click "Next"

6. **Port** ⚠️ **IMPORTANT**
   - Change port from `5432` to: `5433`
   - Click "Next"

7. **Advanced Options**
   - Locale: Default locale (English, United States)
   - Click "Next"

8. **Pre Installation Summary**
   - Review settings
   - Click "Next"

9. **Ready to Install**
   - Click "Next" to begin installation
   - Wait for installation to complete (2-5 minutes)

10. **Completing Setup**
    - Uncheck "Launch Stack Builder at exit" (optional)
    - Click "Finish"

### 3. Create Database and User

After installation completes, run this script:

```powershell
.\install_postgresql.ps1
```

This will:
- Detect the installed PostgreSQL
- Create the `biomedical_search` database
- Create the `user` account with password `password`
- Grant necessary privileges

### 4. Verify Installation

Test the connection:

```powershell
# Test if PostgreSQL is running
Test-NetConnection -ComputerName localhost -Port 5433

# Connect to database
psql -U user -d biomedical_search -p 5433
# Password: password
```

## Manual Database Setup (Alternative)

If the script doesn't work, you can manually create the database:

1. **Open Command Prompt or PowerShell**

2. **Connect to PostgreSQL:**
   ```powershell
   "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -p 5433
   ```
   Enter password: `password`

3. **Run these SQL commands:**
   ```sql
   CREATE USER "user" WITH PASSWORD 'password';
   CREATE DATABASE biomedical_search OWNER "user";
   GRANT ALL PRIVILEGES ON DATABASE biomedical_search TO "user";
   \q
   ```

4. **Test the connection:**
   ```powershell
   "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U user -d biomedical_search -p 5433
   ```
   Enter password: `password`

## Configuration Summary

Once installed, your PostgreSQL will have:

- **Host:** localhost
- **Port:** 5433
- **Database:** biomedical_search
- **Username:** user
- **Password:** password
- **Connection String:** `postgresql://user:password@localhost:5433/biomedical_search`

## Troubleshooting

### Port Already in Use

If port 5433 is already in use, you can:
1. Use a different port during installation (e.g., 5434)
2. Update your `.env` file to match the port you chose

### Installation Fails

- Make sure you have administrator privileges
- Disable antivirus temporarily
- Check available disk space (need at least 500MB)

### Can't Connect After Installation

Check if the service is running:
```powershell
Get-Service postgresql-x64-15
```

If stopped, start it:
```powershell
Start-Service postgresql-x64-15
```

## Next Steps

After PostgreSQL is installed and the database is created:

1. **Start all services:**
   ```powershell
   .\start_services.ps1
   ```

2. **Start your backend:**
   ```powershell
   uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start your frontend:**
   ```powershell
   cd frontend
   python -m http.server 8080
   ```

Your complete BioMed Scholar application will then be running!
