from flask import Flask, request, abort

app = Flask(__name__)
app.config.from_object('settings')
app.config.from_envvar('GOONHILLY_SETTINGS')

import logging
import logging.handlers

if app.config['UA_PARSER']:
    try:
        from ua_parser.py.user_agent_parser import Parse
    except:
        pass


logger = logging.getLogger('Goonhilly')
logger.setLevel(logging.INFO)
log_handler = logging.FileHandler(app.config['GOONHILLY_LOG_FILE'])
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s [%(levelname)s] %(message)s"))
logger.addHandler(log_handler)


def clean(s):
    if ' ' in s:
        s = '"%s"' % s.replace('"', '\'')
    return s


@app.route('/', methods=['GET',])
def index():
    return '<style type="text/css">' \
           '    html, body { height: 100%; margin: 0; padding: 0; }' \
           '    img#bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }' \
           '</style>' \
           '<img src="http://www.sciencephoto.com/images/showFullWatermarked.html/C0015325-Goonhilly_Satellite_Earth_Station,_UK-SPL.jpg?id=670015325" id="bg" />', 200


@app.route('/<source_tag>/', methods=['POST', 'GET',])
def log(source_tag):
    if source_tag not in app.config['GOONHILLY_AUTHORIZED_SOURCE_TAGS']:
        return abort(401)
    
    l = ['%s=%s' % (clean(k), clean(v)) for k, v in request.values.iteritems()]
    l.append('%s=%s' % (clean('client_id'), clean(request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR') or '-')))
    l.append('%s=%s' % (clean('source_tag'), clean(source_tag)))
    if app.config['UA_PARSER']:
        try:
            dict = Parse(request.user_agent.string)
            l.append('%s=%s' % (clean('ua_user_agent_family'), clean("%s" % dict['user_agent'].get('family'))))
            l.append('%s=%s' % (clean('ua_user_agent_major'), clean("%s" % dict['user_agent'].get('major'))))
            l.append('%s=%s' % (clean('ua_user_agent_minor'), clean("%s" % dict['user_agent'].get('minor'))))
            l.append('%s=%s' % (clean('ua_os_family'), clean("%s" % dict['os'].get('family'))))
            l.append('%s=%s' % (clean('ua_os_major'), clean("%s" % dict['os'].get('major'))))
            l.append('%s=%s' % (clean('ua_os_minor'), clean("%s" % dict['os'].get('minor'))))
            l.append('%s=%s' % (clean('ua_device_is_spider'), clean("%s" % dict['device'].get('is_spider'))))
            l.append('%s=%s' % (clean('ua_device_is_mobile'), clean("%s" % dict['device'].get('is_mobile'))))
            l.append('%s=%s' % (clean('ua_device_family'), clean("%s" % dict['device'].get('family'))))
        except:
            l.append('%s=%s' % (clean('ua_logging_error'), clean('True')))
    out = ' '.join(l)
    logger.info(out)
    return 'CREATED', 201


if __name__ == '__main__':
    app.run()

