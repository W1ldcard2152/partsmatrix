// Quick Entry Admin JavaScript - Optimized for Fast Data Entry

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initQuickEntry();
    });
    
    function initQuickEntry() {
        // Add loading indicators
        addLoadingIndicators();
        
        // Add keyboard shortcuts
        addKeyboardShortcuts();
        
        // Auto-focus first field
        autoFocusFirstField();
        
        // Add quick action buttons
        addQuickActions();
        
        // Improve form validation feedback
        improveFormFeedback();
        
        // Add keyboard shortcut hints
        addKeyboardHints();
    }
    
    function addLoadingIndicators() {
        // Show loading on form submissions
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function() {
                document.body.classList.add('loading');
            });
        });
        
        // Show loading on admin actions
        const actionButtons = document.querySelectorAll('button[name="_save"], button[name="_addanother"], button[name="_continue"]');
        actionButtons.forEach(button => {
            button.addEventListener('click', function() {
                setTimeout(() => {
                    document.body.classList.add('loading');
                }, 100);
            });
        });
        
        // Show loading on pagination clicks
        const paginationLinks = document.querySelectorAll('.paginator a');
        paginationLinks.forEach(link => {
            link.addEventListener('click', function() {
                document.body.classList.add('loading');
            });
        });
    }
    
    function addKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl+S or Cmd+S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const saveButton = document.querySelector('button[name="_save"]');
                if (saveButton) {
                    saveButton.click();
                }
            }
            
            // Ctrl+Enter or Cmd+Enter to save and add another
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const addAnotherButton = document.querySelector('button[name="_addanother"]');
                if (addAnotherButton) {
                    addAnotherButton.click();
                }
            }
            
            // Escape to cancel/go back
            if (e.key === 'Escape') {
                const cancelLink = document.querySelector('.cancel-link');
                if (cancelLink) {
                    window.location.href = cancelLink.href;
                }
            }
            
            // F2 to toggle keyboard hints
            if (e.key === 'F2') {
                e.preventDefault();
                toggleKeyboardHints();
            }
        });
    }
    
    function autoFocusFirstField() {
        // Auto-focus first input field that's not hidden
        const firstInput = document.querySelector('input[type="text"]:not([readonly]):not([disabled]), select:not([disabled]), textarea:not([readonly]):not([disabled])');
        if (firstInput && !firstInput.value) {
            firstInput.focus();
        }
    }
    
    function addQuickActions() {
        // Add quick action bar to change forms
        const contentArea = document.querySelector('#content');
        if (contentArea && document.querySelector('.change-form')) {
            const quickActionsBar = document.createElement('div');
            quickActionsBar.className = 'quick-actions';
            quickActionsBar.innerHTML = `
                <button type="button" class="quick-btn" onclick="clearForm()">Clear Form</button>
                <button type="button" class="quick-btn success" onclick="duplicateRecord()">Duplicate</button>
                <button type="button" class="quick-btn" onclick="toggleCollapsed()">Toggle Details</button>
            `;
            contentArea.insertBefore(quickActionsBar, contentArea.firstChild);
        }
    }
    
    function improveFormFeedback() {
        // Add real-time validation feedback
        const requiredFields = document.querySelectorAll('input[required], select[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', function() {
                if (!this.value) {
                    this.style.borderColor = '#dc3545';
                } else {
                    this.style.borderColor = '#28a745';
                }
            });
            
            field.addEventListener('input', function() {
                if (this.value) {
                    this.style.borderColor = '#28a745';
                }
            });
        });
    }
    
    function addKeyboardHints() {
        const hintsDiv = document.createElement('div');
        hintsDiv.className = 'keyboard-hints';
        hintsDiv.innerHTML = `
            <strong>Keyboard Shortcuts:</strong><br>
            Ctrl+S: Save<br>
            Ctrl+Enter: Save & Add Another<br>
            Esc: Cancel<br>
            F2: Toggle hints
        `;
        document.body.appendChild(hintsDiv);
    }
    
    function toggleKeyboardHints() {
        const hints = document.querySelector('.keyboard-hints');
        if (hints) {
            hints.classList.toggle('show');
        }
    }
    
    // Global utility functions
    window.clearForm = function() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="number"], textarea');
        inputs.forEach(input => {
            if (!input.readOnly) {
                input.value = '';
            }
        });
        
        const selects = document.querySelectorAll('select');
        selects.forEach(select => {
            if (!select.disabled) {
                select.selectedIndex = 0;
            }
        });
        
        autoFocusFirstField();
    };
    
    window.duplicateRecord = function() {
        // Create a new record with current form data
        const form = document.querySelector('form');
        if (form) {
            const action = form.action.replace(/\/\d+\/change\/$/, '/add/');
            form.action = action;
            
            // Remove ID field if it exists
            const idField = document.querySelector('input[name="id"]');
            if (idField) {
                idField.remove();
            }
            
            // Submit as new record
            const saveButton = document.querySelector('button[name="_save"]');
            if (saveButton) {
                saveButton.click();
            }
        }
    };
    
    window.toggleCollapsed = function() {
        const collapsedSections = document.querySelectorAll('.collapse');
        collapsedSections.forEach(section => {
            section.classList.toggle('collapsed');
        });
    };
    
    // Auto-save draft functionality (localStorage)
    function enableAutoSave() {
        const form = document.querySelector('.change-form form, .add-form form');
        if (!form) return;
        
        const formId = window.location.pathname;
        const inputs = form.querySelectorAll('input, select, textarea');
        
        // Load saved data
        inputs.forEach(input => {
            const savedValue = localStorage.getItem(`draft_${formId}_${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });
        
        // Save data on change
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                localStorage.setItem(`draft_${formId}_${input.name}`, input.value);
            });
        });
        
        // Clear draft on successful save
        form.addEventListener('submit', function() {
            inputs.forEach(input => {
                localStorage.removeItem(`draft_${formId}_${input.name}`);
            });
        });
    }
    
    // Enable auto-save for forms
    enableAutoSave();
    
    // Add performance monitoring
    function addPerformanceMonitoring() {
        let startTime = performance.now();
        
        window.addEventListener('load', function() {
            const loadTime = performance.now() - startTime;
            if (loadTime > 1000) {
                console.warn(`Slow page load: ${loadTime.toFixed(0)}ms`);
                
                // Show performance warning to admins
                if (document.querySelector('.messagelist')) {
                    const warning = document.createElement('div');
                    warning.className = 'messagelist';
                    warning.innerHTML = `
                        <div class="warning">
                            Page loaded slowly (${loadTime.toFixed(0)}ms). 
                            Consider reducing page size or optimizing queries.
                        </div>
                    `;
                    document.querySelector('#content').insertBefore(warning, document.querySelector('#content').firstChild);
                }
            }
        });
    }
    
    addPerformanceMonitoring();
    
})();
