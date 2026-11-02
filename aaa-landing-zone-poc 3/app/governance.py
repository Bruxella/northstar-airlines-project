"""Pure-Python governance engine. No cloud credentials needed for the demo."""
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'app' / 'state.json'
BASELINE = {
    'development': {'allowed_regions': ['eu-west-1', 'us-east-1'], 'require_mfa': True, 'public_s3_block': True, 'ebs_encryption': True, 'log_retention_days': 30, 'access_tier': 'developer'},
    'testing': {'allowed_regions': ['eu-west-1'], 'require_mfa': True, 'public_s3_block': True, 'ebs_encryption': True, 'log_retention_days': 90, 'access_tier': 'tester'},
    'production': {'allowed_regions': ['eu-west-1'], 'require_mfa': True, 'public_s3_block': True, 'ebs_encryption': True, 'log_retention_days': 365, 'access_tier': 'read-only'},
}
IMMUTABLE = {'require_mfa', 'public_s3_block', 'ebs_encryption'}


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def init_state():
    return {'policy_version': 1, 'accounts': [
        {'id': '111111111111', 'name': 'booking-dev', 'env': 'development', 'overrides': {}, 'actual': {}, 'last_deployment': 'never'},
        {'id': '222222222222', 'name': 'booking-test', 'env': 'testing', 'overrides': {}, 'actual': {}, 'last_deployment': 'never'},
        {'id': '333333333333', 'name': 'booking-prod', 'env': 'production', 'overrides': {}, 'actual': {}, 'last_deployment': 'never'},
        {'id': '444444444444', 'name': 'analytics-prod', 'env': 'production', 'overrides': {}, 'actual': {}, 'last_deployment': 'never'},
        {'id': '555555555555', 'name': 'crew-dev', 'env': 'development', 'overrides': {}, 'actual': {}, 'last_deployment': 'never'},
        {'id': '666666666666', 'name': 'crew-test', 'env': 'testing', 'overrides': {}, 'actual': {}, 'last_deployment': 'never'},
    ], 'deployments': [], 'exceptions': []}


def load():
    if not DATA.exists():
        save(init_state())
    return json.loads(DATA.read_text())


def save(state):
    tmp = DATA.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, indent=2) + '\n')
    tmp.replace(DATA)


def desired(account):
    cfg = dict(BASELINE[account['env']])
    overrides = account.get('overrides', {})
    if IMMUTABLE.intersection(overrides):
        raise ValueError('Organization-wide security controls cannot be overridden')
    cfg.update(overrides)
    return cfg


def assess(account):
    expected = desired(account)
    actual = account.get('actual') or {}
    mismatches = {k: {'expected': v, 'actual': actual.get(k)} for k, v in expected.items() if actual.get(k) != v}
    return {'status': 'compliant' if not mismatches else 'drifted', 'drift': mismatches, 'expected': expected}


def inventory(state):
    return [{**a, **assess(a)} for a in state['accounts']]


def reconcile(state, ids=None, fail_ids=None):
    ids = set(ids or [a['id'] for a in state['accounts']])
    fail_ids = set(fail_ids or [])
    results = []
    for a in state['accounts']:
        if a['id'] not in ids:
            continue
        status = 'failed' if a['id'] in fail_ids else 'succeeded'
        if status == 'succeeded':
            a['actual'] = desired(a).copy()
            a['last_deployment'] = now()
        results.append({'account': a['id'], 'name': a['name'], 'env': a['env'], 'status': status, 'at': now(), 'policy_version': state['policy_version']})
    state['deployments'] = (results[::-1] + state['deployments'])[:250]
    return results


def add_account(state, account_id, name, env):
    if env not in BASELINE:
        raise ValueError('Invalid environment')
    if not account_id.isdigit() or len(account_id) != 12:
        raise ValueError('Account ID must be 12 digits')
    if any(a['id'] == account_id for a in state['accounts']):
        raise ValueError('Account already exists')
    account = {'id': account_id, 'name': name, 'env': env, 'overrides': {}, 'actual': {}, 'last_deployment': 'never'}
    state['accounts'].append(account)
    return account


def request_exception(state, account_id, key, value, ticket, expiry):
    account = next((a for a in state['accounts'] if a['id'] == account_id), None)
    if not account:
        raise ValueError('Unknown account')
    if key in IMMUTABLE or key not in BASELINE[account['env']]:
        raise ValueError('Security guardrail or unknown key cannot be exempted')
    if not ticket or not expiry:
        raise ValueError('Ticket and expiration are required')
    exception = {'account': account_id, 'key': key, 'value': value, 'ticket': ticket, 'expiry': expiry, 'status': 'pending', 'created': now()}
    state['exceptions'].append(exception)
    return exception


def approve_exception(state, index):
    exception = state['exceptions'][index]
    if exception['status'] != 'pending':
        raise ValueError('Only pending exceptions can be approved')
    if exception['expiry'] < now()[:10]:
        raise ValueError('Cannot approve an expired exception')
    account = next(a for a in state['accounts'] if a['id'] == exception['account'])
    account['overrides'][exception['key']] = exception['value']
    exception['status'] = 'approved'
    return exception
