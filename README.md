# asot-py
A script to update a user's playlist with the latest Armin van Buuren ASOT Radio episode.
## Example usage
### Obtain all required env variables
[Create a Spotify app](https://developer.spotify.com/dashboard/applications) if you don't have one yet.
- CLIENT_ID: [Spotify Dashboard](https://developer.spotify.com/dashboard/)
- CLIENT_SECRET: [Spotify Dashboard](https://developer.spotify.com/dashboard/)
- REFRESH_TOKEN: [Spotify Refresh Token Generator](https://spotify-refresh-token-generator.netlify.app/#welcome)
- PLAYLIST_ID: Copy the playlist's share link in Spotify and extract the ID after `/playlist/` and before `?`
- USER_ID: From your user profile, copy the share link and extract the ID after `/user/` and before `?`
### Modify env.list
The example env file contains the required variables and will be used when launching our docker container. Replace the placeholders with the values obtained above for later use.
### Build Docker image
```
docker build -t asot-py .
```
### Run Docker Container
```
docker run -d --env-file env.list --name asot-py asot-py
```
Using the `--env-file` flag allows us to pass our environment variables to the container without storing outside our local machine. Additionally, we are using the `-d` to run the container in the background.
### Check Docker logs to confirm the script is working
```
docker logs -f asot-py
```
Note: the included `mycron` file's schedule is set to hourly on Thursdays (`1 * * * 4`) so it is only attempting to update the playlist on the day new ASOT episodes are released. If you would like to confirm the script works without waiting, adjust the cron schedule to run every minute (`* * * * *`).