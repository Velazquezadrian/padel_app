# AI Coding Agent Instructions for Sistema de Turnos para Pádel

Welcome to the codebase for the "Sistema de Turnos para Pádel" project. This document provides essential guidance for AI coding agents to be productive in this repository. Follow these instructions to understand the architecture, workflows, and conventions specific to this project.

---

## 📂 Project Overview

This project is a complete system for managing pádel court reservations, including a licensing system. It consists of the following major components:

- **Backend (Flask)**: REST API for managing reservations, clients, and licensing logic (`app.py`).
- **Desktop Frontend (PyWebView)**: GUI for end-users to interact with the system (`app_escritorio.py`).
- **License Management**: Handles license generation, validation, and hardware binding (`licencia_manager.py`).
- **Admin Tools**: Serial key generator for administrators (`generador_seriales_gui.py`).

### Key Directories
- `templates/`: HTML templates for the desktop frontend.
- `static/`: Static assets (CSS, JS, images).
- `build/`: Output directory for compiled executables.
- `Paquetes_Finales/`: Packaged deliverables for clients.

---

## 🛠️ Developer Workflows

### Setting Up the Development Environment
1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies from `requirements.txt`.
4. Copy `config.example.json` to `config.json` and adjust settings as needed.
5. Run the desktop application:
   ```bash
   python app_escritorio.py
   ```

### Building Executables

#### Windows
- **Main Application**:
  ```bash
  pyinstaller --clean --noconfirm --name="SistemaTurnosPadel" --windowed --icon="icono_padel.ico" --add-data="templates;templates" --add-data="static;static" app_escritorio.py
  ```
- **Serial Generator**:
  ```bash
  pyinstaller --onefile --windowed --name="GeneradorSeriales" --icon="icono_padel.ico" generador_seriales_gui.py
  ```

#### macOS
- Use the provided script:
  ```bash
  ./build_mac.sh
  ```

### Testing Licensing Features
- Use `GeneradorSeriales.exe` to generate serials.
- Test activation and trial persistence using the desktop application.

---

## 📐 Project-Specific Conventions

### Data Persistence
- Reservations are stored in `reservas.json`.
- Client data and license records are stored in `registro_clientes.json`.

### Configuration
- All runtime settings (e.g., court count, operating hours) are defined in `config.json`.

### Security
- Licenses are encrypted using AES-128.
- Hardware binding ensures licenses are tied to specific machines.

### Code Style
- Follow PEP 8 for Python code.
- Use descriptive variable names and docstrings for all functions.

---

## 🔗 Integration Points

### External Dependencies
- **Flask**: Backend API.
- **PyWebView**: Desktop GUI.
- **Cryptography**: License encryption.
- **PyInstaller**: Packaging executables.

### Cross-Component Communication
- The desktop frontend communicates with the backend via REST API endpoints defined in `app.py`.
- Licensing logic is shared between `licencia_manager.py` and the desktop application.

---

## 📄 Examples

### Adding a New API Endpoint
1. Define the route in `app.py`:
   ```python
   @app.route('/api/new-feature', methods=['POST'])
   def new_feature():
       data = request.json
       # Process data
       return jsonify({"success": True})
   ```
2. Update the frontend to call the new endpoint.

### Modifying the Desktop GUI
1. Edit the corresponding HTML template in `templates/`.
2. Update JavaScript logic in `static/js/` if needed.
3. Test changes by running `python app_escritorio.py`.

---

For further details, refer to the [README.md](../README.md) or other documentation files in the repository.