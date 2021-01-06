  // Called when the Spotify Web Playback SDK is ready to use
  window.onSpotifyWebPlaybackSDKReady = () => {

    // Define the Spotify Connect device, getOAuthToken has an actual token 
    // hardcoded for the sake of simplicity

    var player = new Spotify.Player({
      name: 'Splatify',
      getOAuthToken: callback => {
        callback(auth_token);
      },
      volume: 0.1
    });

    // Called when connected to the player created beforehand successfully
    player.addListener('ready', ({ device_id }) => {
      console.log('Ready with Device ID', device_id);

      const play = ({
        spotify_uri,
        playerInstance: {
          _options: {
            getOAuthToken,
            id
          }
        }
      }) => {
        getOAuthToken(access_token => {
          fetch(`https://api.spotify.com/v1/me/player/play?device_id=${id}`, {
            method: 'PUT',
            body: JSON.stringify({ context_uri: spotify_uri }),
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${access_token}`
            },
          });
        });
      };

      play({
        playerInstance: player,
        spotify_uri: 'spotify:playlist:3px8ZRPx2vsBJ506bEn083',
      });
    });

    // Connect to the player created beforehand, this is equivalent to 
    // creating a new device which will be visible for Spotify Connect
    player.connect();
  };
