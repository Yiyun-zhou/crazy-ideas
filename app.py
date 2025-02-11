from flask import Flask, request, jsonify, render_template #flask创建web应用
import sqlite3 #sqlite数据库
from openai import OpenAI
import os

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS ingredients (id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()
    conn.close()

# 初始化 OpenAI
client = os.getenv('OPENAI_API_KEY')
#openai.api_key = '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'  # 替换为你的 API Key

# 添加食材
@app.route('/ingredients', methods=['POST'])
def add_ingredient():
    data = request.json
    name = data.get('name')
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute('INSERT INTO ingredients (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()
    return jsonify({'id': c.lastrowid})

# 获取食材列表
@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute('SELECT * FROM ingredients')
    ingredients = c.fetchall()
    conn.close()
    return jsonify(ingredients)

# 生成菜谱
@app.route('/generate-recipe', methods=['POST'])
def generate_recipe():
    data = request.json
    health_goal = data.get('healthGoal', '无')
    taste_preference = data.get('tastePreference', '无')
    meal = data.get('meal', '无')  # 获取用户选择的餐别
    allergy = data.get('allergy', '无')
    servings = data.get('servings', 1)
    extrainfo = data.get('additional', '').strip()

    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute('SELECT name FROM ingredients')
    ingredients = [row[0] for row in c.fetchall()]
    conn.close()

    prompt = f"你是一个顶尖营养师和厨师，请根据以下食材生成一个菜谱：{', '.join(ingredients)}。"
    if health_goal != '无':
        prompt += f"健康目标：{health_goal}。"
    if taste_preference != '无':
        prompt += f"口味偏好：{taste_preference}。"
    if meal != '无':
        prompt += f"餐别：{meal}。"
    if allergy != '无':
        prompt += f"过敏：{allergy}。"
    prompt += f"用餐人数：{servings}人。"

    if extrainfo:
        prompt += f'额外要求：{extrainfo}。'

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    recipe = response.choices[0].message.content
    return jsonify({'recipe': recipe})

# 删除食材
@app.route('/ingredients/<int:id>', methods=['DELETE'])
def delete_ingredient(id):
    conn = sqlite3.connect('fridge.db')
    c = conn.cursor()
    c.execute('DELETE FROM ingredients WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# 首页
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
