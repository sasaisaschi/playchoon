document.addEventListener('DOMContentLoaded', (event) => {
  document.getElementById('push-button').addEventListener('click', function () {
    console.log('Button was clicked');
    var artistNames = document.getElementById('Artists-Input').value.split(',');
    var totalSongs = document.getElementById('field-2').value;

    fetch('/generate_playlist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ artist_names: artistNames, total_songs: totalSongs }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.auth_url) {
        // Der Benutzer ist nicht authentifiziert, leiten Sie ihn zur Spotify-Authentifizierungs-URL um
        window.location.href = data.auth_url;
      } else {
        console.log(data);
        // Hier können Sie Benutzerfeedback geben
      }
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  });
});
