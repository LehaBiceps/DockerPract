from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Конфигурация базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель задачи
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default='normal')  # low, normal, high
    due_date = db.Column(db.String(10), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'due_date': self.due_date,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Создание таблиц
with app.app_context():
    db.create_all()

# Маршруты

@app.route('/')
def index():
    return render_template('index.html')

# API для получения всех задач
@app.route('/api/todos', methods=['GET'])
def get_todos():
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'created_at')
    
    query = Todo.query
    
    # Фильтрация по статусу
    if filter_type == 'completed':
        query = query.filter_by(completed=True)
    elif filter_type == 'active':
        query = query.filter_by(completed=False)
    
    # Поиск по названию и описанию
    if search:
        query = query.filter(
            (Todo.title.ilike(f'%{search}%')) | 
            (Todo.description.ilike(f'%{search}%'))
        )
    
    # Сортировка
    if sort_by == 'priority':
        # Приоритет: high > normal > low
        priority_order = {'high': 1, 'normal': 2, 'low': 3}
        todos = query.all()
        todos.sort(key=lambda x: priority_order.get(x.priority, 2))
    elif sort_by == 'due_date':
        query = query.order_by(Todo.due_date.asc())
        todos = query.all()
    else:
        query = query.order_by(Todo.created_at.desc())
        todos = query.all()
    
    return jsonify([todo.to_dict() for todo in todos])

# API для добавления новой задачи
@app.route('/api/todos', methods=['POST'])
def create_todo():
    try:
        data = request.json
        
        if not data.get('title'):
            return jsonify({'error': 'Название задачи обязательно'}), 400
        
        todo = Todo(
            title=data.get('title'),
            description=data.get('description', ''),
            priority=data.get('priority', 'normal'),
            due_date=data.get('due_date', '')
        )
        
        db.session.add(todo)
        db.session.commit()
        
        return jsonify(todo.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API для обновления задачи
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        todo = Todo.query.get_or_404(todo_id)
        data = request.json
        
        if 'title' in data:
            todo.title = data['title']
        if 'description' in data:
            todo.description = data['description']
        if 'completed' in data:
            todo.completed = data['completed']
        if 'priority' in data:
            todo.priority = data['priority']
        if 'due_date' in data:
            todo.due_date = data['due_date']
        
        db.session.commit()
        return jsonify(todo.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API для удаления задачи
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get_or_404(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': 'Задача удалена'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API для получения статистики
@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = Todo.query.count()
    completed = Todo.query.filter_by(completed=True).count()
    active = total - completed
    
    return jsonify({
        'total': total,
        'completed': completed,
        'active': active,
        'completion_rate': round((completed / total * 100) if total > 0 else 0, 1)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

