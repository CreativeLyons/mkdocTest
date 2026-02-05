/**
 * Open all external links in new tabs
 */
(function() {
    'use strict';

    function fixExternalLinks() {
        // Find all links that start with http:// or https://
        document.querySelectorAll('a[href^="http://"], a[href^="https://"]').forEach(function(link) {
            // Don't modify if already has target
            if (!link.hasAttribute('target')) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        });
    }

    // Support for MkDocs Material 'instant' loading
    if (typeof document$ !== 'undefined') {
        document$.subscribe(function() {
            fixExternalLinks();
        });
    } 
    // Fallback for standard themes
    else if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixExternalLinks);
    } else {
        fixExternalLinks();
    }
})();
