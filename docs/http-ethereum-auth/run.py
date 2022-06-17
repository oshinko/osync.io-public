from flask import Flask, jsonify, request
from osnk.httpauth import EthereumAuthentication
from osnk.validations import requires

app = Flask(__name__)
eth_auth = EthereumAuthentication()


@eth_auth.authorization
def authorization(header):
    return request.headers.get(header)


@eth_auth.authenticate
def authenticate(header, scheme):
    return jsonify(error='Unauthorized'), 401, {header: scheme}


@eth_auth.message
def message(address):
    return b'Hello!'


@app.route('/ethereum/addresses', methods=['POST'])
@requires(eth_auth)
def post_ethereum_addresses():
    return jsonify(f'0x{eth_auth.address.hex()}')


@app.route('/')
def get_client():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Client</title>
</head>
<body>
  <script>
    var web3 = new Web3(web3.currentProvider);
    var current = null;
    setInterval(() => {
      if (web3.eth.defaultAccount !== current) {
        current = web3.eth.defaultAccount;
        var hex = web3.toHex("Hello!");
        var from = web3.eth.defaultAccount;
        web3.personal.sign(hex, from, (e, r) => {
          if (e) {
            var result = document.createTextNode(e.message);
            document.querySelector("body").appendChild(result);
            return;
          }
          var req = new XMLHttpRequest();
          req.open("POST", "/ethereum/addresses");
          req.setRequestHeader("Content-Type", "application/json");
          req.setRequestHeader("Authorization", `Ethereum ${from} ${r}`);
          req.onreadystatechange = () => {
            if (req.readyState === 4 && req.status === 200) {
              var address = JSON.parse(req.responseText);
              var result = document.createTextNode(`Accepted ${address}.`);
              document.querySelector("body").appendChild(result);
            }
          };
          req.send();
        });
      }
    }, 100);
  </script>
</body>
</html>
"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
