import os
import asyncio
import tempfile
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = "8056697346:AAGNTjD9OW4KcvMbKkIBkx_5RK6Nd7klB0w"

YANDEX_BROWSER_PATH = r"C:\Users\user\AppData\Local\Yandex\YandexBrowser\Application\browser.exe"
YANDEXDRIVER_PATH_1 = r"C:\Users\user\Desktop\yandexdriver\yandexdriver.exe"
YANDEXDRIVER_PATH_2 = r"C:\Users\user\Desktop\yandexdriver2\yandexdriver.exe"
YANDEXDRIVER_PATH_3 = r"C:\Users\user\Desktop\yandexdriver3\yandexdriver.exe"

def get_chrome_options():
    chrome_options = Options()
    chrome_options.binary_location = YANDEX_BROWSER_PATH
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=ru")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=375,5000")
    chrome_options.add_experimental_option("prefs", {
        "translate_whitelists": {"ko": "ru"},
        "translate": {"enabled": True}
    })
    return chrome_options

async def process_sku(update: Update, context: CallbackContext, sku: str):
    msg = await update.message.reply_text("Ожидайте... Обрабатывается страница технического состояния.")
    try:
        options = get_chrome_options()
        driver = webdriver.Chrome(service=ChromeService(YANDEXDRIVER_PATH_1), options=options)
        driver.get(f"https://fem.encar.com/cars/report/inspect/{sku}")
        await asyncio.sleep(7)

        try:
            btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Просмотреть все в развернутом виде')]")
            driver.execute_script("arguments[0].scrollIntoView();", btn)
            await asyncio.sleep(1)
            btn.click()
            await asyncio.sleep(3)
        except NoSuchElementException:
            pass

        driver.set_window_size(375, 4492)
        await asyncio.sleep(2)
        screenshot = driver.get_screenshot_as_png()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            pdf_path = temp.name
            Image.open(BytesIO(screenshot)).save(pdf_path, "PDF")

        with open(pdf_path, "rb") as f:
            await update.message.reply_document(f, filename="Техническое_состояние.pdf")
        os.remove(pdf_path)
    except:
        pass
    finally:
        await msg.delete()
        try:
            driver.quit()
        except:
            pass

async def process_accident_page(update: Update, context: CallbackContext, sku: str):
    msg = await update.message.reply_text("Ожидайте... Обрабатывается страница страховой истории.")
    try:
        options = get_chrome_options()
        driver = webdriver.Chrome(service=ChromeService(YANDEXDRIVER_PATH_2), options=options)
        driver.get(f"https://fem.encar.com/cars/report/accident/{sku}")
        await asyncio.sleep(7)

        try:
            btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Просмотреть все развернутые')]")
            driver.execute_script("arguments[0].scrollIntoView();", btn)
            await asyncio.sleep(1)
            btn.click()
            await asyncio.sleep(3)
        except NoSuchElementException:
            pass

        driver.set_window_size(375, 5000)
        await asyncio.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(2)

        screenshot = driver.get_screenshot_as_png()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            pdf_path = temp.name
            Image.open(BytesIO(screenshot)).save(pdf_path, "PDF")

        with open(pdf_path, "rb") as f:
            await update.message.reply_document(f, filename="Страховая_история.pdf")
        os.remove(pdf_path)
    except:
        pass
    finally:
        await msg.delete()
        try:
            driver.quit()
        except:
            pass

async def process_diagnosis_page(update: Update, context: CallbackContext, sku: str):
    msg = await update.message.reply_text("Ожидайте... Обрабатывается страница диагностики.")
    try:
        options = get_chrome_options()
        driver = webdriver.Chrome(service=ChromeService(YANDEXDRIVER_PATH_3), options=options)
        driver.get(f"https://fem.encar.com/cars/report/diagnosis/{sku}")
        await asyncio.sleep(8)

        driver.set_window_size(375, 5000)
        await asyncio.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(2)

        screenshot = driver.get_screenshot_as_png()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            pdf_path = temp.name
            Image.open(BytesIO(screenshot)).save(pdf_path, "PDF")

        with open(pdf_path, "rb") as f:
            await update.message.reply_document(f, filename="Диагностика.pdf")
        os.remove(pdf_path)
    except:
        pass
    finally:
        await msg.delete()
        try:
            driver.quit()
        except:
            pass

async def start(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        return
    sku = args[0].replace("sku_", "")
    await asyncio.gather(
        process_sku(update, context, sku),
        process_accident_page(update, context, sku),
        process_diagnosis_page(update, context, sku)
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()