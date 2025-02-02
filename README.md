# 3D Sky Categorion – README  

## Introduction  
Thank you for downloading **3D Sky Categorion**!  

This application is designed to **automatically organize your files** (e.g., `5887.526861f4db7fc.jpeg`, `5887.526861f4db7fc.rar`...) into the appropriate **categories**, following the structure found on [3dsky.org](https://3dsky.org).  

## Setup Instructions  

### 1. Extract Category Folders  
For your convenience, a ZIP file named **`3dsky-allFOLDERS.zip`** is included. This archive contains all the necessary category folders.  

- Extract the empty folders to a preferred location (e.g., `C:\3dsky\categories`).  
- **Remember this path**, as you will need to set it inside the program.  

### 2. Set Up the Input Folder  
Choose a separate folder where you store **unorganized files** (e.g., `C:\3dsky\images`).  

---

## ChromeDriver Requirement  

### ⚠️ Important: ChromeDriver is Required  
This program **requires ChromeDriver** to function properly.  

1. Download ChromeDriver from:  
   [https://googlechromelabs.github.io/chrome-for-testing/#stable](https://googlechromelabs.github.io/chrome-for-testing/#stable)  
2. **Use the Stable version**, then extract the ZIP file.  
3. Set the **full path** to `chromedriver.exe` inside the program.  
   - Example: `C:\chromedriver-win64\chromedriver.exe`  

**Note:** ChromeDriver requires Google Chrome to be installed in its default location for your operating system.  

---

## Configuring the Polygon Expert ID  

At the bottom of the program, you'll find an option labeled **"Change Polygon Expert ID"**.  

This setting is **crucial** because the **Polygon Expert ID changes periodically**. The program needs to be updated with the correct ID when starting.  

### How to Find the Polygon Expert ID:  
1. Go to [https://3dsky.org](https://3dsky.org).  
2. Scroll to the bottom of the page and click on **Polygon Expert**.  
3. Copy the model ID from the URL.  
   - **Example:** If the URL is:  
     `https://3dsky.org/3dmodels/show/nabor_proektorov_epson_1`  
     Then set: **`nabor_proektorov_epson_1`** as the Polygon Expert ID.  

---

## Running the Program  

Once all paths and the Polygon Expert ID are set, **click the "Start" button**.  

- The program will launch **ChromeDriver** in the background to search 3dsky.org for each file's **category and subcategory**.  
- Files will be automatically moved to their correct subcategory folders.  

### Configuration Persistence (`config.json`)  

- When you set the **categories folder**, **images folder**, and **Polygon Expert ID**, they are automatically **saved in a file named `config.json`**.  
- This ensures that your settings **are retained** even if you close and reopen the application.  
- Upon launching the program, **the saved configuration is loaded automatically**, so you don’t need to re-enter the paths every time.  

### ChromeDriver Process Management  

- While the program is running, a folder named **`chrome_profile`** will be created inside the **3D Sky Categorion** directory.  
  - This folder (around **20MB**) is used to track **ChromeDriver processes**.  
  - The folder will be **automatically deleted** when the application stops.  
- **ChromeDriver processes are terminated when you click "Stop" or close the application.**  
- This method ensures that **only ChromeDriver processes are closed**, without affecting any real Chrome browser sessions you may have open.  

---

## Handling Errors and Missing Files  

### Possible Issues:  
1. **Page Load Failures or Bugs**  
   - Sometimes, the website may fail to load or encounter issues.  
   - If this happens, the program may return `"null"` as the model ID.  
   - These files will remain in the **Images Folder** and can be reprocessed later.  

2. **Unrecognized Models**  
   - If a file's model ID **does not exist on 3dsky.org**, it will be moved to the **"unknown" category**.  

---

## Monitoring Progress  

At the bottom of the program interface, you will find:  
- **Logs** showing real-time activity.  
- **A progress bar** displaying the percentage of files successfully organized.  

---

If you encounter any issues, double-check your ChromeDriver path and Polygon Expert ID settings.  

Happy organizing! 🚀  


