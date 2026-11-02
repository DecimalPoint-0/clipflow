# Contributing to ClipFlow

Thank you for your interest in contributing! ClipFlow is built to be simple, fast, and completely offline.

---

## 🛠️ Local Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/<your-username>/clipflow.git
   cd clipflow
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   python run.py
   ```

5. Run unit tests before submitting changes:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

---

## 💡 Submitting Changes

1. Create a feature branch: `git checkout -b feature/my-new-feature`
2. Commit your changes: `git commit -am 'Add some feature'`
3. Push to the branch: `git push origin feature/my-new-feature`
4. Open a Pull Request!

