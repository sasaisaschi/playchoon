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
      } else if (data.status === 'success') {
        console.log(data);
        // Show success message
        document.querySelector('.success-message').style.display = 'block';
        // Hide the form
        document.getElementById('playlist-form').style.display = 'none';
        // Add playlist link to success message
        const successMessage = document.querySelector('.success-message p');
        successMessage.innerHTML = 'Thanks for using PLAYCHOON. <br><a href="https://open.spotify.com/playlist/' + 
          data.playlist_id + '" target="_blank" class="playlist-link">Open your playlist in Spotify</a>';
      } else {
        console.error('Error:', data.message);
        // Show error message
        document.querySelector('.error-message').style.display = 'block';
        document.querySelector('.error-message p').textContent = data.message || 'Oops! Something went wrong while submitting the form. :(';
      }
    })
    .catch((error) => {
      console.error('Error:', error);
      // Show error message
      document.querySelector('.error-message').style.display = 'block';
      document.querySelector('.error-message p').textContent = 'Oops! Something went wrong while submitting the form. Please try again later.';
    });
  });
});
