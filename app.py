# -*- coding: utf-8 -*-
import json

import os
import piecash
import pymysql
from flask import Flask, request, render_template

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def hello():
    # try:
    #     book = piecash.open_book(uri_conn=os.environ['JAWSDB_URL'], readonly=False, do_backup=False,
    #                              open_if_lock=True)
    # except Exception as e:
    #     return '{}'.format(e)
    #
    # income = 100
    # outcome = -23
    # in_tree = income_tree(book.root_account.children(type="INCOME"))
    # ex_tree = income_tree(book.root_account.children(type="EXPENSE"))
    #
    # accounts = [{'id': a.guid, 'name': a.fullname} for a in book.accounts]

    return render_template("index.html")


@app.route('/data')
def get_income_ajax():
    try:
        book = piecash.open_book(uri_conn=os.environ['JAWSDB_URL'], readonly=False, do_backup=False,
                                 open_if_lock=True)
    except Exception as e:
        return json.dumps({'error': '{}'.format(e)})

    income = get_income(book)
    expense = get_expense(book)
    accounts = [{'id': a.guid, 'name': a.fullname, 'shortname': a.name} for a in book.accounts]

    ctx = {
        'income': '{:.2f}'.format(income),
        'expense': '{:.2f}'.format(expense),
        'balance': '{:.2f}'.format(income + expense),
        'accounts': accounts
    }

    return json.dumps(ctx)


@app.route('/add_entry', methods=("POST",))
def add_entry():
    account = request.form.get('expense_account')
    amount = request.form.get('expense_amount')

    if account and amount:
        response = {
            'status': 'success',
        }
    else:
        response = {
            'status': 'danger',
            'message': 'Buuuu!'
        }

    return json.dumps(response)


def get_splits_sum(book, account_type):
    _sum = 0
    for account in book.accounts:
        if account.type == account_type and account.placeholder != 1:
            for split in account.splits:
                _sum -= split.value

    return _sum


def account_balance(account):
    balance = 0
    for split in account.splits:
        balance -= split.value

    return balance


def get_income(book):
    return float(get_splits_sum(book, "INCOME"))


def get_expense(book):
    return float(get_splits_sum(book, "EXPENSE"))


def income_tree(account):
    tree = {
        'name': u'{}'.format(account.name),
        'balance': account_balance(account),
        'children': []
    }
    for acc in account.children:
        tree['children'].append(income_tree(acc))

    for child in tree['children']:
        tree['balance'] += child['balance']

    return tree


app.run(host="0.0.0.0", port=8000, debug=True)
