import React, { useState, useEffect } from 'react';
import {
  Button,
  Input,
  FormControl,
  Flex,
  VerticalStackLayout,
  H2,
  ParagraphMedium,
} from 'frontend/components';
import { TaskService } from 'frontend/services';
import { useAuthContext } from 'frontend/contexts/auth.provider';
import { Task } from 'frontend/types';
import { ButtonKind } from 'frontend/types/button';

const Tasks = () => {
  const { isUserAuthenticated } = useAuthContext();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [newTask, setNewTask] = useState({ title: '', description: '' });
  const [editingTask, setEditingTask] = useState({
    title: '',
    description: '',
  });

  const taskService = new TaskService();

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await taskService.getTasks();
      console.log('response', response);
      if (response.data) {
        setTasks(response.data.items || []);
      }
    } catch (error: any) {
      console.error('Failed to fetch tasks:', error);
      if (error.message?.includes('access token')) {
        // Handle authentication errors
        console.log('Authentication error, redirecting to login');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleAddTask = async () => {
    if (!newTask.title || !newTask.description) return;

    try {
      const response = await taskService.createTask(newTask);
      if (response.data) {
        setTasks([...tasks, response.data]);
        setNewTask({ title: '', description: '' });
        setShowAddForm(false);
      }
    } catch (error: any) {
      console.error('Failed to create task:', error);
      if (error.message?.includes('access token')) {
        console.log('Authentication error, redirecting to login');
      }
    }
  };

  const handleUpdateTask = async (taskId: string) => {
    if (!editingTask.title || !editingTask.description) return;

    try {
      const response = await taskService.updateTask(taskId, editingTask);
      if (response.data) {
        setTasks(
          tasks.map((task) => (task.id === taskId ? response.data! : task)),
        );
        setEditingTaskId(null);
        setEditingTask({ title: '', description: '' });
      }
    } catch (error: any) {
      console.error('Failed to update task:', error);
      if (error.message?.includes('access token')) {
        console.log('Authentication error, redirecting to login');
      }
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      await taskService.deleteTask(taskId);
      setTasks(tasks.filter((task) => task.id !== taskId));
    } catch (error: any) {
      console.error('Failed to delete task:', error);
      if (error.message?.includes('access token')) {
        console.log('Authentication error, redirecting to login');
      }
    }
  };

  const startEditing = (task: Task) => {
    setEditingTaskId(task.id);
    setEditingTask({ title: task.title, description: task.description });
  };

  const cancelEditing = () => {
    setEditingTaskId(null);
    setEditingTask({ title: '', description: '' });
  };

  if (!isUserAuthenticated()) {
    return (
      <div className="p-6">
        <ParagraphMedium>Please log in to view tasks.</ParagraphMedium>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <VerticalStackLayout gap={6}>
        <div className="flex justify-between items-center">
          <H2>Tasks</H2>
          <Button
            kind={ButtonKind.PRIMARY}
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? 'Cancel' : 'Add Task'}
          </Button>
        </div>

        {showAddForm && (
          <div className="border rounded-lg p-4 bg-gray-50">
            <VerticalStackLayout gap={4}>
              <H2>Add New Task</H2>
              <FormControl label="Title">
                <Input
                  value={newTask.title}
                  onChange={(e) =>
                    setNewTask({ ...newTask, title: e.target.value })
                  }
                  placeholder="Enter task title"
                />
              </FormControl>
              <FormControl label="Description">
                <textarea
                  className="w-full rounded-lg border border-stroke bg-white p-4 outline-none focus:border-primary resize-none"
                  rows={3}
                  value={newTask.description}
                  onChange={(e) =>
                    setNewTask({ ...newTask, description: e.target.value })
                  }
                  placeholder="Enter task description"
                />
              </FormControl>
              <Flex gap={3}>
                <Button
                  kind={ButtonKind.PRIMARY}
                  onClick={handleAddTask}
                  disabled={!newTask.title || !newTask.description}
                >
                  Add Task
                </Button>
                <Button
                  kind={ButtonKind.SECONDARY}
                  onClick={() => setShowAddForm(false)}
                >
                  Cancel
                </Button>
              </Flex>
            </VerticalStackLayout>
          </div>
        )}

        {loading ? (
          <div className="text-center py-8">
            <ParagraphMedium>Loading tasks...</ParagraphMedium>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8">
            <ParagraphMedium>
              No tasks found. Create your first task!
            </ParagraphMedium>
          </div>
        ) : (
          <VerticalStackLayout gap={4}>
            {tasks.map((task) => (
              <div key={task.id} className="border rounded-lg p-4">
                {editingTaskId === task.id ? (
                  <VerticalStackLayout gap={3}>
                    <FormControl label="Title">
                      <Input
                        value={editingTask.title}
                        onChange={(e) =>
                          setEditingTask({
                            ...editingTask,
                            title: e.target.value,
                          })
                        }
                      />
                    </FormControl>
                    <FormControl label="Description">
                      <textarea
                        className="w-full rounded-lg border border-stroke bg-white p-4 outline-none focus:border-primary resize-none"
                        rows={3}
                        value={editingTask.description}
                        onChange={(e) =>
                          setEditingTask({
                            ...editingTask,
                            description: e.target.value,
                          })
                        }
                      />
                    </FormControl>
                    <Flex gap={3}>
                      <Button
                        kind={ButtonKind.PRIMARY}
                        onClick={() => handleUpdateTask(task.id)}
                        disabled={
                          !editingTask.title || !editingTask.description
                        }
                      >
                        Save
                      </Button>
                      <Button
                        kind={ButtonKind.SECONDARY}
                        onClick={cancelEditing}
                      >
                        Cancel
                      </Button>
                    </Flex>
                  </VerticalStackLayout>
                ) : (
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <H2>{task.title}</H2>
                      <Flex gap={2}>
                        <Button
                          kind={ButtonKind.SECONDARY}
                          onClick={() => startEditing(task)}
                        >
                          Edit
                        </Button>
                        <Button
                          kind={ButtonKind.SECONDARY}
                          onClick={() => handleDeleteTask(task.id)}
                        >
                          Delete
                        </Button>
                      </Flex>
                    </div>
                    <ParagraphMedium>{task.description}</ParagraphMedium>
                  </div>
                )}
              </div>
            ))}
          </VerticalStackLayout>
        )}
      </VerticalStackLayout>
    </div>
  );
};

export default Tasks;
