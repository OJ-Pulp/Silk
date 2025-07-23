document.querySelectorAll('.sidebar-button').forEach(button => {
  button.addEventListener('click', () => {
    const action = button.getAttribute('data-tooltip');
    console.log(`Clicked: ${action}`);
    // Placeholder for action-specific code
  });
});