import mitmproxy
from mitmproxy.net.http.http1.assemble import assemble_request

def response(flow):
    if all(keyword in flow.request.pretty_url for keyword in ['https://www.zillow.com/homes/', 'zpid']):
        htmldata=flow.response.text
        with open("zillowdata.html","w") as f:
            f.write(htmldata)