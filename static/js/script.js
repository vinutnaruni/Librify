// Custom JavaScript for Library Management System

// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss alerts after 5 seconds
  setTimeout(() => {
    const alerts = document.querySelectorAll(".alert")
    alerts.forEach((alert) => {
      // Check if Bootstrap is available
      if (typeof bootstrap !== "undefined") {
        const bsAlert = new bootstrap.Alert(alert)
        bsAlert.close()
      } else {
        // Fallback if Bootstrap JS is not loaded
        alert.classList.remove("show")
        setTimeout(() => {
          alert.remove()
        }, 300)
      }
    })
  }, 5000)

  // Initialize tooltips if Bootstrap is available
  if (typeof bootstrap !== "undefined") {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
  }

  // Password confirmation validation
  const passwordField = document.getElementById("password")
  const confirmPasswordField = document.getElementById("confirm_password")

  if (passwordField && confirmPasswordField) {
    confirmPasswordField.addEventListener("input", () => {
      if (passwordField.value !== confirmPasswordField.value) {
        confirmPasswordField.setCustomValidity("Passwords don't match")
      } else {
        confirmPasswordField.setCustomValidity("")
      }
    })
  }

  // Book search form validation
  const searchForm = document.querySelector('form[action*="books"]')
  if (searchForm) {
    searchForm.addEventListener("submit", (event) => {
      const searchInput = searchForm.querySelector('input[name="search"]')
      if (searchInput && searchInput.value.trim() === "" && !searchForm.querySelector('select[name="genre"]').value) {
        event.preventDefault()
        searchInput.focus()
      }
    })
  }

  // Add current year to footer
  const yearElement = document.querySelector(".current-year")
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear()
  }

  // Confirm delete actions
  const deleteButtons = document.querySelectorAll("[data-confirm]")
  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      if (!confirm(this.getAttribute("data-confirm"))) {
        event.preventDefault()
      }
    })
  })

  // Book quantity validation
  const quantityInput = document.getElementById("quantity")
  if (quantityInput) {
    quantityInput.addEventListener("input", function () {
      if (Number.parseInt(this.value) < 1) {
        this.value = 1
      }
    })
  }

  // Toggle password visibility
  const togglePasswordButtons = document.querySelectorAll(".toggle-password")
  togglePasswordButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const passwordInput = document.querySelector(this.getAttribute("data-target"))
      if (passwordInput) {
        if (passwordInput.type === "password") {
          passwordInput.type = "text"
          this.innerHTML = '<i class="fas fa-eye-slash"></i>'
        } else {
          passwordInput.type = "password"
          this.innerHTML = '<i class="fas fa-eye"></i>'
        }
      }
    })
  })

  // Add animation classes to elements as they scroll into view
  const animateOnScroll = () => {
    const elements = document.querySelectorAll(".card, .jumbotron, .stats-card")

    elements.forEach((element) => {
      const elementPosition = element.getBoundingClientRect().top
      const screenPosition = window.innerHeight / 1.2

      if (elementPosition < screenPosition) {
        element.classList.add("fade-in")
      }
    })
  }

  // Run on page load
  animateOnScroll()

  // Run on scroll
  window.addEventListener("scroll", animateOnScroll)
})
