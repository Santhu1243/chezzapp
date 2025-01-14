function confirmLogout() {
  const confirmation = window.confirm("Are you sure you want to log out?");
  if (confirmation) {
    document.getElementById("logout-form").submit();
  }
}
