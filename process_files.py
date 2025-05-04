import os
import shutil
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver(chromedriver_path):
    chrome_options = Options()
    # headless con disable-gpu per Windows
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # forziamo layout desktop
    chrome_options.add_argument("--window-size=1920,1080")
    # user-agent reale
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.7103.49 Safari/537.36"
    )
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)


def wait_for_page_load(driver, timeout=20):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def log_message(message, log_signal=None):
    if log_signal:
        log_signal.emit(message)
    else:
        print(message)


def get_model_id(driver, base_name, log_signal=None):
    url = f"https://3dsky.org/3dmodels?query={base_name}&order=relevance"
    driver.get(url)
    wait_for_page_load(driver)
    time.sleep(1)
    try:
        first = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//a[contains(@href, "/3dmodels/show/")]')
            )
        )
        href = first.get_attribute("href")
        model_id = href.split("/")[-1]
        log_message(f"→ [search] {base_name} → model_id: {model_id}", log_signal)
        return model_id
    except Exception as e:
        log_message(f"[ERROR] get_model_id({base_name}): {e}", log_signal)
        return None


def get_category_subcategory(driver, model_id, log_signal=None):
    if not model_id:
        return None, None
    driver.get(f"https://3dsky.org/3dmodels/show/{model_id}")
    wait_for_page_load(driver)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    try:
        crumbs = WebDriverWait(driver, 15).until(
            EC.visibility_of_all_elements_located(
                (By.XPATH, '//a[@itemprop="item"]/span[@itemprop="name"]')
            )
        )
        category = crumbs[0].text.strip()
        subcategory = crumbs[1].text.strip() if len(crumbs) > 1 else "Unknown"
        log_message(f"→ [page] {model_id} → Categoria: {category}, Sotto: {subcategory}", log_signal)
        return category, subcategory
    except Exception as e:
        with open(f"debug_{model_id}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        log_message(f"[ERROR] get_category_subcategory({model_id}): {e}", log_signal)
        return None, None


def process_files(chromedriver_path, categories_folder, image_folder, polygon_id,
                  log_signal=None, progress_signal=None):
    """
    Esegue lo spostamento dei file in "image_folder" verso le
    sottocartelle di "categories_folder" in base a categorie e sottocategorie
    recuperate da 3dsky.org.
    Il parametro "polygon_id" identifica i modelli da trattare come 'unknown'.
    """
    # Driver
    driver = setup_driver(chromedriver_path)
    # Cartella per unknown
    unknown_folder = os.path.join(categories_folder, "unknown")
    os.makedirs(unknown_folder, exist_ok=True)
    # Lista di tutti i file supportati
    supported = ['.jpg', '.jpeg', '.png', '.zip', '.rar', '.7z']
    files = [f for f in os.listdir(image_folder) if os.path.splitext(f)[1].lower() in supported]
    total = len(files)
    if total == 0:
        log_message("Nessun file da processare.", log_signal)
        driver.quit()
        return
    # Raggruppa per base_name
    base_map = {}
    for f in files:
        base = os.path.splitext(f)[0]
        base_map.setdefault(base, []).append(f)
    done = 0
    # Inizio processamento
    log_message(f"Starting processing of {total} files...", log_signal)
    try:
        for base, matches in base_map.items():
            model_id = get_model_id(driver, base, log_signal)
            if not model_id or model_id == polygon_id:
                target = unknown_folder
            else:
                cat, sub = get_category_subcategory(driver, model_id, log_signal)
                if not cat or not sub:
                    target = unknown_folder
                else:
                    target = os.path.join(categories_folder, cat, sub)
                    os.makedirs(target, exist_ok=True)
            for m in matches:
                src = os.path.join(image_folder, m)
                dst = os.path.join(target, m)
                shutil.move(src, dst)
                log_message(f"Moved {m} → {target}", log_signal)
                done += 1
                if progress_signal:
                    pct = int(done / total * 100)
                    progress_signal.emit(min(pct, 100))
    finally:
        driver.quit()
        log_message("Driver chiuso.", log_signal)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python process_files.py <chromedriver_path> <categories_folder> <image_folder> <polygon_id>")
        sys.exit(1)
    _, chrome, cats, imgs, poly = sys.argv
    process_files(chrome, cats, imgs, poly)
