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

            if (tasks.length === 0) {
                taskList.innerHTML = `
                            <div class="empty-state">
                                <h3>No ${activeTab} tasks</h3>
                                <p>You're all caught up! 🎉</p>
                            </div>
                        `;
                return;
            }

            tasks.forEach(task => {
                const taskElement = document.createElement('div');
                taskElement.className = `task-card ${task.priority}`;

                const deadlineText = task.deadline ?
                    new Date(task.deadline).toLocaleString() :
                    'No deadline';

                taskElement.innerHTML = `
                            <div class="task-header">
                                <div>
                                    <h3 class="task-title">${task.title}</h3>
                                    ${task.description ? `<p class="task-description">${task.description}</p>` : ''}
                                </div>
                                <span class="priority-badge priority-${task.priority}">
                                    ${task.priority}
                                </span>
                            </div>
                            <div class="task-meta">
                                <span>⏰ ${deadlineText}</span>
                            </div>
                            <div class="task-actions">
                                ${!task.completed ? `
                                    <button onclick="completeTask(${task.id})" class="btn btn-success btn-small">
                                        ✅ Complete
                                    </button>
                                    <button onclick="editTask(${task.id})" class="btn btn-warning btn-small">
                                        ✏️ Edit
                                    </button>
                                ` : ''}
                                <button onclick="deleteTask(${task.id})" class="btn btn-danger btn-small">
                                    🗑️ Delete
                                </button>
                            </div>
                        `;
                taskList.appendChild(taskElement);
            });
        } catch (error) {
            console.error('Error fetching tasks:', error);
            taskList.innerHTML = '<div class="error-message">Error loading tasks. Please try again.</div>';
        }
    };

    // Create task
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = taskForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        submitBtn.innerHTML = '<div class="loading"></div>';
        submitBtn.disabled = true;

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
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });

    // Complete task
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
            taskList.innerHTML = `<div class="error-message">Error completing task: ${error.message}</div>`;
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
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            fetchTasks();
        });
    });

    // Initial fetch
    fetchTasks();
});