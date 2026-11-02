"""Local demo server: python -m app.server (standard library only)."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import os
from urllib.parse import urlparse
from app import governance as g

INDEX = Path(__file__).with_name('index.html')

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, payload):
        out = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            out = INDEX.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)
        elif path == '/api/state':
            s = g.load()
            self.respond(200, {'policy_version': s['policy_version'], 'accounts': g.inventory(s), 'deployments': s['deployments'], 'exceptions': s['exceptions'], 'policy': g.BASELINE})
        elif path == '/health':
            self.respond(200, {'status': 'ok'})
        else:
            self.respond(404, {'error': 'not found'})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length > 16384:
                raise ValueError('Request too large')
            data = json.loads(self.rfile.read(length) or '{}')
            s = g.load()
            path = urlparse(self.path).path
            if path == '/api/reconcile':
                result = g.reconcile(s, data.get('ids'), data.get('fail_ids'))
            elif path == '/api/drift':
                a = next(a for a in s['accounts'] if a['id'] == data['id'])
                key = data.get('key', 'public_s3_block')
                if key not in g.BASELINE[a['env']]:
                    raise ValueError('Unknown setting')
                a['actual'][key] = data.get('value', False)
                result = g.assess(a)
            elif path == '/api/accounts':
                result = g.add_account(s, data['id'], data['name'], data['env'])
            elif path == '/api/policy-version':
                s['policy_version'] += 1
                result = {'policy_version': s['policy_version'], 'note': 'A centrally versioned policy release triggers fleet reconcile; current policy values remain unchanged in this demo'}
            elif path == '/api/exceptions':
                result = g.request_exception(s, data['id'], data['key'], data['value'], data['ticket'], data['expiry'])
            elif path == '/api/exceptions/approve':
                result = g.approve_exception(s, int(data['index']))
            elif path == '/api/reset':
                s = g.init_state()
                result = {'reset': True}
            else:
                return self.respond(404, {'error': 'not found'})
            g.save(s)
            self.respond(200, {'result': result})
        except (ValueError, KeyError, StopIteration, IndexError, TypeError) as e:
            self.respond(400, {'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8765'))
    print(f'AAA Landing Zone Governance Demo: http://localhost:{port}', flush=True)
    HTTPServer(('127.0.0.1', port), Handler).serve_forever()
