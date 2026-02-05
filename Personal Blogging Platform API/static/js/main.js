// Flash message auto-close
document.addEventListener('DOMContentLoaded', function() {
    // Close flash messages
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.opacity = '0';
            setTimeout(() => {
                this.parentElement.remove();
            }, 300);
        });
    });

    // Auto-close flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });
    }

    // Like button functionality
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            const icon = this.querySelector('i');
            
            try {
                const response = await fetch(`/posts/${postId}/like`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Update like count
                    const likeCount = this.querySelector('.like-count');
                    if (likeCount) {
                        likeCount.textContent = data.data.likes_count;
                    }
                    
                    // Toggle icon
                    if (data.data.action === 'liked') {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        this.classList.add('liked');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        this.classList.remove('liked');
                    }
                } else {
                    showToast(data.message, 'error');
                }
            } catch (error) {
                showToast('An error occurred', 'error');
            }
        });
    });

    // Comment form submission
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Posting...';
            
            try {
                const response = await fetch('/comments/add', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Add comment to the list
                    addCommentToDOM(data.comment);
                    this.reset();
                    showToast('Comment posted successfully!', 'success');
                } else {
                    showToast(data.message, 'error');
                }
            } catch (error) {
                showToast('An error occurred', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // Delete post confirmation
    document.querySelectorAll('.delete-post-btn').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!confirm('Are you sure you want to delete this post?')) {
                return;
            }
            
            const postId = this.dataset.postId;
            
            try {
                const response = await fetch(`/posts/${postId}/delete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    window.location.href = '/dashboard';
                } else {
                    showToast(data.message, 'error');
                }
            } catch (error) {
                showToast('An error occurred', 'error');
            }
        });
    });

    // Profile update form
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Saving...';
            
            try {
                const response = await fetch('/profile/update', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showToast('Profile updated successfully!', 'success');
                } else {
                    showToast(data.message, 'error');
                }
            } catch (error) {
                showToast('An error occurred', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // Rich text editor for post content
    const postContent = document.getElementById('post-content');
    if (postContent) {
        // Simple toolbar for text formatting
        const toolbar = document.createElement('div');
        toolbar.className = 'editor-toolbar';
        toolbar.innerHTML = `
            <button type="button" data-command="bold"><i class="fas fa-bold"></i></button>
            <button type="button" data-command="italic"><i class="fas fa-italic"></i></button>
            <button type="button" data-command="insertUnorderedList"><i class="fas fa-list-ul"></i></button>
            <button type="button" data-command="insertOrderedList"><i class="fas fa-list-ol"></i></button>
            <button type="button" data-command="createLink"><i class="fas fa-link"></i></button>
        `;
        
        postContent.parentNode.insertBefore(toolbar, postContent);
        
        toolbar.addEventListener('click', function(e) {
            if (e.target.tagName === 'BUTTON') {
                const command = e.target.dataset.command;
                if (command === 'createLink') {
                    const url = prompt('Enter URL:');
                    if (url) {
                        document.execCommand(command, false, url);
                    }
                } else {
                    document.execCommand(command, false, null);
                }
                postContent.focus();
            }
        });
    }

    // Image preview for file inputs
    const imageInputs = document.querySelectorAll('input[type="file"][accept^="image/"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewId = this.dataset.preview;
                    const preview = previewId ? document.getElementById(previewId) : 
                        this.parentNode.querySelector('.image-preview');
                    
                    if (!preview) {
                        const previewDiv = document.createElement('div');
                        previewDiv.className = 'image-preview';
                        this.parentNode.insertBefore(previewDiv, this.nextSibling);
                    }
                    
                    const previewContainer = preview || this.parentNode.querySelector('.image-preview');
                    previewContainer.innerHTML = `
                        <img src="${e.target.result}" alt="Preview">
                        <button type="button" class="remove-image">&times;</button>
                    `;
                    
                    previewContainer.querySelector('.remove-image').addEventListener('click', function() {
                        previewContainer.remove();
                        input.value = '';
                    });
                }.bind(this);
                reader.readAsDataURL(file);
            }
        });
    });
});

// Helper function to show toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    document.body.appendChild(toast);
    
    // Add styles for toast
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 300px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    });
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Helper function to add comment to DOM
function addCommentToDOM(comment) {
    const commentsList = document.querySelector('.comments-list');
    if (!commentsList) return;
    
    const commentElement = document.createElement('div');
    commentElement.className = 'comment';
    commentElement.innerHTML = `
        <div class="comment-header">
            <img src="${comment.author.profile_image || '/static/images/default-avatar.png'}" 
                 alt="${comment.author.username}" class="comment-avatar">
            <div>
                <strong>${comment.author.username}</strong>
                <span class="comment-date">${new Date(comment.created_at).toLocaleDateString()}</span>
            </div>
        </div>
        <div class="comment-content">${comment.content}</div>
    `;
    
    if (comment.parent_id) {
        const parentComment = document.querySelector(`[data-comment-id="${comment.parent_id}"]`);
        if (parentComment) {
            const replies = parentComment.querySelector('.comment-replies') || 
                (() => {
                    const repliesDiv = document.createElement('div');
                    repliesDiv.className = 'comment-replies';
                    parentComment.appendChild(repliesDiv);
                    return repliesDiv;
                })();
            replies.appendChild(commentElement);
        }
    } else {
        commentsList.appendChild(commentElement);
    }
}

// CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);