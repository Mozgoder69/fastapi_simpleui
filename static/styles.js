document.addEventListener("DOMContentLoaded", function () {
  applyStylesToForms();
});

function applyStylesToForms() {
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes) {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) {
            // Check if the node is an element
            if ($(node).hasClass("alpaca-field-input")) {
              $(node).addClass("validate");
            }
            if ($(node).hasClass("alpaca-field-textarea")) {
              $(node).addClass("materialize-textarea");
            }
          }
        });
      }
    });
  });

  observer.observe(document.body, { childList: true, subtree: true });
}

function toast(message, duration = 3000) {
  M.toast({ html: message, displayLength: duration });
}
