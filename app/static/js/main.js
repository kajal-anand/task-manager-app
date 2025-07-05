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
                                    ${task.tags && task.tags.length > 0 ? `
                                        <div class="task-tags">
                                            ${task.tags.map(tag => `<span class="tag ${tag.name}">${tag.name}</span>`).join('')}
                                        </div>
                                    ` : ''}
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

    // Edit task - Updated with modal
    window.editTask = async (taskId) => {
        try {
            // First, fetch the current task data
            const response = await fetch(`/api/tasks/${taskId}`);
            const task = await response.json();

            // Populate the modal form
            document.getElementById('edit-title').value = task.title;
            document.getElementById('edit-description').value = task.description || '';
            document.getElementById('edit-deadline').value = task.deadline ?
                new Date(task.deadline).toISOString().slice(0, 16) : '';
            // document.getElementById('edit-priority').value = task.priority || 'medium';

            // Store the task ID for later use
            document.getElementById('edit-form').dataset.taskId = taskId;

            // Show the modal
            openEditModal();
        } catch (error) {
            console.error('Error fetching task for edit:', error);
            alert('Error loading task details. Please try again.');
        }
    };

    // Modal functions
    window.openEditModal = () => {
        const modal = document.getElementById('edit-modal');
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    window.closeEditModal = () => {
        const modal = document.getElementById('edit-modal');
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        document.getElementById('edit-form').reset();
    };

    // Handle edit form submission
    document.getElementById('edit-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const saveBtn = document.getElementById('save-btn');
        const originalText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<div class="loading"></div>';
        saveBtn.disabled = true;

        const taskId = e.target.dataset.taskId;
        const updatedTask = {
            title: document.getElementById('edit-title').value,
            description: document.getElementById('edit-description').value,
            deadline: document.getElementById('edit-deadline').value,
            priority: document.getElementById('edit-priority').value
        };

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedTask)
            });

            if (!response.ok) {
                throw new Error('Failed to update task');
            }

            closeEditModal();
            fetchTasks();
        } catch (error) {
            console.error('Error updating task:', error);
            alert('Error updating task. Please try again.');
        } finally {
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
        }
    });

    // Close modal when clicking outside
    document.getElementById('edit-modal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('edit-modal')) {
            closeEditModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.getElementById('edit-modal').classList.contains('active')) {
            closeEditModal();
        }
    });

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