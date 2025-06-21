import React from 'react';
import TodoList from '../../components/todo/TodoList';

const TodoPage: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Your TODOs</h1>
      <TodoList />
    </div>
  );
};

export default TodoPage;
