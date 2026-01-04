navigator.geolocation.getCurrentPosition(pos => {
    fetch("/send_sos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: pos.coords.latitude,
            lng: pos.coords.longitude
        })
    }).then(() => alert("SOS Sent!"));
});

function sendSOS() {
    if (!navigator.geolocation) {
        alert("GPS not supported");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        pos => {
            fetch("/sos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    lat: pos.coords.latitude,
                    lng: pos.coords.longitude
                })
            }).then(() => alert("SOS Sent"));
        },
        () => {
            localStorage.setItem("pendingSOS", "true");
            alert("No signal. SOS saved.");
        }
    );
}

window.addEventListener("online", () => {
    if (localStorage.getItem("pendingSOS")) {
        sendSOS();
        localStorage.removeItem("pendingSOS");
    }
});

