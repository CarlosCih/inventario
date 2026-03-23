// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function() {
      // For mobile
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('show');
      } else {
        // For desktop
        sidebar.classList.toggle('hidden');
      }
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
      if (window.innerWidth <= 768) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnToggle = sidebarToggle.contains(event.target);
        
        if (!isClickInsideSidebar && !isClickOnToggle && sidebar.classList.contains('show')) {
          sidebar.classList.remove('show');
        }
      }
    });
  }
});
