// Evershade Website JavaScript

// Tab switching
document.addEventListener('DOMContentLoaded', function() {
  // Initialize tabs
  document.querySelectorAll('.tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      var tabGroup = this.closest('.tabs');
      var targetId = this.getAttribute('data-tab');
      
      // Deactivate all tabs in group
      tabGroup.querySelectorAll('.tab').forEach(function(t) {
        t.classList.remove('active');
      });
      
      // Activate clicked tab
      this.classList.add('active');
      
      // Show corresponding content
      var contentContainer = tabGroup.nextElementSibling;
      if (contentContainer) {
        contentContainer.querySelectorAll('.tab-content').forEach(function(content) {
          content.classList.remove('active');
        });
        var targetContent = contentContainer.querySelector('#' + targetId);
        if (targetContent) {
          targetContent.classList.add('active');
        }
      }
    });
  });

  // Search functionality
  var searchInput = document.querySelector('.search-box input');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      var query = this.value.toLowerCase();
      var cards = document.querySelectorAll('.card');
      
      cards.forEach(function(card) {
        var text = card.textContent.toLowerCase();
        if (query && !text.includes(query)) {
          card.style.display = 'none';
        } else {
          card.style.display = '';
        }
      });
    });
  }

  // Copy code button
  document.querySelectorAll('pre').forEach(function(pre) {
    var button = document.createElement('button');
    button.textContent = 'Copy';
    button.style.cssText = 'position:absolute;top:0.5rem;right:0.5rem;padding:0.25rem 0.5rem;background:var(--bg-card);border:1px solid var(--border);border-radius:4px;color:var(--text-secondary);font-size:0.75rem;cursor:pointer;';
    pre.style.position = 'relative';
    pre.appendChild(button);
    
    button.addEventListener('click', function() {
      var code = pre.querySelector('code') || pre;
      var text = code.textContent.replace('Copy', '').trim();
      navigator.clipboard.writeText(text).then(function() {
        button.textContent = 'Copied!';
        setTimeout(function() {
          button.textContent = 'Copy';
        }, 2000);
      });
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var targetId = this.getAttribute('href');
      if (targetId !== '#') {
        var target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });
});
