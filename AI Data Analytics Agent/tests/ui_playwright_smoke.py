from playwright.sync_api import sync_playwright
from pathlib import Path
import time

TEST_CSV = Path(__file__).parent / 'ui_test_upload.csv'
TEST_CSV.write_text('a,b,c\n1,2,3\n4,5,6\n')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:8501', timeout=60000)

    # Wait for page to load
    time.sleep(2)

    # If there is a select box for models, pick the first option
    try:
        sel = page.query_selector('select')
        if sel:
            options = sel.eval_on_selector_all('option', 'nodes => nodes.map(n => n.value)')
            if options:
                page.select_option('select', options[0])
    except Exception as e:
        print('MODEL_SELECT_ERR', e)

    # Click Initialize Agent
    try:
        init_btn = page.query_selector('text=Initialize Agent')
        if init_btn:
            init_btn.click()
            time.sleep(1)
    except Exception as e:
        print('INIT_ERR', e)

    # Upload file via input[type=file]
    try:
        input_el = page.query_selector('input[type=file]')
        if input_el:
            input_el.set_input_files(str(TEST_CSV))
            time.sleep(2)
        else:
            print('NO_FILE_INPUT')
    except Exception as e:
        print('UPLOAD_ERR', e)

    # Click Descriptive tab
    try:
        tab = page.query_selector('text=Descriptive')
        if tab:
            tab.click()
            time.sleep(0.5)
    except Exception as e:
        print('TAB_ERR', e)

    # Click Run Descriptive Analysis
    try:
        run_btn = page.query_selector('text=Run Descriptive Analysis')
        if run_btn:
            run_btn.click()
        else:
            # fallback: try to click button by role
            btns = page.query_selector_all('button')
            for b in btns:
                txt = b.inner_text().strip()
                if 'Descriptive' in txt:
                    b.click()
                    break
    except Exception as e:
        print('RUN_DESC_ERR', e)

    # Wait for results
    time.sleep(5)

    # Save screenshot
    out = Path(__file__).parent / 'ui_smoke_result.png'
    page.screenshot(path=str(out), full_page=True)
    print('SCREENSHOT_SAVED', out)

    # Dump some page text for quick verification
    content = page.inner_text('body')[:2000]
    print('PAGE_SNIPPET_START')
    print(content)
    print('PAGE_SNIPPET_END')

    browser.close()
