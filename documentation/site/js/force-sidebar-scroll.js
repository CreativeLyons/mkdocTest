/**
 * Force Sidebar Scroll to Active Item
 * Ensures the active navigation item is visible in the sidebar on page load
 */
(function() {
    function scrollSidebar() {
        // Target the primary sidebar's scroll container
        var sidebar = document.querySelector('.md-sidebar--primary .md-sidebar__scrollwrap');
        // Target the active link
        var activeLink = document.querySelector('.md-sidebar--primary .md-nav__link--active');
        
        if (sidebar && activeLink) {
            // Get dimensions
            var sidebarRect = sidebar.getBoundingClientRect();
            var activeRect = activeLink.getBoundingClientRect();
            
            // Calculate the position of the active link relative to the visible sidebar area
            // We want to center it, so:
            // Desired Position = (Sidebar Height / 2) - (Link Height / 2)
            
            // Current offset from top of sidebar
            var offsetFromTop = activeRect.top - sidebarRect.top;
            
            // How much we need to scroll:
            // If offsetFromTop is 1000px, and we want it at 300px (center), we scroll down 700px.
            // New ScrollTop = Current ScrollTop + (OffsetFromTop - CenterPosition)
            
            var centerPosition = (sidebar.clientHeight / 2) - (activeLink.clientHeight / 2);
            var scrollAdjustment = offsetFromTop - centerPosition;
            
            sidebar.scrollTop += scrollAdjustment;
        }
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(scrollSidebar, 100);
        });
    } else {
        setTimeout(scrollSidebar, 100);
    }
    
    // Listen for MkDocs Material 'instant' navigation events
    if (typeof document$ !== 'undefined') {
        document$.subscribe(function() {
            // Small timeout to allow rendering to settle after navigation
            setTimeout(scrollSidebar, 100);
        });
    }
})();
