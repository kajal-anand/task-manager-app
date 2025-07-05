document.addEventListener('DOMContentLoaded', () => {
    const taskForm = document.getElementById('task-form');
    const taskList = document.getElementById('task-list');
    const tabButtons = document.querySelectorAll('.tab-button');
    let activeTab = 'upcoming';

    // Fetch and display tasks
    const fetchTasks = async () => {
        try {
            const response = await fetch(`/api/tasks/?status=${activeTab}&ordering=-priority`);
            const tasks = await response.json();
            taskList.innerHTML = '';
            tasks.forEach(task => {
                const taskElement = document.createElement('div');
                taskElement.className = `task-card border p-4 rounded flex justify-between items-center ${task.priority}`;
                taskElement.innerHTML = `
                    <div>
                        <h3 class="font-bold">${task.title}</h3>
                        <p>${task.description || ''}</p>
                        <p>Deadline: ${task.deadline ? new Date(task.deadline).toLocaleString() : 'None'}</p>
                        <p>Priority: ${task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}</p>
                    </div>
                    <div class="flex gap-2">
                        ${!task.completed ? `
                            <button onclick="completeTask(${task.id})" class="bg-green-500 text-white px-4 py-2 rounded">Complete</button>
                            <button onclick="editTask(${task.id})" class="bg-yellow-500 text-white px-4 py-2 rounded">Edit</button>
                        ` : ''}
                        <button onclick="deleteTask(${task.id})" class="bg-red-500 text-white px-4 py-2 rounded">Delete</button>
                    </div>
                `;
                taskList.appendChild(taskElement);
            });
        } catch (error) {
            console.error('Error fetching tasks:', error);
            taskList.innerHTML = '<p class="text-red-500">Error loading tasks</p>';
        }
    };

    // Create task
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const task = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            deadline: document.getElementById('deadline').value
        };
        try {
            await fetch('/api/tasks/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(task)
            });
            taskForm.reset();
            fetchTasks();
        } catch (error) {
            console.error('Error creating task:', error);
        }
    });

    // Complete task
    // Only showing the updated completeTask function
    window.completeTask = async (taskId) => {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed: true })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}, detail: ${JSON.stringify(errorData)}`);
            }
            fetchTasks();
        } catch (error) {
            console.error('Error completing task:', error);
            taskList.innerHTML = `<p class="text-red-500">Error completing task: ${error.message}</p>`;
        }
    };
    // Edit task
    window.editTask = async (taskId) => {
        const title = prompt('Enter new title:');
        const description = prompt('Enter new description:');
        const deadline = prompt('Enter new deadline (YYYY-MM-DDTHH:MM):');
        if (title) {
            try {
                await fetch(`/api/tasks/${taskId}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description, deadline })
                });
                fetchTasks();
            } catch (error) {
                console.error('Error updating task:', error);
            }
        }
    };

    // Delete task
    window.deleteTask = async (taskId) => {
        if (confirm('Are you sure you want to delete this task?')) {
            try {
                await fetch(`/api/tasks/${taskId}`, {
                    method: 'DELETE'
                });
                fetchTasks();
            } catch (error) {
                console.error('Error deleting task:', error);
            }
        }
    };

    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            activeTab = button.dataset.status;
            tabButtons.forEach(btn => btn.classList.replace('bg-blue-500', 'bg-gray-200'));
            tabButtons.forEach(btn => btn.classList.replace('text-white', 'text-black'));
            button.classList.replace('bg-gray-200', 'bg-blue-500');
            button.classList.replace('text-black', 'text-white');
            fetchTasks();
        });
    });

    // Initial fetch
    fetchTasks();
});