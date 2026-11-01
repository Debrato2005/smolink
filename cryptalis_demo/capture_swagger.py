"""Execute the existing URL operation in the original Swagger UI and capture it."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request
from uuid import uuid4

from websockets.sync.client import connect


class Browser:
    def __init__(self, websocket):
        self.websocket = websocket
        self.sequence = 0

    def call(self, method, **params):
        self.sequence += 1
        self.websocket.send(json.dumps({'id': self.sequence, 'method': method, 'params': params}))
        while True:
            response = json.loads(self.websocket.recv(timeout=15))
            if response.get('id') == self.sequence:
                if 'error' in response:
                    raise RuntimeError('Browser command failed: ' + method)
                return response.get('result', {})

    def evaluate(self, expression):
        result = self.call('Runtime.evaluate', expression=expression, returnByValue=True,
                           awaitPromise=True)
        if 'exceptionDetails' in result:
            raise RuntimeError('Browser page evaluation failed.')
        return result['result'].get('value')

    def wait(self, expression, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.evaluate(expression):
                return
            time.sleep(0.1)
        raise RuntimeError('Original Swagger UI did not reach the expected state.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.receipt.exists():
        parser.error('Use new output paths.')
    with tempfile.TemporaryDirectory(prefix='smolink-swagger-') as profile:
        command = ['chromium', '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                   '--disable-gpu', '--remote-debugging-port=0', '--user-data-dir=' + profile,
                   '--window-size=1440,1400', 'about:blank']
        if os.environ.get('HTTPS_PROXY'):
            command[1:1] = ['--proxy-server=' + os.environ['HTTPS_PROXY'],
                            '--proxy-bypass-list=127.0.0.1;localhost;[::1]']
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            port_file = Path(profile) / 'DevToolsActivePort'
            deadline = time.monotonic() + 20
            while not port_file.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.1)
            port = int(port_file.read_text().splitlines()[0])
            targets = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'))
            target = next(target for target in targets if target['type'] == 'page')
            with connect(target['webSocketDebuggerUrl'], max_size=16 * 1024 * 1024) as websocket:
                browser = Browser(websocket)
                browser.call('Page.enable')
                browser.call('Page.navigate', url=args.url.rstrip('/') + '/docs')
                browser.wait("document.querySelectorAll('.opblock').length > 0")
                browser.evaluate("""window.operation = [...document.querySelectorAll('.opblock')].find(
                    x => x.querySelector('.opblock-summary-path').textContent.trim() === '/api/v1/urls');
                    operation.querySelector('.opblock-summary-control').click();""")
                browser.wait("!!operation.querySelector('.try-out__btn')")
                browser.evaluate("operation.querySelector('.try-out__btn').click()")
                browser.wait("!!operation.querySelector('textarea')")
                payload = {'destination': 'https://example.invalid/swagger-live-proof?marker=synthetic-plaintext',
                           'alias': 'swagger-' + uuid4().hex[:12]}
                browser.evaluate("operation.querySelector('textarea').focus(); operation.querySelector('textarea').select()")
                browser.call('Input.insertText', text=json.dumps(payload))
                browser.evaluate("operation.querySelector('.execute').click()")
                browser.wait("!!operation.querySelector('.responses-inner .live-responses-table')")
                browser.wait("!!operation.querySelector('.live-responses-table tbody .response-col_status')")
                status = browser.evaluate("operation.querySelector('.live-responses-table tbody .response-col_status').textContent.trim()")
                response = browser.evaluate("operation.querySelector('.live-responses-table .response-col_description pre').textContent")
                browser.evaluate("operation.querySelector('.responses-inner').scrollIntoView({block:'center'})")
                screenshot = browser.call('Page.captureScreenshot', format='png', captureBeyondViewport=False)
                args.output.write_bytes(base64.b64decode(screenshot['data']))
                with args.receipt.open('x') as stream:
                    json.dump({'url': args.url, 'interface': 'original Smolink Swagger UI',
                        'request': {'method': 'POST', 'path': '/api/v1/urls', 'json': payload},
                        'status': status, 'response_text': response,
                        'screenshot': args.output.name}, stream, indent=2)
                    stream.write('\n')
                print(json.dumps({'swagger_post_status': status, 'screenshot': str(args.output)}))
        finally:
            process.terminate()
            process.wait(timeout=10)


if __name__ == '__main__':
    main()
