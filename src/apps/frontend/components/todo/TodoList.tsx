import React, { useEffect, useState } from 'react';
import { getTodo, updateTodo, deleteTodo } from '../../services/todo.service';
import { Todo } from '../../types/todo';
import TodoItem from './TodoItem';
import TodoForm from './TodoForm';

const TodoList: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);

  const loadTodos = async () => {
    const items = await getTodo();
    setTodos(items);
  };

  useEffect(() => {
    loadTodos();
  }, []);

  const handleUpdateStatus = async (id: string) => {
    try {
      await updateTodo(id, { status: 'Done' });
      const updatedTodos = await getTodo();
      setTodos(updatedTodos);
    } catch (error) {
      console.error('Failed to mark todo as done', error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTodo(id);
      const updatedTodos = await getTodo(); // Re-fetch from backend
      setTodos(updatedTodos);
    } catch (error) {
      console.error('Failed to delete todo:', error);
    }
  };

  return (
    <div>
      <TodoForm onCreate={loadTodos} />
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onUpdateStatus={handleUpdateStatus}
          onDelete={() => handleDelete(todo.id)}
        />
      ))}
    </div>
  );
};

export default TodoList;
