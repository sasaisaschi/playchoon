document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('push-button');
  const form = document.getElementById('playlist-form');
  const successEl = document.querySelector('.success-message');
  const errorEl = document.querySelector('.error-message');
  const errorMsg = document.querySelector('.error-message p');
  const successMsg = document.querySelector('.success-message p');

  btn.addEventListener('click', () => {
    const artistInput = document.getElementById('Artists-Input').value.trim();
    const totalSongs = document.getElementById('field-2').value;

    if (!artistInput) {
      showError('Bitte mindestens einen Künstler eingeben.');
      return;
    }

    const artistNames = artistInput.split(',').map(a => a.trim()).filter(Boolean);

    setLoading(true);
    hideMessages();

    fetch('/generate_playlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artist_names: artistNames, total_songs: totalSongs }),
    })
      .then(response => response.json())
      .then(data => {
        setLoading(false);
        if (data.auth_url) {
          window.location.href = data.auth_url;
        } else if (data.status === 'success') {
          form.style.display = 'none';
          successEl.style.display = 'block';
          successMsg.innerHTML =
            'Thanks for using PLAYCHOON. <br><a href="https://open.spotify.com/playlist/' +
            data.playlist_id +
            '" target="_blank" class="playlist-link">Open your playlist in Spotify</a>';
        } else {
          showError(data.message || 'Oops! Something went wrong. Please try again.');
        }
      })
      .catch(() => {
        setLoading(false);
        showError('Keine Verbindung zum Server. Bitte später erneut versuchen.');
      });
  });

  function setLoading(active) {
    btn.disabled = active;
    btn.value = active ? 'Loading...' : 'Push Button';
    btn.style.opacity = active ? '0.6' : '1';
  }

  function showError(message) {
    errorMsg.textContent = message;
    errorEl.style.display = 'block';
  }

  function hideMessages() {
    successEl.style.display = 'none';
    errorEl.style.display = 'none';
  }
});
