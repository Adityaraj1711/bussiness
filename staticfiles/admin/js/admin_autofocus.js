// admin_autofocus.js

document.addEventListener('DOMContentLoaded', function() {
    // Wait for the page to load completely
    setTimeout(function() {
        // Find the Select2 container (for the autocomplete field)
        var select2Container = document.querySelector('.select2-container--admin-autocomplete');

        if (select2Container) {
            // Simulate clicking the Select2 container to open the dropdown
            var select2Selection = select2Container.querySelector('.select2-selection--single');
            if (select2Selection) {
                select2Selection.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));  // Use mousedown
                // Now, wait for the search input to appear and focus on it
                setTimeout(function() {
                    // Find the dynamically added input field for searching
                    var searchInput = document.querySelector('.select2-search__field');
                    if (searchInput) {
                        searchInput.focus();  // Set focus to the search input
                    }
                }, 100);  // Short delay to allow the input field to be rendered
            }
        }
    }, 500);  // Small delay to ensure widgets are fully initialized
});
