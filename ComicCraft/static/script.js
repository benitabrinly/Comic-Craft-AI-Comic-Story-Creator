// Show a loading screen while the comic is being generated.
var form = document.getElementById("comic-form");
if (form) {
  form.addEventListener("submit", function () {
    document.getElementById("loading").hidden = false;
    form.querySelector("button[type=submit]").disabled = true;
  });
}
