const map = L.map("map").setView([10.76, 106.66], 10);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

fetch("/tours/map/")
  .then((response) => response.json())
  .then((tours) => {
    const bounds = [];

    tours.forEach((tour) => {
      const marker = L.marker([tour.lat, tour.lng]).addTo(map).bindPopup(`
          <img src="${tour.thumbnail_url}" alt="${tour.title}" style="width: 100px; height: auto; border-radius: 5px;"/><br>
          <b>${tour.title}</b><br>
          <a href="/tours/detail/${tour.id}">Xem chi tiết</a>
        `);

      bounds.push([tour.lat, tour.lng]);
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds);
    }
  });
