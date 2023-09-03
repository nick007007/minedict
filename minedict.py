from pathlib import Path
from json import loads, dumps
from random import sample

from translate import Translator
import PySimpleGUI as sg


'''
工具
'''


def load_json(path):
    try:
        text = path.read_text(encoding='utf-8')
        return loads(text)
    except:
        return {}


def save_json(path, obj):
    text = dumps(obj, ensure_ascii=False, indent=4)
    path.write_text(text, encoding='utf-8')


def format_list(iter):
    return '\n'.join(f'{i}. {x}' for i, x in enumerate(iter, 1))


'''
后端
'''


db_path = Path(r'db.json')

output_path = Path(r'词库.txt')

test_path = Path(r'抽测.txt')
answer_path = Path(r'答案.txt')

db = load_json(db_path)

translator = Translator(from_lang='english', to_lang='chinese')


def output_db():
    l = sorted(f'{k}: {v}' for k, v in db.items())
    output_path.write_text(format_list(l), encoding='utf-8')


def sample_db(rate):
    n = int(len(db) * rate)

    if n < 1:
        print('单词不足')
        return

    test, answer = zip(*sample(list(db.items()), n))

    test_path.write_text(format_list(test), encoding='utf-8')
    answer_path.write_text(format_list(answer), encoding='utf-8')

    print('抽测与答案已生成至程序根目录')


'''
前端
'''


layout_1 = \
    [
        [sg.InputText(key='input', size=(20, 1))],
        [sg.Text('加入新单词'), sg.Button('提交')]
    ]


left_col = \
    [
        [sg.Text(f'单词总数：{len(db)}', key='count')],
        [sg.InputOptionMenu(['20%', '40%', '60%', '80%'], default_value='20%', key='menu', size=(3, 1))]
    ]

right_col = \
    [
        [sg.Button('导出词库')],
        [sg.Button('抽测')]
    ]

layout_2 = [[sg.Column(left_col), sg.Column(right_col)]]


layout = \
    [
        [
            sg.Frame('', layout_1),
            sg.Frame('', layout_2),
        ],

        [sg.Text('程序输出')],
        [sg.Output(size=(50, 5))],
    ]


def update():
    word = values['input']

    if word == '':
        print('输入为空')
    elif word in db:
        print('单词已存在')

        print(f'{word}: {db[word]}')
    else:
        print('正在翻译...')

        try:
            trans = translator.translate(word)
            db[word] = trans

            print(f'{word}: {trans}')

            save_json(db_path, db)

            window['input'].update(value='')
            window['count'].update(value=f'单词总数：{len(db)}')

            print('词典已更新')
        except:
            print('翻译失败')


'''
主程序
'''


window = sg.Window('我的词典', layout, finalize=True)

print('欢迎使用, json不存在会自动创建, 录入单词需要联网翻译~')

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == '提交':
        update()

    elif event == '导出词库':
        output_db()

        print('词库已导出至程序根目录')

    elif event == '抽测':
        if values['menu'] == '':
            print('请选择抽测比例')
        else:
            rate = int(values['menu'][: -1]) / 100
            sample_db(rate)

window.close()
