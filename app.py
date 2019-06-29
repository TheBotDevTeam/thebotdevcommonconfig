import json
from functools import wraps

from flask import Flask, render_template, url_for, redirect, request, make_response, jsonify

app = Flask(__name__)

with open('config.json') as cfg:
    config = json.load(cfg)


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.cookies.get('auth') or request.args.get('auth')
        if auth != config['configpwd']:
            return render_template('illegal.html')

        resp = make_response(func(*args, **kwargs))
        resp.set_cookie('auth', auth)
        return resp

    return wrapper


def write_config():
    with open('config.json', 'w') as cfg:
        json.dump(config, cfg)


@app.route('/config/raw/<int:real_shard>')
@require_auth
def get_raw_config(real_shard):
    new_config = config.copy()
    new_config['shard_min'] = int(real_shard * config['dshards'] / config['shards'])
    new_config['shard_max'] = int((real_shard + 1) * config['dshards'] / config['shards'] )
    return jsonify(new_config)


@app.route('/')
@require_auth
def index():
    return render_template('index.html')


@app.route('/config/get')
@require_auth
def get_config():
    return render_template('get-config.html', config=json.dumps(config, indent=4))


@app.route('/config/set', methods=['GET'])
@require_auth
def set_config():
    return render_template('set-config.html', shards=config['shards'], dshards=config['dshards'], token=config['token'])


@app.route('/config/new', methods=['POST'])
@require_auth
def set_config_now():
    token = request.form['token']
    shards = int(request.form['shards'])
    dshards = int(request.form['dshards'])
    config['shards'] = shards
    config['token'] = token
    config['dshards'] = dshards
    write_config()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
