const map = L.map("map").setView([10.76, 106.66], 10);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

const pathSegments = window.location.pathname.split("/");
const tourId = pathSegments[pathSegments.length - 1];

fetch(`../route-map/${tourId}`)
  .then((response) => response.json())
  .then((data) => {
    console.log(data);
    L.geoJSON(data, {
      // Tùy chỉnh hiển thị cho từng loại dữ liệu
      style: function (feature) {
        if (feature.properties.type === "route") {
          return { color: "red", weight: 5, opacity: 0.7 };
        }
      },
      // Tạo marker và popup cho các điểm (Point)
      onEachFeature: function (feature, layer) {
        if (feature.properties && feature.properties.name) {
          layer.bindPopup(
            `<b>${feature.properties.name}</b><br>Loại: ${feature.properties.type}`,
          );
        }
      },
    }).addTo(map);

    const geojsonLayer = L.geoJSON(data).addTo(map);
    map.fitBounds(geojsonLayer.getBounds());
  });
