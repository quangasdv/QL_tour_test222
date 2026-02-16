const map = L.map("map").setView([10.76, 106.66], 10);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

const pathSegments = window.location.pathname.split("/");
const tourId = pathSegments[pathSegments.length - 1];

fetch(`../route-map/${tourId}`)
  .then((res) => res.json())
  .then((data) => {
    const geojsonLayer = L.geoJSON(data, {
      // Style cho LineString
      style: function (feature) {
        if (feature.properties.type === "route") {
          return {
            color: "red",
            weight: 5,
            opacity: 0.7,
          };
        }
      },

      // BẮT BUỘC cho Point
      pointToLayer: function (feature, latlng) {
        return L.marker(latlng);
      },

      // Popup
      onEachFeature: function (feature, layer) {
        if (feature.geometry.type === "Point") {
          layer.bindPopup(`
            <b>${feature.properties.name}</b><br>
            Order: ${feature.properties.order}
          `);
        }

        if (feature.geometry.type === "LineString") {
          layer.bindPopup(`
            <b>${feature.properties.name}</b><br>
            Distance: ${feature.properties.distance_km.toFixed(2)} km
          `);
        }
      },
    }).addTo(map);

    map.fitBounds(geojsonLayer.getBounds());
  });
