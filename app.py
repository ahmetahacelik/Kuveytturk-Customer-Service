from flask import Flask, request,render_template
from flask import send_file
from KuveytturkService import KuveytturkCustomerService

app = Flask(__name__)


@app.route('/')
def mainFunc():
    return render_template("text.html")


@app.route('/myapp',methods = ['POST', 'GET'])
def login():
      iban = request.form['iban']
      cvc = request.form['cvc']
      kuveytturk=KuveytturkCustomerService(iban,cvc)
      kuveytturk.main()

      return send_file(iban + ".pdf", as_attachment=True)




if __name__ == '__main__':
    app.run(debug = True)