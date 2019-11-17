import datetime
import logging
import os

from flask import Flask

from fx_rate.utility import get_fx_rate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/fx-rate', methods=['GET'])
def get():
    usd_jpy = get_fx_rate()
    res = 'timestamp={}, USDJPY={}'.format(
        datetime.datetime.utcnow() + datetime.timedelta(hours=9), usd_jpy)
    logger.info(res)
    return res, 200


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)
