searchForm = document.getElementById("search-form");

searchForm.addEventListener("submit", function (event) {
  event.preventDefault();
  const formData = new FormData(searchForm);
  const data = {};
  let csrftoken = "";

  for (const [key, value] of formData.entries()) {
    if (key === "csrfmiddlewaretoken") {
      csrftoken = value;
      continue;
    }

    data[key] = value;
  }

  console.log(data);

  fetch("tours/search/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(data),
  })
    .then((request) => request.json())
    .then((data) => {
      console.log(data);
    });
});
