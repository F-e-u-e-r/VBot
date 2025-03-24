/**
 * Main JavaScript file for the Tracking Tool application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.navbar-toggler');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickInsideToggle = sidebarToggle.contains(event.target);
            
            if (!isClickInsideSidebar && !isClickInsideToggle && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        });
    }
    
    // Initialize and auto-dismiss toasts after 5 seconds
    const toastElList = document.querySelectorAll('.toast');
    const toastList = [...toastElList].map(toastEl => {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        return toast;
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(alert) {
        // Skip dismissing if it's the file info alert
        if (alert.id === 'file-info') return;
        
        setTimeout(function() {
            // Use Bootstrap's dismiss method if available
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            } else {
                // Fallback to manual removal
                alert.classList.remove('show');
                setTimeout(function() {
                    alert.remove();
                }, 300);
            }
        }, 5000); // 5 seconds
    });

    // Enhanced notification system
    window.showNotification = function(message, type = 'info') {
        // Check if notification container exists, create if not
        let notificationContainer = document.querySelector('.flash-messages');
        
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.className = 'flash-messages';
            document.body.appendChild(notificationContainer);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
        notification.role = 'alert';
        
        // Add appropriate icon based on notification type
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'danger') icon = 'exclamation-triangle';
        if (type === 'warning') icon = 'exclamation-circle';
        
        notification.innerHTML = `
            <i class="bi bi-${icon} me-2"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to container
        notificationContainer.appendChild(notification);
        
        // Set up auto-dismiss
        setTimeout(function() {
            const closeBtn = notification.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            } else {
                notification.classList.remove('show');
                setTimeout(function() {
                    notification.remove();
                }, 300);
            }
        }, 5000);
        
        return notification;
    };
    
    // Global drag and drop zone functionality
    const dragDropZones = document.querySelectorAll('.drag-drop-zone');
    
    if (dragDropZones.length > 0) {
        // Apply to all drag-drop-zones
        dragDropZones.forEach(zone => {
            // Skip if the zone already has event listeners (prevent duplicates)
            if (zone.dataset.initializedDragDrop === 'true') return;
            
            // Mark as initialized
            zone.dataset.initializedDragDrop = 'true';
            
            // Prevent default drag behaviors
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                zone.addEventListener(eventName, function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });
            
            // Add visual feedback on drag over
            ['dragenter', 'dragover'].forEach(eventName => {
                zone.addEventListener(eventName, function() {
                    zone.classList.add('dragover');
                }, false);
            });
            
            // Remove visual feedback when drag leaves or on drop
            ['dragleave', 'drop'].forEach(eventName => {
                zone.addEventListener(eventName, function() {
                    zone.classList.remove('dragover');
                }, false);
            });
        });
    }
    
    // Initialize clipboard functionality for any copy buttons
    const copyButtons = document.querySelectorAll('.btn-copy');
    if (copyButtons.length > 0) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const content = this.getAttribute('data-content');
                
                // Use modern Clipboard API if available
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(content)
                        .then(() => {
                            showCopySuccessState(button);
                            showNotification('Copied to clipboard!', 'success');
                        })
                        .catch(() => {
                            // Fallback
                            copyLegacyMethod(content);
                            showCopySuccessState(button);
                        });
                } else {
                    // Fallback for older browsers
                    copyLegacyMethod(content);
                    showCopySuccessState(button);
                }
            });
        });
    }
    
    function copyLegacyMethod(content) {
        const textarea = document.createElement('textarea');
        textarea.value = content;
        textarea.style.position = 'fixed'; // Avoid scrolling
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
    
    function showCopySuccessState(button) {
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="bi bi-check"></i>';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-secondary');
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
        }, 1500);
    }
});
