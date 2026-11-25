import subprocess, time, pathlib, urllib.request, urllib.error, pytest, shutil, sys
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
URL = "http://localhost:8767/"
DADOS = RAIZ / "tests" / "dados"


@pytest.fixture(scope="session", autouse=True)
def servidor():
    subprocess.run([sys.executable, str(RAIZ / "tests" / "gerar_dados.py")], check=True)
    # Nunca reaproveitar um servidor já aberto: ele pode servir outra pasta (outra versão do app)
    # e os testes passariam contra o código errado (25/11/2026).
    try:
        urllib.request.urlopen(URL, timeout=1)
        pytest.exit(f"Porta 8767 já ocupada por outro servidor; feche-o antes de testar ({URL})", returncode=2)
    except urllib.error.URLError:
        pass
    p =subprocess.Popen([sys.executable, "-m", "http.server", "8767", "--directory", str(RAIZ)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        try:
            urllib.request.urlopen(URL, timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    yield
    p.terminate()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        exe = "/usr/bin/google-chrome"
        b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
        yield b
        b.close()


@pytest.fixture()
def ctx(browser):
    c = browser.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True,
                            service_workers="allow")
    c.set_default_timeout(4000)
    c.reqs = []
    c.on("request", lambda r: c.reqs.append(r.url))
    yield c
    c.close()


@pytest.fixture()
def page(ctx):
    pg = ctx.new_page()
    pg.goto(URL)
    pg.wait_for_timeout(800)
    return pg
