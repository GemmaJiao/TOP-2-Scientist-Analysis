```markdown
# TOP-2-Scientist-Analysis

This project provides a web-based tool to analyze and visualize scientist publication data from Elsevier's dataset (2020–2023). It includes a FastAPI backend (`ranking.py`) to process data and a frontend (HTML, CSS, JavaScript) to display visualizations. React is optional for advanced frontend development.

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.11.9**: For the FastAPI backend.
- **Node.js (v18 or higher)**: For Vite (frontend development server).
- **VSCode**: Recommended for editing and running the project.
- **Excel Data Files**: Download the four Excel files (2020–2023) from:
  - [Elsevier Dataset](https://elsevier.digitalcommonsdata.com/datasets/btchxktzyw/7)
  - Recommended naming: `Table_1_Authors_singleyr_{year}_pubs_since_1788_wopp_extracted_202408.xlsx` (e.g., `Table_1_Authors_singleyr_2020_pubs_since_1788_wopp_extracted_202408.xlsx`).

## Project Structure

```
TOP-2-Scientist-Analysis/
├── frontend/
│   ├── AnalysisPage.html
│   ├── index.html
│   ├── searchpage.html
│   ├── vite.config.js
│   └── (images, CSS, JS files)
├── ranking.py
├── Table_1_Authors_singleyr_2020_pubs_since_1788_wopp_extracted_202408.xlsx
├── Table_1_Authors_singleyr_2021_pubs_since_1788_wopp_extracted_202408.xlsx
├── Table_1_Authors_singleyr_2022_pubs_since_1788_wopp_extracted_202408.xlsx
├── Table_1_Authors_singleyr_2023_pubs_since_1788_wopp_extracted_202408.xlsx
└── README.md
```

## Setup and Running the Project

### Step 1: Run the Backend (`ranking.py`)

The backend processes Excel data and serves API endpoints using FastAPI.

#### Option 1: Using Anaconda Prompt
1. Open Anaconda Prompt.
2. Create and activate a new environment:
   ```bash
   conda create -n TOP2-Analysis python=3.11.9
   conda activate TOP2-Analysis
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pandas numpy python-dateutil openpyxl
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn ranking:app --reload
   ```
5. Verify:
   - You should see:
     ```
     INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
     ```
   - Open `http://127.0.0.1:8000/docs` in a browser to view the FastAPI Swagger UI.

#### Option 2: Using PyCharm
1. Open PyCharm and load the project (`File > Open > TOP-2-Scientist-Analysis`).
2. Configure the Python interpreter:
   - Go to `File > Settings > Project: TOP-2-Scientist-Analysis > Python Interpreter`.
   - Click the gear icon (`⚙`) > `Add...` > `New environment using` > Select `Python 3.11.9`.
3. Open a terminal in PyCharm (`View > Tool Windows > Terminal`).
4. Install dependencies:
   ```bash
   pip install fastapi uvicorn pandas numpy python-dateutil openpyxl
   ```
5. Run the server:
   ```bash
   uvicorn ranking:app --reload
   ```
6. Verify as above.

#### Data File Setup
- Place the four Excel files (2020–2023) in the project root directory.
- Ensure filenames match the expected format (e.g., `Table_1_Authors_singleyr_2020_pubs_since_1788_wopp_extracted_202408.xlsx`).
- If using different names, update `ranking.py` to reference the correct filenames.

### Step 2: Run the Frontend (Visualization)

The frontend is a pure HTML, CSS, and JavaScript project served by Vite. React is **not required** unless you want to extend the project.

#### Setup
1. Ensure Node.js is installed:
   ```bash
   node -v
   npm -v
   ```
   - Expected: `v18.x.x` or higher, `npm 9.x.x` or higher.
   - If not installed, download from [nodejs.org](https://nodejs.org/).
2. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
3. Initialize `package.json` (if not present):
   ```bash
   npm init -y
   ```
4. Install Vite and Chart.js:
   ```bash
   npm install vite chart.js
   ```
5. Verify `package.json`:
   ```json
   {
     "name": "top2-analysis-frontend",
     "version": "1.0.0",
     "scripts": {
       "dev": "vite",
       "build": "vite build",
       "preview": "vite preview"
     },
     "dependencies": {
       "chart.js": "^4.4.3",
       "vite": "^5.4.8"
     }
   }
   ```
6. Verify `vite.config.js`:
   ```javascript
   import { defineConfig } from 'vite';
   export default defineConfig({
       server: { port: 5173 },
       root: './frontend',
       build: {
           rollupOptions: {
               input: {
                   main: './frontend/index.html',
                   searchpage: './frontend/searchpage.html',
                   analysis: './frontend/AnalysisPage.html'
               }
           }
       }
   });
   ```

#### Run the Frontend
1. Start the Vite development server:
   ```bash
   npm run dev
   ```
2. Verify:
   - You should see:
     ```
     VITE v5.4.8  ready in 300 ms
     ➜  Local:   http://localhost:5173/
     ```
   - Open `http://localhost:5173/index.html` in a browser.
3. Test the application:
   - Enter a scientist's name (e.g., `Rana Munns, aus`) on the search page.
   - Verify that charts load on the analysis page (e.g., Publication Types, Citations).

### Optional: Extending with React

If you want to extend the frontend with React (not required for the base project), follow these steps:

1. Create a new React project with Vite:
   ```bash
   cd your-parent-directory
   npm create vite@latest frontend-react -- --template react
   ```
   - Select `React` and `JavaScript` when prompted.
2. Navigate to the React project:
   ```bash
   cd frontend-react
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the React development server:
   ```bash
   npm run dev
   ```
5. Verify:
   - Open `http://localhost:5173` to see the default React app.
6. Migrate existing HTML/JS logic:
   - Convert `index.html`, `searchpage.html`, and `AnalysisPage.html` to React components (`HomePage.jsx`, `SearchPage.jsx`, `AnalysisPage.jsx`).
   - Use `react-chartjs-2` for charts:
     ```bash
     npm install chart.js react-chartjs-2
     ```
   - See the [React migration guide](#react-migration) for details (to be added based on your needs).

### Troubleshooting

- **Backend Issues**:
  - **Excel files not found**: Ensure the Excel files are in the project root and match the expected names.
  - **API not running**: Check `http://127.0.0.1:8000/docs`. Verify `uvicorn` logs for errors.
  - **CORS errors**: Add CORS middleware to `ranking.py`:
    ```python
    from fastapi.middleware.cors import CORSMiddleware
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```
- **Frontend Issues**:
  - **Vite fails to start**: Run `npm install` again or clear npm cache:
    ```bash
    npm cache clean --force
    ```
  - **Charts not loading**: Check browser console (`F12 > Console`) for errors. Verify `yearData[2021]`:
    ```javascript
    console.log('2021 data:', yearData[2021]);
    ```
- **2021 Data Missing**:
  - Verify `Table_1_Authors_singleyr_2021_pubs_since_1788_wopp_extracted_202408.xlsx` contains `nc9619 (ns)`, `h19 (ns)`, etc.:
    ```bash
    head -n 1 Table_1_Authors_singleyr_2021_pubs_since_1788_wopp_extracted_202408.xlsx
    ```

### VSCode Setup

- **Recommended Extensions**:
  - **Python** (`ms-python.python`): Python support.
  - **ESLint** (`dbaeumer.vscode-eslint`): JavaScript linting.
  - **Prettier** (`esbenp.prettier-vscode`): Code formatting.
  - Install via `Extensions` (Ctrl+Shift+X).
- **Run Commands**:
  - Use the integrated terminal (`Ctrl+``) for `uvicorn` and `npm run dev`.
- **Debugging**:
  - Check backend logs in the `uvicorn` terminal.
  - Use browser DevTools (`F12`) for frontend errors.

### Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/your-repo/TOP-2-Scientist-Analysis).
```

   
   
   



  

   
