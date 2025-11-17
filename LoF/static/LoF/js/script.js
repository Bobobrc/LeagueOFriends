function showLeaderboard(id, buttonId) {
  // Hide all leaderboards
  var leaderboards = document.querySelectorAll(".leaderboard")
  leaderboards.forEach(function (leaderboard) {
    leaderboard.style.display = "none"
  })
  // Show the selected leaderboard
  var selectedLeaderboard = document.getElementById(id)
  if (selectedLeaderboard) {
    selectedLeaderboard.style.display = "block"
  }
  // Remove the active class from all buttons
  var buttons = document.querySelectorAll('button[name="leaderboardButton"]')
  buttons.forEach(function (button) {
    button.classList.remove("active-button")
  })

  // Add the active class to the clicked button
  var clickedButton = document.getElementById(buttonId)
  if (clickedButton) {
    clickedButton.classList.add("active-button")
  }

  // Store the current state in localStorage
  localStorage.setItem("lastViewedLeaderboard", id)
  localStorage.setItem("lastClickedButton", buttonId)
}

document.addEventListener("DOMContentLoaded", function () {
  var lastViewedLeaderboard = localStorage.getItem("lastViewedLeaderboard") || "soloDuoLeaderboard"
  var lastClickedButton = localStorage.getItem("lastClickedButton") || "soloDuoButton"

  showLeaderboard(lastViewedLeaderboard, lastClickedButton)
})
