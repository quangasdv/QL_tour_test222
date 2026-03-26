const map = L.map("map").setView([10.76, 106.66], 10);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

const pathSegments = window.location.pathname.split("/");
// Robustly extract the last numeric segment as tourId (handles trailing slash).
const numericSegments = pathSegments.filter((s) => /^\d+$/.test(s));
const tourId = numericSegments.length ? numericSegments[numericSegments.length - 1] : null;

if (!tourId) {
  console.error("Could not detect tourId from URL:", window.location.pathname);
}

fetch(`../route-map/${tourId}`)
  .then((res) => res.json())
  .then((data) => {
    console.log(data);
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
            Order: ${feature.properties.order}<br>
            Description: ${feature.properties.description}
          `);
        }

        if (feature.geometry.type === "LineString") {
          const distanceKm = feature.properties.distance_km ?? 0;
          layer.bindPopup(`
            <b>${feature.properties.name}</b><br>
            Distance: ${Number(distanceKm).toFixed(2)} km
          `);
        }
      },
    }).addTo(map);

    const bounds = geojsonLayer.getBounds();
    if (bounds && bounds.isValid && bounds.isValid()) {
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  });
