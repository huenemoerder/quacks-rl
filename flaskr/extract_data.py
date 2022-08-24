from db import get_db
from flask import Flask, current_app
import os
import xlsxwriter
import ast

workbook = xlsxwriter.Workbook('plot_data/test.xlsx')
worksheet = workbook.add_worksheet()
row = 0
col = 0

worksheet.write(row, col,'Turn')
worksheet.write(row, col + 1, 'State')
worksheet.write(row, col + 2, 'Player Info')
worksheet.write(row, col + 3, 'bag')
worksheet.write(row, col + 4, 'bag length')
worksheet.write(row, col + 5, 'pot')
worksheet.write(row, col + 6, 'pot length')
worksheet.write(row, col + 7, 'rubies')
worksheet.write(row, col + 8, 'current_score')
worksheet.write(row, col + 9, 'money')
worksheet.write(row, col + 10, 'tmp_vp')
worksheet.write(row, col + 11, 'vp')
worksheet.write(row, col + 12, 'exploded')
worksheet.write(row, col + 13, 'bought')
worksheet.write(row, col + 14, 'bought length')
worksheet.write(row, col + 15, 'bought_')
worksheet.write(row, col + 16, 'bought_ length')
worksheet.write(row, col + 17, 'drop_pos')
worksheet.write(row, col + 18, 'current_pos')
worksheet.write(row, col + 19, 'stopped')
worksheet.write(row, col + 20, 'rats')

# {'bag': [['white', 3], ['white', 1], ['green', 4]], 
# 'pot': [['green', 4], ['orange', 1], ['orange', 1], ['green', 2], ['white', 1], ['white', 2], ['orange', 1], ['white', 1], ['orange', 1], ['green', 4], ['green', 4], ['green', 2], ['green', 1], ['white', 2], ['orange', 1], ['orange', 1], ['green', 2], ['green', 4], ['white', 1]], 
# 'drop_pos': 2, 'current_pos': 38, 'current_score': {'current_position': 38, 'cur_money': 27, 'cur_vp': 10, 'cur_ruby': False},
#  'rats': 0, 'money': 27, 'tmp_vp': 10, 'vp': 26, 'rubies': 2, 'stopped': True, 'exploded': False, 'bought': [], 'bought_': []}

row += 1

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

with app.app_context():
    db = get_db()
    cur = db.cursor()
    for each_row in cur.execute(
        'SELECT *'
        ' FROM gamestate'
        ' ORDER BY id ASC'
    ).fetchall():
        print (each_row['turn'])
        print (each_row['state'])
        print (each_row['player'])

        dict1 = ast.literal_eval(each_row['player'])
        worksheet.write(row, col, each_row['turn'])
        worksheet.write(row, col + 1, each_row['state'])
        worksheet.write(row, col + 2, each_row['player'])
        worksheet.write(row, col + 3, str(dict1['bag']))
        worksheet.write(row, col + 4, len(dict1['bag']))
        worksheet.write(row, col + 5, str(dict1['pot']))
        worksheet.write(row, col + 6, len(dict1['pot']))
        worksheet.write(row, col + 7, str(dict1['rubies']))
        worksheet.write(row, col + 8, str(dict1['current_score']))
        worksheet.write(row, col + 9, str(dict1['money']))
        worksheet.write(row, col + 10, str(dict1['tmp_vp']))
        worksheet.write(row, col + 11, str(dict1['vp']))
        worksheet.write(row, col + 12, str(dict1['exploded']))
        worksheet.write(row, col + 13, str(dict1['bought']))
        worksheet.write(row, col + 14, len(dict1['bought']))
        worksheet.write(row, col + 15, str(dict1['bought_']))
        worksheet.write(row, col + 16, len(dict1['bought_']))
        worksheet.write(row, col + 17, str(dict1['drop_pos']))
        worksheet.write(row, col + 18, str(dict1['current_pos']))
        worksheet.write(row, col + 19, str(dict1['stopped']))
        worksheet.write(row, col + 20, str(dict1['rats']))


        row += 1
        print ('\n')



workbook.close()