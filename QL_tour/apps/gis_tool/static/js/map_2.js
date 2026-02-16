const map = L.map("map").setView([10.76, 106.66], 10);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

fetch("/tours")
  .then((response) => response.json())
  .then((data) => {
    console.log(data);
    const geojsonLayer = L.geoJSON(data, {
      onEachFeature: (feature, layer) => {
        layer.bindPopup(
          `
            <img src="${feature.properties.thumbnail}" alt="${feature.properties.title}" style="width: 100px; height: auto; border-radius: 5px;"/><br>
            <b>${feature.properties.title}</b><br>
            <a href="/tours/detail/${feature.id}">Xem chi tiết</a>
          `,
        );
      },
    }).addTo(map);

    map.fitBounds(geojsonLayer.getBounds());
  });
